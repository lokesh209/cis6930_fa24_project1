import spacy
from redactor import redact_phones

nlp = spacy.blank("en")

def test_redact_phones():
    text = "Contact us at (555) 123-4567 or 555-123-4567 or +1 (555) 123-4567."
    doc = nlp(text)
    expected = "Contact us at ██████████████ or ███████████ or ██████████████████."
    redacted_doc = redact_phones(doc)
    assert redacted_doc.text == expected
