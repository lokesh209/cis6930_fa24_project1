import spacy
from redactor import redact_concept

nlp = spacy.blank("en")

def test_redact_concept():
    text = "The wine tasting was amazing. We also enjoyed other activities."
    doc = nlp(text)
    concepts = ["wine"]
    expected = "████████████████████████████████. We also enjoyed other activities."
    redacted_doc = redact_concept(doc, concepts)
    assert redacted_doc.text == expected
