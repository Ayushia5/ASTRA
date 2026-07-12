"""Neo4j driver setup and connectivity."""
import os
import hashlib
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

_driver = None

def get_driver():
    """Get or initialize the Neo4j driver singleton."""
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "")
        user = os.getenv("NEO4J_USERNAME", "")
        password = os.getenv("NEO4J_PASSWORD", "")
        try:
            _driver = GraphDatabase.driver(uri, auth=(user, password))
            _driver.verify_connectivity()
            print(f"[INFO] get_driver: Connected using {uri}")
        except Exception as e:
            if "Unable to retrieve routing information" in str(e) and uri.startswith("neo4j+s://"):
                fallback_uri = uri.replace("neo4j+s://", "bolt+ssc://")
                print(f"[WARNING] get_driver: Failed with neo4j+s://. Retrying with {fallback_uri} ...")
                try:
                    _driver = GraphDatabase.driver(fallback_uri, auth=(user, password))
                    _driver.verify_connectivity()
                    print(f"[INFO] get_driver: Successfully connected using fallback: {fallback_uri}")
                except Exception as fallback_e:
                    print(f"[WARNING] get_driver: Fallback also failed - {fallback_e}")
                    raise fallback_e
            else:
                print(f"[WARNING] get_driver: Failed to initialize - {e}")
                raise
    return _driver

def verify_connection() -> bool:
    """Verify connectivity to the Neo4j database."""
    try:
        driver = get_driver()
        driver.verify_connectivity()
        return True
    except Exception as e:
        print(f"[WARNING] verify_connection: Neo4j connection failed - {e}")
        return False

def create_signal_node(card: dict) -> str:
    """Create a Post node and related nodes in Neo4j from a triage card."""
    query = """
    MERGE (e:ExamEvent {name: $exam_name})
    ON CREATE SET e.exam_date = $exam_date, e.created_at = datetime()
    CREATE (p:Post {
        signal_id: $signal_id,
        lsi_score: $lsi_score,
        triage_level: $triage_level,
        classification: $classification,
        platform: $platform,
        question_count: $question_count,
        original_language: $original_language,
        first_seen: datetime(),
        recommended_action: $recommended_action
    })
    CREATE (p)-[:RELATED_TO]->(e)
    WITH p
    UNWIND $questions AS q_pair
    MERGE (q:Question {question_hash: q_pair.hash})
    ON CREATE SET q.text = q_pair.text
    CREATE (p)-[:CONTAINS]->(q)
    RETURN p.signal_id AS node_id
    """
    questions = card.get("extracted_questions", [])
    q_pairs = [{"text": q, "hash": hashlib.sha256(q.encode()).hexdigest()[:16]} for q in questions]
    params = {
        "exam_name": card.get("exam_event", "Unknown"),
        "exam_date": card.get("exam_date", ""),
        "signal_id": card.get("signal_id", ""),
        "lsi_score": card.get("lsi_score", 0),
        "triage_level": card.get("triage_level", "LOW"),
        "classification": card.get("classification", "unclear"),
        "platform": card.get("source_platform", "unknown"),
        "question_count": card.get("question_count", 0),
        "original_language": card.get("original_language", "en"),
        "recommended_action": card.get("recommended_action", "LOG_ONLY"),
        "questions": q_pairs
    }
    try:
        driver = get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, **params)
            record = result.single()
            return record["node_id"] if record else card.get("signal_id", "unknown")
    except Exception as e:
        print(f"[ERROR] create_signal_node failed: {e}")
        return "neo4j_write_failed"

def get_all_signals(limit: int = 50) -> list:
    """Fetch all Post nodes ordered by first_seen descending."""
    try:
        driver = get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(
                "MATCH (p:Post) RETURN p ORDER BY p.first_seen DESC LIMIT $limit",
                {"limit": limit}
            )
            return [dict(record["p"]) for record in result]
    except Exception as e:
        print(f"[ERROR] get_all_signals failed: {e}")
        return []

def get_spread_graph(exam_name: str) -> dict:
    """Return nodes and edges for the spread graph visualization."""
    try:
        driver = get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(
                "MATCH (p:Post)-[:RELATED_TO]->(e:ExamEvent {name: $exam_name}) RETURN p, e",
                {"exam_name": exam_name}
            )
            nodes, edges, seen = [], [], set()
            for record in result:
                post = dict(record["p"])
                exam = dict(record["e"])
                if post["signal_id"] not in seen:
                    nodes.append({"id": post["signal_id"], "label": "Post",
                                  "lsi_score": post.get("lsi_score", 0),
                                  "triage_level": post.get("triage_level", "LOW"),
                                  "platform": post.get("platform", "unknown")})
                    seen.add(post["signal_id"])
                exam_id = f"exam_{exam_name}"
                if exam_id not in seen:
                    nodes.append({"id": exam_id, "label": "ExamEvent", "name": exam_name})
                    seen.add(exam_id)
                edges.append({"from": post["signal_id"], "to": exam_id, "type": "RELATED_TO"})
            return {"nodes": nodes, "edges": edges}
    except Exception as e:
        print(f"[ERROR] get_spread_graph failed: {e}")
        return {"nodes": [], "edges": []}

if __name__ == "__main__":
    print("Neo4j connected:", verify_connection())