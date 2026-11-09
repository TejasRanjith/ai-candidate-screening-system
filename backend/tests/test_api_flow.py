import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

init_db()

@pytest.mark.asyncio
async def test_full_screening_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        health_resp = await client.get("/api/health")
        assert health_resp.status_code == 200
        data = health_resp.json()
        assert data["status"] == "healthy"
        assert data["indexed_chunks_count"] > 0

        # 2. Get roles & samples
        roles_resp = await client.get("/api/roles")
        assert roles_resp.status_code == 200
        assert len(roles_resp.json()["roles"]) == 3

        samples_resp = await client.get("/api/sample-resumes")
        assert samples_resp.status_code == 200
        samples = samples_resp.json()["samples"]
        assert len(samples) >= 3

        # 3. Start session with sample resume
        start_payload = {
            "role": "AI/ML Engineer",
            "sample_resume_id": "resume_ai_ml_engineer"
        }
        start_resp = await client.post("/api/sessions/start", data=start_payload)
        assert start_resp.status_code == 201
        session_data = start_resp.json()
        session_id = session_data["session_id"]
        assert session_data["candidate_name"] == "Sarah Chen"
        assert session_data["total_turns"] == 5
        assert session_data["current_turn_index"] == 0

        # 4. Turn 1: Fetch next question
        q1_resp = await client.get(f"/api/sessions/{session_id}/next-question")
        assert q1_resp.status_code == 200
        q1_data = q1_resp.json()
        assert q1_data["turn_index"] == 1
        assert len(q1_data["question_text"]) > 20
        assert q1_data["cited_concept"] != ""

        # 5. Turn 1: Submit Answer
        ans1_resp = await client.post(
            f"/api/sessions/{session_id}/submit-answer",
            json={"answer": "Empirical risk minimization approximates expected risk by calculating loss across available training samples. To avoid overfitting noisy samples, we introduce regularization penalties like L2 weight decay."}
        )
        assert ans1_resp.status_code == 200
        ans1_data = ans1_resp.json()
        assert ans1_data["turn_index"] == 1
        assert ans1_data["score"] > 0
        assert ans1_data["is_completed"] is False
        assert ans1_data["next_turn_index"] == 2

        # 6. Complete remaining turns 2 through 5
        for turn_idx in range(2, 6):
            q_resp = await client.get(f"/api/sessions/{session_id}/next-question")
            assert q_resp.status_code == 200
            ans_resp = await client.post(
                f"/api/sessions/{session_id}/submit-answer",
                json={"answer": f"For turn {turn_idx}, we address the trade-off by carefully tuning hyperparameters, verifying validation metrics, and deploying robust fault-tolerant monitoring."}
            )
            assert ans_resp.status_code == 200
            res = ans_resp.json()
            if turn_idx == 5:
                assert res["is_completed"] is True
                assert res["next_turn_index"] is None

        # 7. Final Report
        report_resp = await client.get(f"/api/sessions/{session_id}/report")
        assert report_resp.status_code == 200
        report = report_resp.json()
        assert report["session_id"] == session_id
        assert report["completed_turns"] == 5
        assert report["overall_score"] > 0
        assert len(report["turns"]) == 5
        assert len(report["strengths"]) > 0
        assert report["hiring_recommendation"] != ""

@pytest.mark.asyncio
async def test_session_not_found_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/sessions/non-existent-uuid/report")
        assert resp.status_code == 404
