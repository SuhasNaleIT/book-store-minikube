# Book-store-G4
Book Store Flask App
# 📚 BookStore — CSC8113 Group Project

A cloud-native bookstore application built with Flask, deployed on Kubernetes with HPA scaling, CI/CD via GitHub Actions, and IaC via Terraform.

---

## Project Structure

```
bookstore/
├── app/
│   └── __init__.py       ← Flask app factory + Hello World route
├── config.py             ← App configuration (reads from .env)
├── run.py                ← Entry point to start the app
├── requirements.txt      ← Python dependencies
├── .env.example          ← Environment variable template (safe to commit)
├── .gitignore            ← Files excluded from Git
└── README.md             ← This file
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/bookstore.git
cd bookstore
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://flask_user:flask_pass@localhost:5432/flask_demo_db
```

### 5. Run the app

```bash
python run.py
```

Visit: [http://localhost:5000](http://localhost:5000)

You should see the **BookStore Hello World** page.

---

## Team Services

| Service | Technology | Owner |
|---|---|---|
| Catalogue Service | Python / Flask | |
| Cart Service | Java / Spring Boot | |
| Frontend | React / Node.js | |
| Database | PostgreSQL | Shared |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | PostgreSQL |
| Containerisation | Docker |
| Orchestration | Kubernetes (EKS) |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Load Testing | k6 |

---

## Health Check

```
GET /health → { "status": "healthy" }
```

Used by Kubernetes liveness probe.
