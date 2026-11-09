import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLE_DIR = "/home/antigravity/backend/data/sample_resumes"
os.makedirs(SAMPLE_DIR, exist_ok=True)

RESUMES = {
    "resume_ai_ml_engineer": {
        "name": "Sarah Chen",
        "role": "AI/ML Engineer",
        "email": "sarah.chen@mleng.io",
        "summary": "AI/ML Engineer with 4+ years of experience training and deploying deep learning models, fine-tuning LLMs, and building low-latency RAG architectures in production.",
        "skills": ["Python", "PyTorch", "HuggingFace Transformers", "LangChain", "ChromaDB", "FastAPI", "Docker", "CUDA", "MLflow", "Scikit-Learn"],
        "domains": ["Deep Learning", "Retrieval-Augmented Generation", "NLP", "Optimization", "Model Quantization"],
        "experience": [
            "Senior Machine Learning Engineer @ NeuralScale (2022 - Present): Architected an enterprise RAG pipeline serving 2M daily queries with sub-120ms p95 latency. Optimized cross-encoder re-ranking and implemented semantic caching in Redis.",
            "ML Engineer @ DataVanguard (2020 - 2022): Fine-tuned Llama and BERT models for classification and summarization. Mitigated severe training class imbalance using focal loss and SMOTE, boosting minority class F1-score from 0.58 to 0.83.",
            "Applied AI Researcher @ TechLabs (2019 - 2020): Researched gradient descent optimization variants (AdamW, Lion) and regularized deep CNNs using DropPath, Mixup, and BatchNorm."
        ],
        "education": "M.S. in Computer Science (Machine Learning Concentration), University of Washington"
    },
    "resume_backend_engineer": {
        "name": "Marcus Vance",
        "role": "Senior Backend Engineer",
        "email": "marcus.vance@systems.dev",
        "summary": "Distributed systems and backend architect with 5+ years building scalable microservices, high-throughput APIs, and transactional database architectures.",
        "skills": ["Python", "FastAPI", "Go", "PostgreSQL", "Redis", "Kafka", "Docker", "Kubernetes", "SQLAlchemy", "gRPC"],
        "domains": ["Distributed Systems", "Database Indexing & Concurrency", "Event-Driven Systems", "Caching Strategies", "API Reliability"],
        "experience": [
            "Lead Backend Engineer @ CloudSync Systems (2021 - Present): Designed distributed ingestion platform handling 45,000 requests/sec using FastAPI, Kafka, and Redis. Solved cache stampede using probabilistic early expiration and distributed mutex locks.",
            "Backend Engineer @ FinTech Core (2019 - 2021): Optimized PostgreSQL relational schema and B+ Tree indexes, reducing 99th percentile query latency from 850ms to 18ms. Implemented strict serializable transactions for ledger consistency.",
            "Systems Developer @ DataStream Inc (2018 - 2019): Built asynchronous worker services utilizing non-blocking event loops and circuit breaker patterns to guarantee 99.99% service uptime."
        ],
        "education": "B.S. in Software Engineering, Purdue University"
    },
    "resume_data_scientist": {
        "name": "Elena Rostova",
        "role": "Data Scientist",
        "email": "elena.rostova@analytics.org",
        "summary": "Data Scientist with 3+ years applying statistical modeling, ensemble machine learning algorithms, and hypothesis testing to solve customer churn and pricing optimization.",
        "skills": ["Python", "R", "Scikit-Learn", "XGBoost", "Pandas", "NumPy", "SQL", "Statsmodels", "Tableau", "Git"],
        "domains": ["Supervised Learning", "Feature Engineering", "Hypothesis Testing", "Model Evaluation & ROC-AUC", "Regularization"],
        "experience": [
            "Data Scientist @ MarketMetrics (2022 - Present): Developed end-to-end churn prediction engine using XGBoost and Random Forests with 0.88 ROC-AUC. Performed extensive hyperparameter tuning using Bayesian Optimization.",
            "Junior Data Scientist @ RetailOptima (2020 - 2022): Engineered feature selection pipelines using L1 Lasso regularization to reduce dimensionality from 450 to 32 critical variables. Designed and evaluated A/B tests with strict statistical power analysis.",
            "Data Analyst @ StatCore (2019 - 2020): Analyzed customer lifetime value distributions, calibrated logistic regression probability outputs, and built automated reporting dashboards."
        ],
        "education": "M.S. in Applied Statistics, University of Michigan"
    }
}

styles = getSampleStyleSheet()
title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), spaceAfter=6)
subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=12)
h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), leading=12, spaceAfter=4)

for filename, data in RESUMES.items():
    # 1. Text version
    txt_path = os.path.join(SAMPLE_DIR, f"{filename}.txt")
    with open(txt_path, "w") as f:
        f.write(f"NAME: {data['name']}\n")
        f.write(f"TARGET ROLE: {data['role']}\n")
        f.write(f"EMAIL: {data['email']}\n\n")
        f.write(f"SUMMARY:\n{data['summary']}\n\n")
        f.write(f"TECHNICAL SKILLS:\n{', '.join(data['skills'])}\n\n")
        f.write(f"CORE DOMAINS:\n{', '.join(data['domains'])}\n\n")
        f.write("EXPERIENCE:\n")
        for exp in data['experience']:
            f.write(f"- {exp}\n")
        f.write(f"\nEDUCATION:\n{data['education']}\n")
    print(f"Generated text resume: {txt_path}")

    # 2. PDF version
    pdf_path = os.path.join(SAMPLE_DIR, f"{filename}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = [
        Paragraph(data['name'], title_style),
        Paragraph(f"{data['role']} &nbsp;|&nbsp; {data['email']}", subtitle_style),
        Spacer(1, 4),
        Paragraph("Professional Summary", h2_style),
        Paragraph(data['summary'], body_style),
        Spacer(1, 4),
        Paragraph("Technical Skills & Technologies", h2_style),
        Paragraph("<b>Languages & Tools:</b> " + ", ".join(data['skills']), body_style),
        Paragraph("<b>Domain Competencies:</b> " + ", ".join(data['domains']), body_style),
        Spacer(1, 4),
        Paragraph("Professional Experience", h2_style),
    ]
    for exp in data['experience']:
        story.append(Paragraph(f"• {exp}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Education", h2_style))
    story.append(Paragraph(data['education'], body_style))
    doc.build(story)
    print(f"Generated PDF resume: {pdf_path}")
