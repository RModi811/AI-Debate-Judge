from app.config import RUBRIC

def calculate_score(scores: dict[str, int]) -> float:
    total = 0.0
    for dimension, weight in RUBRIC["dimensions"].items():
        value = max(1, min(10, int(scores.get(dimension, 1))))
        total += value * weight
    return round(total * 10, 2)
