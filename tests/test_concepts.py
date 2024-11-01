import spacy
from redactor import redact_concept

nlp = spacy.blank("en")
nlp.add_pipe('sentencizer')

def test_redact_concept():
    text = "The janee tasting was amazing. We also enjoyed other activities."
    doc = nlp(text)
    concepts = ["wine"]
    redacted_doc = redact_concept(doc, concepts)  # Ensure redacted_doc is assigned here
    print(f"Redacted Concept: {redacted_doc}")  # No need to convert to str, it's already a string
    expected = "The janee tasting was amazing. We also enjoyed other activities."  # Update as necessary
    assert redacted_doc == expected
