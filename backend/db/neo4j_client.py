"""Neo4j driver setup and connectivity."""
import os
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()

_driver: Driver | None = None

def get_driver() -> Driver:
    """Get or initialize the Neo4j driver singleton."""
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "")
        user = os.getenv("NEO4J_USERNAME", "")
        password = os.getenv("NEO4J_PASSWORD", "")
        
        try:
            _driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            print(f"[WARNING] get_driver: Failed to initialize Neo4j driver - {e}")
            raise
    return _driver

def verify_connectivity() -> bool:
    """Verify connectivity to the Neo4j database."""
    try:
        driver = get_driver()
        driver.verify_connectivity()
        return True
    except Exception as e:
        print(f"[WARNING] verify_connectivity: Neo4j connection failed - {e}")
        return False
