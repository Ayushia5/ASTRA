from datetime import datetime, timezone

def build_triage_card(
    signal_id: str,
    upload_meta: dict,
    ocr_result: str,
    language_result: dict,
    questions: list[str],
    classification: dict,
    lsi_result: dict,
    neo4j_node_id: str
) -> dict:
    
    triage_level = lsi_result["triage_level"]
    color_map = {
        "CRITICAL": "red",
        "ELEVATED": "orange",
        "MODERATE": "yellow",
        "LOW": "green"
    }
    triage_color = color_map.get(triage_level, "green")
    
    return {
        "signal_id": signal_id,
        "exam_event": upload_meta["exam_name"],
        "exam_date": upload_meta["exam_date"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lsi_score": lsi_result["lsi_score"],
        "triage_level": triage_level,
        "recommended_action": lsi_result["recommended_action"],
        "lsi_breakdown": lsi_result["breakdown"],
        "classification": classification["classification"],
        "classification_confidence": classification["confidence"],
        "classification_reasoning": classification["reasoning"],
        "original_language": language_result["original_language"],
        "was_translated": language_result["was_translated"],
        "extracted_questions": questions[:5],
        "question_count": len(questions),
        "source_platform": upload_meta.get("source_platform", "unknown"),
        "neo4j_node_id": neo4j_node_id,
        "triage_color": triage_color
    }
