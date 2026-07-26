"""
skills_db.py
Static database of technical & soft skills used for:
 - Skill extraction from resumes
 - Resume <-> Job Description keyword/skill matching

Kept as a plain Python list (no internet download required) so the
application works fully offline after `pip install -r requirements.txt`.
"""

TECHNICAL_SKILLS = [
    # Programming Languages
    "python", "java", "c++", "c", "c#", "javascript", "typescript", "php",
    "ruby", "go", "golang", "swift", "kotlin", "r", "matlab", "scala",
    "perl", "rust", "dart", "sql", "html", "css", "bash", "shell scripting",

    # Web Development
    "flask", "django", "fastapi", "react", "react.js", "angular", "vue",
    "vue.js", "node.js", "nodejs", "express.js", "bootstrap", "tailwind",
    "jquery", "next.js", "redux", "rest api", "restful api", "graphql",
    "web sockets", "ajax", "json", "xml",

    # Data Science / AI / ML
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "nlp", "computer vision",
    "data science", "data analysis", "data analytics", "data visualization",
    "data mining", "data engineering", "big data", "statistics",
    "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch",
    "pandas", "numpy", "matplotlib", "seaborn", "opencv", "nltk", "spacy",
    "neural networks", "cnn", "rnn", "lstm", "transformers", "llm",
    "generative ai", "prompt engineering", "feature engineering",
    "predictive modeling", "regression", "classification", "clustering",
    "reinforcement learning", "xgboost", "hadoop", "spark", "pyspark",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
    "cassandra", "firebase", "dbms", "database management",
    "nosql", "elasticsearch",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "jenkins", "ci/cd", "git", "github", "gitlab", "linux", "unix",
    "terraform", "ansible", "devops", "microservices", "cloud computing",
    "nginx", "apache",

    # Tools / Software
    "excel", "power bi", "tableau", "jira", "postman", "vs code",
    "figma", "photoshop", "canva", "microsoft office", "word", "powerpoint",

    # Mobile
    "android", "ios", "flutter", "react native", "android studio",

    # Other CS Fundamentals
    "data structures", "algorithms", "oop", "object oriented programming",
    "operating systems", "computer networks", "software engineering",
    "system design", "api development", "unit testing", "agile", "scrum",
    "version control", "debugging", "problem solving",
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "presentation skills", "project management",
    "decision making", "analytical skills", "attention to detail",
    "interpersonal skills", "conflict resolution", "multitasking",
    "work ethic", "self motivated", "self-motivated", "team player",
]

ALL_SKILLS = sorted(set(TECHNICAL_SKILLS + SOFT_SKILLS), key=len, reverse=True)

# Common section header keywords used to detect resume sections
SECTION_HEADERS = {
    "education": ["education", "academic background", "academic qualification",
                  "qualifications", "educational background"],
    "skills": ["skills", "technical skills", "core competencies",
               "key skills", "skill set", "areas of expertise"],
    "projects": ["projects", "academic projects", "personal projects",
                 "key projects", "project experience"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment history", "internship", "internships",
                   "work history"],
    "certifications": ["certifications", "certificates", "licenses",
                        "certification", "courses"],
    "languages": ["languages", "language proficiency", "spoken languages"],
    "summary": ["summary", "objective", "career objective",
                "professional summary", "profile"],
    "achievements": ["achievements", "awards", "accomplishments", "honors"],
}

# Common resume action verbs (used for weak-resume detection)
ACTION_VERBS = [
    "developed", "designed", "implemented", "created", "built", "managed",
    "led", "led", "improved", "increased", "decreased", "reduced",
    "optimized", "analyzed", "collaborated", "coordinated", "achieved",
    "delivered", "launched", "automated", "engineered", "architected",
    "streamlined", "spearheaded", "executed", "organized", "solved",
    "researched", "presented", "trained", "mentored", "deployed",
]

COMMON_LANGUAGES = [
    "english", "hindi", "spanish", "french", "german", "chinese",
    "mandarin", "japanese", "korean", "russian", "arabic", "portuguese",
    "italian", "bengali", "marathi", "gujarati", "punjabi", "tamil",
    "telugu", "kannada", "malayalam", "urdu", "odia", "assamese",
]
