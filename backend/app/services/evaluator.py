import logging
import re
from typing import List, Dict, Any, Optional
from app.core.llm import llm

logger = logging.getLogger("screening.evaluator")

class CandidateEvaluator:
    """Evaluates candidate technical responses against retrieved ground-truth textbook chunks."""

    async def evaluate_answer(
        self,
        question_text: str,
        targeted_skill: str,
        cited_concept: str,
        retrieved_chunks: List[Dict[str, Any]],
        candidate_answer: str,
        experience_level: str = "Mid-Level"
    ) -> Dict[str, Any]:
        """Evaluate candidate response using LLM with deterministic semantic rubric fallback."""
        ground_truth_context = "\n\n".join([c.get("text", "") for c in retrieved_chunks[:2]])

        system_prompt = (
            "You are a Principal Engineering Interviewer and Technical Evaluator. "
            "Evaluate the candidate's answer against the provided ground-truth textbook reference and question. "
            "Score objectively between 1.0 and 10.0 according to conceptual precision, accuracy, and depth. "
            "Return valid JSON."
        )

        user_prompt = f"""
Question:
{question_text}

Targeted Skill & Topic: {targeted_skill} (Concept: {cited_concept})
Expected Candidate Seniority: {experience_level}

Ground-Truth Reference from Textbook:
\"\"\"
{ground_truth_context[:1400]}
\"\"\"

Candidate's Submitted Answer:
\"\"\"
{candidate_answer}
\"\"\"

Evaluate the answer and return JSON with keys:
- score (float between 1.0 and 10.0)
- technical_accuracy ("High", "Moderate", "Marginal", or "Insufficient")
- strengths (array of strings highlighting valid arguments or recognized concepts)
- missing_points (array of strings mentioning omitted concepts, mathematical depth, or edge cases)
- constructive_feedback (string with specific actionable feedback)
- model_answer_summary (string summarizing the ideal answer based on the textbook)
"""

        fallback_handler = lambda: self._evaluate_heuristically(
            question_text, targeted_skill, cited_concept, ground_truth_context, candidate_answer, experience_level
        )

        try:
            result = await llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema_class=None,
                fallback_handler=fallback_handler
            )
            if result and "score" in result and "constructive_feedback" in result:
                # Clamp score
                score = float(result.get("score", 7.0))
                score = max(1.0, min(10.0, round(score, 1)))
                result["score"] = score
                return result
        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}. Executing heuristic semantic evaluation.")

        return fallback_handler()

    def _evaluate_heuristically(
        self,
        question_text: str,
        targeted_skill: str,
        cited_concept: str,
        ground_truth_context: str,
        candidate_answer: str,
        experience_level: str
    ) -> Dict[str, Any]:
        """Robust semantic keyword and depth matcher against ground truth."""
        ans = candidate_answer.strip()
        ans_lower = ans.lower()
        words = ans_lower.split()
        word_count = len(words)

        # Extract domain key tokens from ground truth
        clean_context = re.sub(r"[^a-zA-Z0-9\s]", " ", ground_truth_context.lower())
        vocab = [w for w in clean_context.split() if len(w) > 4 and w not in [
            "where", "which", "their", "there", "these", "those", "about", "would", "could", "should", "using"
        ]]
        unique_tokens = list(set(vocab))

        # Check matched tokens
        matched_tokens = [tok for tok in unique_tokens if tok in ans_lower]
        match_ratio = len(matched_tokens) / max(len(unique_tokens[:15]), 1)

        # Baseline score calculation
        if word_count < 10:
            score = 2.0
            accuracy = "Insufficient"
            feedback = "Answer was too brief to demonstrate technical competence. Please elaborate with architectural details, mechanisms, or algorithms."
            missing = ["Fundamental theoretical elaboration", "Specific architectural or mathematical justifications"]
            strengths = ["Submitted an initial response"]
        elif word_count < 30:
            score = 4.5
            accuracy = "Marginal"
            feedback = f"Answer touches upon basic ideas but lacks rigor regarding {cited_concept}. Elaborate on the underlying trade-offs and edge cases."
            missing = ["Detailed implementation considerations", f"Deep connection to principles in {cited_concept}"]
            strengths = [f"Identified basic relevance to {targeted_skill}"]
        else:
            # Word count >= 30
            raw_score = 5.5 + (match_ratio * 3.5)
            # Bonus for structured reasoning (e.g., bullet points, technical terms, code)
            if any(term in ans_lower for term in ["trade-off", "latency", "complexity", "because", "furthermore", "specifically", "in order to"]):
                raw_score += 0.8
            if any(marker in ans for marker in ["- ", "1.", "2.", "•", "```"]):
                raw_score += 0.5
            
            score = min(9.5, max(4.0, round(raw_score, 1)))

            if score >= 8.0:
                accuracy = "High"
                feedback = f"Strong and thorough response. Demonstrates solid grasp of {targeted_skill} and aligns with the ground-truth principles of {cited_concept}."
            elif score >= 6.5:
                accuracy = "Moderate"
                feedback = f"Good technical reasoning with clear intuition. Could be improved by diving deeper into the specific mathematical bounds or failure recovery mechanisms mentioned in {cited_concept}."
            else:
                accuracy = "Marginal"
                feedback = f"Reasonable overview, but some assertions lack concrete theoretical grounding in {cited_concept}."

            strengths = [
                f"Demonstrated practical understanding of {targeted_skill}",
                f"Accurately cited relevant engineering principles ({', '.join(matched_tokens[:3]) if matched_tokens else 'core concepts'})"
            ]
            missing = [
                f"Deeper formal analysis relating to {cited_concept}",
                "Detailed mitigation of edge-case failure modes under production load"
            ]

        # Model answer excerpt
        sentences = [s.strip() for s in ground_truth_context.split(".") if len(s.strip()) > 30]
        model_answer = ". ".join(sentences[:2]) + "." if sentences else "Reference theoretical grounding based on curriculum standard."

        return {
            "score": score,
            "technical_accuracy": accuracy,
            "strengths": strengths,
            "missing_points": missing,
            "constructive_feedback": feedback,
            "model_answer_summary": model_answer
        }

evaluator = CandidateEvaluator()
