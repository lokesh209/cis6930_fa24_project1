import spacy
from redactor import redact_phones

nlp = spacy.blank("en")
nlp.add_pipe('sentencizer')

def test_redact_phones():
    text = "Contact us at (555) 123-4567 or 555-123-4567 or +1 (555) 123-4567."
    doc = nlp(text)
    expected = "Contact us at ██████████████ or ████████████ or +1 ██████████████."
    redacted_doc = redact_phones(doc)
    print(f"Redacted Address: {str(redacted_doc)}")  # Add this line

    assert str(redacted_doc) == expected
