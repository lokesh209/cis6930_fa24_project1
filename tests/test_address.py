import spacy
from redactor import redact_address

nlp = spacy.blank("en")

def test_redact_address():
    text = "Visit us at 611 Jersey Ave., Jersey City NJ 07302."
    doc = nlp(text)
    expected = "Visit us at ███████████████████████████████."
    redacted_doc = redact_address(doc)
    assert redacted_doc.text == expected
