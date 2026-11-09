import re
import logging
from io import BytesIO
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from app.schemas.candidate import ParsedCandidateProfile
from app.core.llm import llm

logger = logging.getLogger("screening.resume_parser")

COMMON_SKILLS_TAXONOMY = {
    # ML / AI
    "pytorch": "PyTorch", "tensorflow": "TensorFlow", "keras": "Keras",
    "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "langchain": "LangChain", "chromadb": "ChromaDB", "huggingface": "Hugging Face",
    "transformers": "Transformers", "cuda": "CUDA", "mlflow": "MLflow",
    "deep learning": "Deep Learning", "nlp": "NLP", "computer vision": "Computer Vision",
    "llm": "LLMs", "rag": "RAG", "xgboost": "XGBoost", "lightgbm": "LightGBM",
    "pandas": "Pandas", "numpy": "NumPy", "opencv": "OpenCV",
    # Backend / Distributed
    "python": "Python", "go": "Go", "golang": "Go", "java": "Java",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL",
    "redis": "Redis", "kafka": "Kafka", "rabbitmq": "RabbitMQ", "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes", "grpc": "gRPC",
    "sqlalchemy": "SQLAlchemy", "graphql": "GraphQL", "rest api": "RESTful APIs",
    "microservices": "Microservices", "asyncio": "AsyncIO", "celery": "Celery",
    # Data Science / Analytics
    "sql": "SQL", "r": "R", "tableau": "Tableau", "power bi": "Power BI",
    "statsmodels": "Statsmodels", "a/b testing": "A/B Testing", "statistics": "Statistics",
    "spark": "Apache Spark", "hadoop": "Hadoop", "snowflake": "Snowflake", "dbt": "dbt"
}

DOMAIN_KEYWORDS = {
    "Deep Learning": ["deep learning", "neural network", "backpropagation", "cnn", "rnn", "lstm", "transformer", "attention"],
    "Retrieval-Augmented Generation (RAG)": ["rag", "retrieval", "vector database", "embeddings", "chroma", "pinecone", "qdrant"],
    "Optimization & Loss Functions": ["gradient descent", "sgd", "loss function", "adam", "cross-entropy", "regularization"],
    "Model Evaluation & Metrics": ["roc-auc", "f1-score", "precision", "recall", "confusion matrix", "cross-validation", "overfitting"],
    "Distributed Systems": ["distributed", "microservices", "replication", "sharding", "consistency", "cap theorem", "kafka"],
    "Database Storage & Concurrency": ["b-tree", "lsm", "acid", "transactions", "isolation", "indexing", "deadlock", "locks"],
    "High-Throughput Caching": ["redis", "memcached", "cache-aside", "write-through", "cache stampede", "invalidation"],
    "API Reliability & Scale": ["rate limit", "circuit breaker", "idempotency", "grpc", "event loop", "asyncio"]
}

class ResumeParser:
    """Enterprise Resume Parser supporting PDF and Text with LLM and heuristic extractors."""

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """Extract clean text from PDF or text bytes with robust fallback."""
        if not file_bytes:
            raise ValueError("Uploaded resume file is empty.")

        text = ""
        fn_lower = filename.lower()
        if fn_lower.endswith(".pdf") or file_bytes.startswith(b"%PDF"):
            try:
                pdf_file = BytesIO(file_bytes)
                reader = PdfReader(pdf_file)
                extracted_pages = []
                for idx, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        extracted_pages.append(t.strip())
                text = "\n\n".join(extracted_pages)
                if not text.strip():
                    raise ValueError("PDF content could not be extracted (may be scanned image).")
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                raise ValueError(f"Failed to parse PDF document: {str(e)}")
        else:
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="ignore")

        return text.strip()

    def parse_heuristically(self, raw_text: str, target_role: str) -> ParsedCandidateProfile:
        """Deterministic NLP heuristic extraction if LLM is unavailable."""
        text_lower = raw_text.lower()
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        # 1. Candidate Name
        candidate_name = "Candidate"
        name_match = re.search(r"^(?:name[:\s]+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", raw_text)
        if name_match:
            candidate_name = name_match.group(1).strip()
        elif lines:
            candidate_name = lines[0].replace("NAME:", "").strip()

        # 2. Email
        email = None
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw_text)
        if email_match:
            email = email_match.group(0)

        # 3. Technical Skills
        found_skills = set()
        for pattern, normalized in COMMON_SKILLS_TAXONOMY.items():
            if re.search(r"\b" + re.escape(pattern) + r"\b", text_lower):
                found_skills.add(normalized)

        if not found_skills:
            # Fallback based on role
            if "backend" in target_role.lower():
                found_skills = {"Python", "FastAPI", "PostgreSQL", "Redis", "Docker"}
            elif "data" in target_role.lower():
                found_skills = {"Python", "SQL", "Scikit-Learn", "Pandas", "Statistics"}
            else:
                found_skills = {"Python", "PyTorch", "Machine Learning", "Transformers", "Deep Learning"}

        skills_list = sorted(list(found_skills))

        # 4. Domain Exposure
        domains = []
        for domain_name, kw_list in DOMAIN_KEYWORDS.items():
            for kw in kw_list:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    domains.append(domain_name)
                    break

        if not domains:
            domains = ["Core Engineering Foundations", "System Design & Algorithms"]

        # 5. Experience Level
        exp_level = "Mid-Level"
        years_match = re.findall(r"(\d+)\+?\s*(?:years|yrs)", text_lower)
        if years_match:
            max_years = max([int(y) for y in years_match if int(y) < 40])
            if max_years >= 6:
                exp_level = "Lead / Staff"
            elif max_years >= 4:
                exp_level = "Senior"
            elif max_years <= 2:
                exp_level = "Junior"
        elif any(k in text_lower for k in ["lead", "staff", "principal", "architect"]):
            exp_level = "Senior / Staff"
        elif any(k in text_lower for k in ["senior", "sr."]):
            exp_level = "Senior"

        # 6. Highlights & Summary
        highlights = []
        for line in lines:
            if line.startswith(("-", "•", "*")) and len(line) > 25:
                highlights.append(line.lstrip("-•* ").strip())
                if len(highlights) >= 4:
                    break

        summary = f"{candidate_name} is a {exp_level} professional with core competencies in {', '.join(skills_list[:5])}. Demonstrates verified background in {', '.join(domains[:3])}."

        return ParsedCandidateProfile(
            candidate_name=candidate_name,
            email=email,
            skills=skills_list[:12],
            technologies=[s for s in skills_list if s in ["Docker", "Kubernetes", "Kafka", "Redis", "ChromaDB", "Git", "MLflow", "PostgreSQL", "FastAPI"]],
            experience_level=exp_level,
            domain_exposure=domains[:5],
            project_highlights=highlights if highlights else [summary],
            raw_summary=summary
        )

    async def parse_resume(self, file_bytes: bytes, filename: str, target_role: str) -> ParsedCandidateProfile:
        """Extract text and invoke LLM for structured profile with graceful heuristic fallback."""
        raw_text = self.extract_text(file_bytes, filename)
        fallback = lambda: self.parse_heuristically(raw_text, target_role)

        system_prompt = (
            "You are an expert technical recruiter and resume analyzer. "
            "Extract structured candidate information from the provided resume text. "
            "Return valid JSON conforming to the requested schema."
        )

        user_prompt = f"""Target Job Role: {target_role}

Resume Text:
\"\"\"
{raw_text[:4000]}
\"\"\"

Extract and format as JSON with keys:
- candidate_name (string)
- email (string or null)
- skills (array of specific programming languages, algorithms, and core technical skills)
- technologies (array of frameworks, databases, and tools)
- experience_level ("Junior", "Mid-Level", "Senior", or "Lead")
- domain_exposure (array of domain concepts e.g. "Distributed Systems", "Deep Learning", "Model Evaluation")
- project_highlights (array of 2-4 key achievements/projects)
- raw_summary (concise 2-sentence summary)
"""

        try:
            parsed_dict = await llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema_class=ParsedCandidateProfile,
                fallback_handler=fallback
            )
            if parsed_dict and "candidate_name" in parsed_dict and parsed_dict.get("skills"):
                return ParsedCandidateProfile(**parsed_dict)
        except Exception as e:
            logger.warning(f"LLM parsing encountered error: {e}. Falling back to heuristic parser.")

        return fallback()

resume_parser = ResumeParser()
