"""Seed Neo4j AuraDB with realistic demo spread graph data."""
import hashlib
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.neo4j_client import get_driver

DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def seed():
    """Seed demo data for Cambridge 2026 and NEET 2026 scenarios."""
    driver = get_driver()

    cambridge_posts = [
        {"signal_id": "cam-001", "platform": "reddit",   "lsi_score": 82, "triage_level": "CRITICAL",  "classification": "high_risk",        "original_language": "en", "hours_before": 7.0},
        {"signal_id": "cam-002", "platform": "telegram", "lsi_score": 78, "triage_level": "CRITICAL",  "classification": "high_risk",        "original_language": "en", "hours_before": 6.5},
        {"signal_id": "cam-003", "platform": "whatsapp", "lsi_score": 55, "triage_level": "ELEVATED",  "classification": "possible_genuine", "original_language": "hi", "hours_before": 5.0},
        {"signal_id": "cam-004", "platform": "telegram", "lsi_score": 61, "triage_level": "ELEVATED",  "classification": "possible_genuine", "original_language": "en", "hours_before": 4.5},
        {"signal_id": "cam-005", "platform": "reddit",   "lsi_score": 45, "triage_level": "MODERATE",  "classification": "possible_genuine", "original_language": "en", "hours_before": 4.0},
        {"signal_id": "cam-006", "platform": "telegram", "lsi_score": 89, "triage_level": "CRITICAL",  "classification": "high_risk",        "original_language": "ur", "hours_before": 3.5},
        {"signal_id": "cam-007", "platform": "youtube",  "lsi_score": 25, "triage_level": "LOW",       "classification": "fake_claim",       "original_language": "en", "hours_before": 3.0},
        {"signal_id": "cam-008", "platform": "telegram", "lsi_score": 72, "triage_level": "ELEVATED",  "classification": "high_risk",        "original_language": "en", "hours_before": 2.0},
    ]

    neet_posts = [
        {"signal_id": "neet-001", "platform": "telegram", "lsi_score": 78, "triage_level": "CRITICAL",  "classification": "high_risk",        "original_language": "hi", "hours_before": 8.0},
        {"signal_id": "neet-002", "platform": "whatsapp", "lsi_score": 65, "triage_level": "ELEVATED",  "classification": "possible_genuine", "original_language": "hi", "hours_before": 6.0},
        {"signal_id": "neet-003", "platform": "telegram", "lsi_score": 55, "triage_level": "ELEVATED",  "classification": "possible_genuine", "original_language": "en", "hours_before": 5.0},
        {"signal_id": "neet-004", "platform": "reddit",   "lsi_score": 38, "triage_level": "MODERATE",  "classification": "possible_genuine", "original_language": "en", "hours_before": 4.0},
        {"signal_id": "neet-005", "platform": "telegram", "lsi_score": 70, "triage_level": "ELEVATED",  "classification": "high_risk",        "original_language": "hi", "hours_before": 2.0},
    ]

    cambridge_questions = [
        "If f(x) = x² + 3x + 2, find the roots of f(x) = 0",
        "Differentiate y = sin(3x) + cos(2x) with respect to x",
        "A particle moves with velocity v = 4t² - 6t. Find displacement from t=0 to t=3",
    ]

    neet_questions = [
        "Which of the following is not a feature of the genetic code?",
        "The resting membrane potential of a neuron is approximately",
    ]

    with driver.session(database=DATABASE) as session:
        # Clear existing seed data
        session.run("MATCH (n) WHERE n.signal_id STARTS WITH 'cam-' OR n.signal_id STARTS WITH 'neet-' DETACH DELETE n")

        # Create Cambridge exam event
        session.run("""
            MERGE (e:ExamEvent {name: 'Cambridge A Level Mathematics 2026'})
            ON CREATE SET e.exam_date = '2026-04-30', e.board = 'Cambridge International', e.created_at = datetime()
        """)

        # Create NEET exam event
        session.run("""
            MERGE (e:ExamEvent {name: 'NEET 2026'})
            ON CREATE SET e.exam_date = '2026-05-04', e.board = 'NTA', e.created_at = datetime()
        """)

        # Create Cambridge question nodes
        for q_text in cambridge_questions:
            q_hash = hashlib.sha256(q_text.encode()).hexdigest()[:16]
            session.run("""
                MERGE (q:Question {question_hash: $hash})
                ON CREATE SET q.text = $text
            """, {"hash": q_hash, "text": q_text})

        # Create NEET question nodes
        for q_text in neet_questions:
            q_hash = hashlib.sha256(q_text.encode()).hexdigest()[:16]
            session.run("""
                MERGE (q:Question {question_hash: $hash})
                ON CREATE SET q.text = $text
            """, {"hash": q_hash, "text": q_text})

        # Create Cambridge posts
        for i, post in enumerate(cambridge_posts):
            session.run("""
                CREATE (p:Post {
                    signal_id: $signal_id,
                    platform: $platform,
                    lsi_score: $lsi_score,
                    triage_level: $triage_level,
                    classification: $classification,
                    original_language: $original_language,
                    question_count: 3,
                    recommended_action: $action,
                    first_seen: datetime() - duration({hours: $hours})
                })
                WITH p
                MATCH (e:ExamEvent {name: 'Cambridge A Level Mathematics 2026'})
                CREATE (p)-[:RELATED_TO]->(e)
            """, {
                **post,
                "action": "EMERGENCY_REVIEW" if post["lsi_score"] >= 75 else "HUMAN_REVIEW",
                "hours": post["hours_before"]
            })

            # Connect each Cambridge post to all 3 questions
            for q_text in cambridge_questions:
                q_hash = hashlib.sha256(q_text.encode()).hexdigest()[:16]
                session.run("""
                    MATCH (p:Post {signal_id: $signal_id})
                    MATCH (q:Question {question_hash: $hash})
                    CREATE (p)-[:CONTAINS]->(q)
                """, {"signal_id": post["signal_id"], "hash": q_hash})

        # Create NEET posts
        for post in neet_posts:
            session.run("""
                CREATE (p:Post {
                    signal_id: $signal_id,
                    platform: $platform,
                    lsi_score: $lsi_score,
                    triage_level: $triage_level,
                    classification: $classification,
                    original_language: $original_language,
                    question_count: 2,
                    recommended_action: $action,
                    first_seen: datetime() - duration({hours: $hours})
                })
                WITH p
                MATCH (e:ExamEvent {name: 'NEET 2026'})
                CREATE (p)-[:RELATED_TO]->(e)
            """, {
                **post,
                "action": "EMERGENCY_REVIEW" if post["lsi_score"] >= 75 else "HUMAN_REVIEW",
                "hours": post["hours_before"]
            })

            # Connect NEET posts to questions
            for q_text in neet_questions:
                q_hash = hashlib.sha256(q_text.encode()).hexdigest()[:16]
                session.run("""
                    MATCH (p:Post {signal_id: $signal_id})
                    MATCH (q:Question {question_hash: $hash})
                    CREATE (p)-[:CONTAINS]->(q)
                """, {"signal_id": post["signal_id"], "hash": q_hash})

    print(f"Seed complete: {len(cambridge_posts)} Cambridge posts + {len(neet_posts)} NEET posts + {len(cambridge_questions) + len(neet_questions)} questions created")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Seed failed: {e}")
        sys.exit(1)