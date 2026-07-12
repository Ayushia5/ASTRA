def compute_lsi(signal: dict) -> dict:
    """
    Computes the Leak Severity Index (LSI) score based on multiple signals.
    """
    # Extract inputs with defaults
    question_count = signal.get("question_count", 0)
    hours = signal.get("hours_to_exam", 999.0)
    platform = signal.get("source_platform", "other").lower()
    spread_count = signal.get("spread_count", 0)
    classification = signal.get("classification", "unclear").lower()

    # SIGNAL 1: Question density (0-25 pts)
    if question_count >= 20:
        s1_score = 25
    elif question_count >= 10:
        s1_score = 18
    elif question_count >= 5:
        s1_score = 12
    elif question_count >= 2:
        s1_score = 7
    else:
        s1_score = 2

    # SIGNAL 2: Temporal proximity (0-25 pts)
    if hours <= 0:
        s2_score = 5
    elif hours <= 6:
        s2_score = 25
    elif hours <= 12:
        s2_score = 20
    elif hours <= 24:
        s2_score = 15
    elif hours <= 48:
        s2_score = 8
    else:
        s2_score = 2

    # SIGNAL 3: Platform risk (0-20 pts)
    if platform == "whatsapp":
        s3_score = 20
    elif platform == "telegram":
        s3_score = 18
    elif platform == "reddit":
        s3_score = 12
    elif platform == "youtube":
        s3_score = 10
    else:
        s3_score = 8

    # SIGNAL 4: Spread signal (0-20 pts)
    if spread_count >= 5:
        s4_score = 20
    elif spread_count >= 3:
        s4_score = 14
    elif spread_count >= 1:
        s4_score = 8
    else:
        s4_score = 0

    # SIGNAL 5: Classification modifier (-15 to +10 pts)
    if classification == "high_risk":
        s5_score = 10
    elif classification == "possible_genuine":
        s5_score = 5
    elif classification == "ghost_paper":
        s5_score = -15
    elif classification == "fake_claim":
        s5_score = -10
    else:
        s5_score = 0

    # Final score = clamp(sum of all signals, 0, 100)
    total_score = s1_score + s2_score + s3_score + s4_score + s5_score
    lsi_score = max(0, min(100, total_score))

    # Triage levels
    if lsi_score >= 75:
        triage_level = "CRITICAL"
        action = "EMERGENCY_REVIEW"
    elif lsi_score >= 55:
        triage_level = "ELEVATED"
        action = "HUMAN_REVIEW"
    elif lsi_score >= 35:
        triage_level = "MODERATE"
        action = "MONITOR"
    else:
        triage_level = "LOW"
        action = "LOG_ONLY"

    return {
        "lsi_score": lsi_score,
        "triage_level": triage_level,
        "recommended_action": action,
        "breakdown": {
            "question_density": s1_score,
            "temporal_proximity": s2_score,
            "platform_risk": s3_score,
            "spread_signal": s4_score,
            "classification_modifier": s5_score
        }
    }


if __name__ == "__main__":
    import json

    # 1. High risk: 15 questions, 5 hrs to exam, telegram, spread=3, classification=high_risk
    tc1 = {
        "question_count": 15,
        "hours_to_exam": 5,
        "source_platform": "telegram",
        "spread_count": 3,
        "classification": "high_risk"
    }
    print("Test Case 1 (High risk):")
    print(json.dumps(compute_lsi(tc1), indent=2))
    print("-" * 40)

    # 2. Ghost paper: 8 questions, 10 hrs, telegram, spread=0, classification=ghost_paper
    tc2 = {
        "question_count": 8,
        "hours_to_exam": 10,
        "source_platform": "telegram",
        "spread_count": 0,
        "classification": "ghost_paper"
    }
    print("Test Case 2 (Ghost paper):")
    print(json.dumps(compute_lsi(tc2), indent=2))
    print("-" * 40)

    # 3. Low signal: 1 question, 72 hrs, other, spread=0, unclear
    tc3 = {
        "question_count": 1,
        "hours_to_exam": 72,
        "source_platform": "other",
        "spread_count": 0,
        "classification": "unclear"
    }
    print("Test Case 3 (Low signal):")
    print(json.dumps(compute_lsi(tc3), indent=2))
    print("-" * 40)
