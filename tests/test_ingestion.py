from app.services.file_ingestion import extract_text

def test_txt_ingestion():
    assert extract_text("debate.txt", b"A: Claim\nB: Response") == "A: Claim\nB: Response"
