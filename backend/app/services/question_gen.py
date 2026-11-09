import logging
import random
from typing import List, Dict, Any, Optional
from app.services.rag_engine import rag_engine
from app.core.llm import llm

logger = logging.getLogger("screening.question_gen")

ROLE_TOPIC_PROGRESSION = {
    "AI/ML Engineer": [
        {
            "stage": "Empirical Risk & Mathematical Foundations",
            "skills": ["Supervised Learning", "Loss Functions", "Linear Models", "Empirical Risk Minimization"],
            "query": "empirical risk minimization loss functions negative log likelihood cross-entropy"
        },
        {
            "stage": "Optimization & Gradient Dynamics",
            "skills": ["Optimization", "Gradient Descent", "SGD", "Adam", "Learning Rate"],
            "query": "stochastic gradient descent mini-batch momentum Adam optimizer learning rates"
        },
        {
            "stage": "Regularization & Generalization Bounds",
            "skills": ["Regularization", "L1 vs L2", "Overfitting", "Bias-Variance Tradeoff"],
            "query": "L1 L2 regularization ridge lasso sparsity bias-variance tradeoff"
        },
        {
            "stage": "Deep Architectures & Representation Learning",
            "skills": ["Deep Learning", "Transformers", "Backpropagation", "BatchNorm", "Dropout"],
            "query": "deep neural networks backpropagation activation functions batch norm dropout"
        },
        {
            "stage": "Model Evaluation, Class Skew & Production Diagnostics",
            "skills": ["Model Evaluation", "ROC-AUC", "Precision-Recall", "Class Imbalance", "SMOTE"],
            "query": "ROC-AUC PR-AUC precision recall class imbalance focal loss SMOTE"
        }
    ],
    "Data Scientist": [
        {
            "stage": "Hypothesis Formulation & Statistical Inference",
            "skills": ["Statistical Analysis", "A/B Testing", "Hypothesis Testing", "Linear Regression"],
            "query": "statistical inference ordinary least squares linear regression hypothesis testing"
        },
        {
            "stage": "Feature Engineering & High-Dimensional Selection",
            "skills": ["Feature Selection", "L1 Regularization", "Lasso", "Dimensionality Reduction"],
            "query": "feature selection L1 lasso sparsity high dimensional curse of dimensionality"
        },
        {
            "stage": "Tree Ensembles & Bias-Variance Decomposition",
            "skills": ["Decision Trees", "Random Forests", "XGBoost", "Bias-Variance"],
            "query": "decision trees gini entropy random forest boosting bias variance tradeoff"
        },
        {
            "stage": "Imbalanced Data & Real-World Calibration",
            "skills": ["Class Imbalance", "Probability Calibration", "SMOTE", "Logistic Regression"],
            "query": "class imbalance logistic regression sigmoid calibration focal loss SMOTE"
        },
        {
            "stage": "Evaluation Metrics & Experimentation Rigor",
            "skills": ["ROC-AUC", "PR-AUC", "Cross-Validation", "Metrics Tradeoffs"],
            "query": "ROC-AUC precision recall PR curves k-fold cross-validation metrics"
        }
    ],
    "Backend Engineer": [
        {
            "stage": "Concurrency & Asynchronous Execution Models",
            "skills": ["Concurrency", "AsyncIO", "Event Loop", "Threading", "Locks"],
            "query": "concurrency asynchronous IO event loop threading race conditions locks"
        },
        {
            "stage": "Storage Engines, Indexing & Query Optimization",
            "skills": ["PostgreSQL", "B+ Trees", "LSM Trees", "Query Optimization", "Indexing"],
            "query": "database storage B-Trees LSM-Trees indexing write amplification"
        },
        {
            "stage": "Transactions, ACID Guarantees & Isolation Levels",
            "skills": ["ACID", "Transactions", "Isolation Levels", "MVCC", "Deadlocks"],
            "query": "ACID transaction isolation levels repeatable read serializable MVCC deadlocks"
        },
        {
            "stage": "Distributed Caching & High-Throughput Resilience",
            "skills": ["Redis", "Caching Strategies", "Cache Stampede", "Invalidation"],
            "query": "distributed caching cache-aside write-through cache stampede invalidation"
        },
        {
            "stage": "Distributed Consistency & High-Availability Patterns",
            "skills": ["Distributed Systems", "CAP Theorem", "Circuit Breakers", "Idempotency"],
            "query": "CAP theorem linearizable consistency circuit breaker rate limiting idempotency keys"
        }
    ]
}

class QuestionGenerator:
    """Generates technically rigorous, candidate-grounded interview questions citing textbook concepts."""

    async def generate_turn_question(
        self,
        candidate_name: str,
        target_role: str,
        parsed_skills: List[str],
        project_highlights: List[str],
        experience_level: str,
        turn_index: int,
        previous_turns: List[Any] = None
    ) -> Dict[str, Any]:
        """Generate a technical question grounded in retrieved textbook chunks and candidate profile."""
        role_key = "AI/ML Engineer"
        if "backend" in target_role.lower() or "systems" in target_role.lower():
            role_key = "Backend Engineer"
        elif "data" in target_role.lower():
            role_key = "Data Scientist"

        progression = ROLE_TOPIC_PROGRESSION.get(role_key, ROLE_TOPIC_PROGRESSION["AI/ML Engineer"])
        stage_idx = min(max(turn_index - 1, 0), len(progression) - 1)
        curr_stage = progression[stage_idx]

        # Match relevant skill from candidate resume or fallback to stage skill
        targeted_skill = curr_stage["skills"][0]
        for skill in parsed_skills:
            for s in curr_stage["skills"]:
                if s.lower() in skill.lower() or skill.lower() in s.lower():
                    targeted_skill = skill
                    break

        # Anchor with a candidate project highlight if available
        project_ref = ""
        if project_highlights and len(project_highlights) > 0:
            pick_idx = (turn_index - 1) % len(project_highlights)
            project_ref = project_highlights[pick_idx]

        # RAG retrieval
        rag_query = f"{curr_stage['query']} {targeted_skill}"
        chunks = rag_engine.retrieve_context(rag_query, role=target_role, k=3)
        if not chunks:
            # Fallback broader query
            chunks = rag_engine.retrieve_context(curr_stage["query"], role=target_role, k=3)

        top_chunk = chunks[0] if chunks else {
            "book": "Foundational Machine Learning & Systems Handbook",
            "chapter": curr_stage["stage"],
            "text": "Core theoretical foundations governing performance, trade-offs, and scaling."
        }

        cited_concept = f"{top_chunk.get('book', 'Textbook')}, {top_chunk.get('chapter', curr_stage['stage'])}"
        source_topic = curr_stage["stage"]

        # Synthesize question via LLM or intelligent deterministic engine
        system_prompt = (
            "You are a Staff Technical Interviewer conducting a rigorous, role-specific screening interview. "
            "Generate a deep technical question that directly bridges the candidate's resume experience "
            "with the provided theoretical textbook context. Do not use generic boilerplate templates. "
            "Ask for architectural justification, mathematical/algorithmic mechanics, or concrete failure-mode analysis."
        )

        user_prompt = f"""
Candidate: {candidate_name} ({experience_level})
Target Role: {target_role}
Turn Number: {turn_index} of 5
Targeted Skill: {targeted_skill}
Candidate Project Anchor: {project_ref}
Retrieved Ground-Truth Textbook Context:
\"\"\"
{top_chunk.get('text', '')[:1200]}
\"\"\"

Formulate an in-depth interview question (2-4 sentences). 
Include a scenario referencing the candidate's background with {targeted_skill}, 
connect it directly to the cited textbook concept ({cited_concept}), 
and ask for their architectural reasoning, algorithmic trade-off, or mitigation strategy.
Return JSON with key 'question_text'.
"""

        fallback_handler = lambda: self._synthesize_fallback_question(
            candidate_name, target_role, targeted_skill, project_ref, top_chunk, cited_concept, turn_index
        )

        try:
            result = await llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema_class=None,
                fallback_handler=fallback_handler
            )
            q_text = result.get("question_text") if result else None
            if q_text and len(q_text) > 30:
                return {
                    "targeted_skill": targeted_skill,
                    "source_topic": source_topic,
                    "cited_concept": cited_concept,
                    "question_text": q_text,
                    "retrieved_chunks": chunks
                }
        except Exception as e:
            logger.warning(f"LLM question generation failed: {e}. Using deterministic synthesis.")

        return fallback_handler()

    def _synthesize_fallback_question(
        self,
        candidate_name: str,
        target_role: str,
        targeted_skill: str,
        project_ref: str,
        top_chunk: Dict[str, Any],
        cited_concept: str,
        turn_index: int
    ) -> Dict[str, Any]:
        """Deterministic scenario question synthesis linking resume context with textbook chunk."""
        chunk_text = top_chunk.get("text", "")
        book = top_chunk.get("book", "Textbook")
        chapter = top_chunk.get("chapter", "Core Foundations")

        # Extract primary technical term from chunk text
        lead_sentence = chunk_text.split(".")[0] if "." in chunk_text else chunk_text[:120]

        templates = [
            f"In your background with {targeted_skill}, you have encountered complex production trade-offs. Grounded in {cited_concept}—specifically where {lead_sentence.strip()}—how would you mathematically or architecturally justify your parameter selection and handle potential degradation or failure modes in a high-scale deployment?",
            f"Based on your hands-on exposure to {targeted_skill}, consider a production scenario where an algorithm begins exhibiting high validation error. Referencing the principles established in {cited_concept}, walk through how you diagnose whether the issue stems from high bias versus high variance, and explain the concrete regularization or architectural modifications you would enact.",
            f"Your profile highlights work in {targeted_skill}. As detailed in {cited_concept}, system guarantees rely on specific invariants. When designing for low latency and high availability under anomalous conditions, what specific synchronization, caching, or optimization trade-offs do you apply to preserve consistency and avoid bottlenecks?",
            f"Given your experience utilizing {targeted_skill}, how do you evaluate alternative approaches when facing skewed data distributions or distributed concurrency limits? Citing the core methodology from {cited_concept}, explain step-by-step how you measure performance and prevent hidden failure states.",
            f"Drawing upon your engineering experience with {targeted_skill}, suppose a mission-critical pipeline begins breaching latency budgets. Grounded in {cited_concept}, explain your diagnostic hierarchy, detailing how you isolate resource contention or mathematical convergence bottlenecks."
        ]

        question_text = templates[(turn_index - 1) % len(templates)]
        if project_ref and len(project_ref) > 15:
            question_text = f"Regarding your experience ('{project_ref[:110]}...'): " + question_text

        return {
            "targeted_skill": targeted_skill,
            "source_topic": chapter,
            "cited_concept": cited_concept,
            "question_text": question_text,
            "retrieved_chunks": [top_chunk]
        }

question_gen = QuestionGenerator()
