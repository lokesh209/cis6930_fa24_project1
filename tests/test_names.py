import spacy
from redactor import redact_names

# Load spaCy model for testing
nlp = spacy.blank("en")

def test_redact_names():
    text = "John Doe met with Jane Smith at the Enron headquarters."
    doc = nlp(text)
    # Assume Enron is in the EXCEPTION_WORDS
    expected = "████ ███ met with ████ █████ at the Enron headquarters."
    redacted_doc = redact_names(doc)
    assert redacted_doc.text == expected
