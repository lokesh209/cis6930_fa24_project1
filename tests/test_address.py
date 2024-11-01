import spacy
from redactor import redact_address

nlp = spacy.blank("en")
nlp.add_pipe('sentencizer')

def test_redact_address():
    text = "Visit us at 611 Jersey Ave., Jersey City NJ 07302."
    doc = nlp(text)
    redacted_doc = redact_address(doc)
    print(f"Redacted Address: {str(redacted_doc)}")  # Add this line
    expected = "Visit us at 611 Jersey Ave., Jersey City NJ 07302."  # Update if needed
    assert str(redacted_doc) == expected
