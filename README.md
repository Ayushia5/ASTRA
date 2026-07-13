# Astra — Assessment Signal Triage & Risk Analysis

> **Protecting Trust in Every Examination**

Astra is a real-time exam paper leak intelligence and triage system. When suspicious content circulates on Telegram, Reddit, WhatsApp, or YouTube before a high-stakes exam, Astra ingests it, extracts questions via OCR, classifies it using AI, scores its credibility, and produces a structured triage card for exam authorities to act on.

**"We don't claim to stop every leak. We reduce the time between the first signal and the first informed action."**

---

## Live Demo

| Service | URL |
|---|---|
| Dashboard | https://astra-threat-guard.base44.app |
| Backend API | https://astra-kem4.onrender.com |
| API Health | https://astra-kem4.onrender.com/health |

---

## The Problem

On April 30, 2026, a full Cambridge A Level Mathematics paper appeared on Reddit 7 hours before the exam. By 5 AM it was circulating across WhatsApp groups in Pakistan, India, and Bangladesh. The exam was at 9 AM. Cambridge administers exams in 160+ countries. No system flagged it in time.

This is not an isolated incident. NEET 2026, Cambridge 2025, Cambridge 2024 — three consecutive years of confirmed leaks affecting millions of students. The pattern is consistent: signals appear hours before the exam, spread across platforms, and authorities act only after the damage is done.

The gap between **first signal** and **first informed action** is measured in hours. Astra measures it in seconds.

---

## What Astra Does

1. An admin uploads a suspicious screenshot from Telegram, Reddit, or WhatsApp
2. Astra runs OCR, detects language, translates if needed (Sarvam Mayura)
3. Sarvam-M classifies the content: genuine leak, ghost paper, fake claim, or unclear
4. The Leak Signal Index (LSI) scores the signal 0–100 across 5 weighted factors
5. A structured triage card is returned with a recommended action
6. The signal and its spread are stored in Neo4j AuraDB as a graph
7. Admins see the spread graph — which platforms, how many posts, which questions

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Backend API | FastAPI + Python 3.11 | Pipeline orchestration |
| OCR | Tesseract (eng+hin+urd) | Question extraction |
| Translation | Sarvam Mayura | 22-language multilingual support |
| Classification | Sarvam-M | Content classification |
| Scoring | LSI Algorithm (custom) | 5-signal weighted scoring |
| Graph Database | Neo4j AuraDB | Spread graph storage |
| Monitoring | Render Background Worker | Durable 3-step workflow |
| Dashboard | Base44 | Admin triage interface |

---

## Sponsor Track Integrations

### Neo4j AuraDB
Astra stores every signal as a graph. Posts connect to ExamEvents, Questions, and Platforms via typed relationships. The spread graph shows how many posts contain the same question across how many platforms — the core evidence of a genuine leak.

**Key Cypher query (spread detection):**
```cypher
MATCH (p:Post)-[:CONTAINS]->(q:Question)<-[:CONTAINS]-(p2:Post)
WHERE p.signal_id <> p2.signal_id
RETURN q.text AS question, count(DISTINCT p) AS spread_count
ORDER BY spread_count DESC
```

In the Cambridge 2026 demo scenario, this query returns 3 questions each appearing across 8 posts — the signature of a real leak.

### Sarvam AI
Two integrations:
- **Mayura (translation):** Detects non-English input and translates to English before processing. Supports Hindi, Urdu, and 20+ Indian languages.
- **Sarvam-M (classification):** Classifies extracted content and returns structured JSON with classification, confidence, and reasoning.

### Render Workflows
Astra runs a durable 3-step monitoring workflow as a Render Background Worker. Each step has independent error handling — if Step 1 fails, Steps 2 and 3 still run. The workflow sweeps for critical signals every 30 minutes.

### Base44
The admin dashboard built on Base44 provides three views: Upload Signal (form → triage card), Signal Feed (live signal list), and Spread Graph (vis.js network visualization connected to Neo4j).

---

## The LSI Score

The Leak Signal Index scores each signal 0–100 across 5 weighted factors:

| Signal | Max Points | Logic |
|---|---|---|
| Question density | 25 | More questions extracted = higher risk |
| Temporal proximity | 25 | Closer to exam = higher risk |
| Platform risk | 20 | WhatsApp (closed) > Telegram > Reddit |
| Spread signal | 20 | More similar posts = higher risk |
| Classification modifier | ±15 | ghost_paper = −15, high_risk = +10 |

**Triage levels:** CRITICAL (≥75) → ELEVATED (≥55) → MODERATE (≥35) → LOW

---

## Ghost Paper Detection

Coaching institutes routinely circulate "predicted papers" before exams — these look identical to real leaks in terms of spread pattern. Astra's Sarvam-M classifier identifies coaching institute language patterns and applies a −15 modifier to the LSI score, preventing false positives that could cause authorities to cancel exams unnecessarily.

---

## Architecture
[Admin Upload] → [FastAPI /upload]
→ OCR (Tesseract)
→ Language Detection (langdetect)
→ Translation (Sarvam Mayura)
→ Question Extraction
→ Classification (Sarvam-M)
→ LSI Scoring
→ Neo4j Write (Post + Question + ExamEvent nodes)
→ Triage Card Response
→ [Base44 Dashboard]
[Render Background Worker] → every 30 min
→ Step 1: fetch signals
→ Step 2: check thresholds (LSI ≥ 75)
→ Step 3: log escalations

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Tesseract OCR (`brew install tesseract` / `apt install tesseract-ocr`)
- Neo4j AuraDB free account
- Sarvam AI API key

### Quick Start
```bash
git clone https://github.com/Ayushia5/ASTRA
cd ASTRA/backend
cp .env.example .env
# Fill in .env with your credentials
pip install -r requirements.txt
python db/seed_data.py
uvicorn main:app --reload
```

### Environment Variables
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=xxxxxxxx
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=xxxxxxxx
SARVAM_API_KEY=your-sarvam-key
BACKEND_URL=https://your-render-url.onrender.com

```
### Seed Demo Data
```bash
python db/seed_data.py
```
Creates 13 posts across Cambridge A Level Mathematics 2026 and NEET 2026 scenarios with realistic spread patterns.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/upload` | POST | Analyze a signal (multipart/form-data) |
| `/signals` | GET | List all triage signals |
| `/graph-data` | GET | Spread graph for a given exam |

---

## Future Roadmap

- Real-time Telegram channel monitoring via Bot API
- Sarvam Saaras V3 voice note transcription
- Automated escalation via WhatsApp Business API
- Official paper hash comparison (requires exam board partnership)
- Multi-board exam calendar integration

---

## Team

Built for HackHazards '26

---

## License

MIT