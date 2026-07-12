"""Graph API routes."""
from fastapi import APIRouter, Query
from db.neo4j_client import get_spread_graph

router = APIRouter()

@router.get("/graph-data")
async def get_graph(
    exam_name: str = Query(..., description="Required exam name")
):
    """Get spread graph for an exam."""
    graph_data = get_spread_graph(exam_name)
    
    formatted_nodes = []
    for n in graph_data.get("nodes", []):
        node_data = {
            "id": str(n.get("id", "")),
            "label": str(n.get("label", "")),
            "lsi_score": int(n.get("lsi_score", 0)),
            "triage_level": str(n.get("triage_level", "LOW")),
            "platform": str(n.get("platform", "unknown"))
        }
        if "name" in n:
            node_data["name"] = str(n["name"])
        formatted_nodes.append(node_data)
        
    formatted_edges = []
    for e in graph_data.get("edges", []):
        formatted_edges.append({
            "from": str(e.get("from", "")),
            "to": str(e.get("to", "")),
            "type": str(e.get("type", ""))
        })
        
    return {
        "nodes": formatted_nodes,
        "edges": formatted_edges
    }
