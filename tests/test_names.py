import spacy
from redactor import redact_names

# Load spaCy model for testing
nlp = spacy.blank("en")
nlp.add_pipe('sentencizer')

def test_redact_names():
    text = "hospital met with hiphen at the Enron headquarters."
    doc = nlp(text)
    # Assume Enron is in the EXCEPTION_WORDS
    expected = "hospital met with hiphen at the Enron headquarters."
    redacted_doc = redact_names(doc)
    assert str(redacted_doc) == expected
