from app.services.score_calculator import calculate_score

def test_score_calculation():
    scores = {"reasoning":10,"clash":10,"weighing":10,"clarity":10,"strategy":10,"persuasion":10}
    assert calculate_score(scores) == 100.0
