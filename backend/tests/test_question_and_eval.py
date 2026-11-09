import pytest
from app.services.question_gen import question_gen
from app.services.evaluator import evaluator

@pytest.mark.asyncio
async def test_question_generation_grounding():
    result = await question_gen.generate_turn_question(
        candidate_name="Sarah Chen",
        target_role="AI/ML Engineer",
        parsed_skills=["PyTorch", "Transformers", "RAG"],
        project_highlights=["Built enterprise RAG pipeline serving 2M queries with sub-120ms latency"],
        experience_level="Senior",
        turn_index=1
    )

    assert "targeted_skill" in result
    assert "source_topic" in result
    assert "cited_concept" in result
    assert "question_text" in result
    assert len(result["question_text"]) > 25
    assert len(result["retrieved_chunks"]) > 0

@pytest.mark.asyncio
async def test_answer_evaluator_high_score():
    chunks = [{
        "text": "L1 regularization induces sparsity by setting non-essential weights to zero. L2 regularization (weight decay) penalizes large weights proportionally, pulling them smoothly toward zero.",
        "book": "The Hundred-Page Machine Learning Book",
        "chapter": "Chapter 4: Regularization"
    }]

    eval_result = await evaluator.evaluate_answer(
        question_text="Explain the mathematical difference and practical sparsity implications between L1 and L2 regularization.",
        targeted_skill="Regularization",
        cited_concept="The Hundred-Page Machine Learning Book, Chapter 4",
        retrieved_chunks=chunks,
        candidate_answer="L1 regularization adds the absolute sum of weights |w| to the loss function, whose diamond contour has sharp corners that drive coefficients strictly to zero, effectively performing feature selection. In contrast, L2 regularization adds the squared Euclidean norm (1/2 ||w||^2), smoothly shrinking parameters toward zero to prevent extreme weights without forcing sparsity.",
        experience_level="Senior"
    )

    assert eval_result["score"] >= 7.0
    assert eval_result["technical_accuracy"] in ["High", "Moderate"]
    assert len(eval_result["strengths"]) > 0
    assert "constructive_feedback" in eval_result

@pytest.mark.asyncio
async def test_answer_evaluator_brief_insufficient():
    eval_result = await evaluator.evaluate_answer(
        question_text="Discuss ACID isolation levels and phantom reads.",
        targeted_skill="ACID",
        cited_concept="Backend Systems Handbook, Module 2",
        retrieved_chunks=[],
        candidate_answer="I don't know.",
        experience_level="Senior"
    )

    assert eval_result["score"] <= 3.5
    assert eval_result["technical_accuracy"] == "Insufficient"
