import spacy
import re
import os
import argparse
import sys
from spacy.tokens import Doc

# Define constants
VERSION = "1.0.0"
REDACTION_CHAR = '█'
EXCEPTION_WORDS = {'Enron'}

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading language model for the spaCy POS tagger\n(don't worry, this will only happen once)")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Add sentencizer to the pipeline
nlp.add_pipe("sentencizer")

def redact_names(doc):
    redacted = doc.text
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG'] and ent.text not in EXCEPTION_WORDS:
            redacted = redacted.replace(ent.text, REDACTION_CHAR * len(ent.text))
    return redacted

def redact_dates(doc):
    date_patterns = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:st|nd|rd|th)?,?\s?\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2}(?:st|nd|rd|th)?,?\s?\d{4}\b'
    ]
    redacted = doc.text
    for pattern in date_patterns:
        redacted = re.sub(pattern, lambda m: REDACTION_CHAR * len(m.group()), redacted)
    return redacted

def redact_phones(doc):
    phone_patterns = [
        r'\(\d{3}\)\s?\d{3}-\d{4}',  # (555) 123-4567
        r'\d{3}-\d{3}-\d{4}',        # 555-123-4567
        r'\d{10}',                   # 5551234567
        r'\+\d{1,2}\s?\(\d{3}\)\s?\d{3}-\d{4}'  # +1 (555) 123-4567
    ]
    redacted = doc.text
    for pattern in phone_patterns:
        redacted = re.sub(pattern, lambda m: REDACTION_CHAR * len(m.group()), redacted)
    return redacted

def redact_address(doc):
    address_pattern = r'\d+\s+(?:[A-Za-z]+\s*)+,\s*(?:[A-Za-z]+\s*)+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?'
    redacted = re.sub(address_pattern, lambda m: REDACTION_CHAR * len(m.group()), doc.text)
    
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC', 'FAC']:
            redacted = redacted.replace(ent.text, REDACTION_CHAR * len(ent.text))
    
    return redacted

def redact_concept(doc, concepts):
    redacted = []
    for sent in doc.sents:
        if any(concept.lower() in sent.text.lower() for concept in concepts):
            redacted.append(REDACTION_CHAR * len(sent.text))
        else:
            redacted.append(sent.text)
    return " ".join(redacted)

def process_file(input_file, output_file, flags, concepts):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Apply each redaction step, re-processing with nlp each time
    if 'names' in flags:
        text = redact_names(nlp(text))
    if 'dates' in flags:
        text = redact_dates(nlp(text))
    if 'phones' in flags:
        text = redact_phones(nlp(text))
    if 'address' in flags:
        text = redact_address(nlp(text))
    if concepts:
        text = redact_concept(nlp(text), concepts)
    
    # Process final redacted text with spaCy for sentence boundary info
    doc = nlp(text)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc.text)
    
    return {"original_length": len(text), "redacted_length": len(doc.text)}

def generate_stats(stats, stats_output):
    stats_text = "\n".join(f"{k}: {v}" for k, v in stats.items())
    
    if stats_output == "stderr":
        print(stats_text, file=sys.stderr)
    elif stats_output == "stdout":
        print(stats_text)
    else:
        with open(stats_output, 'w', encoding='utf-8') as f:
            f.write(stats_text)

def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text documents.")
    parser.add_argument('--version', '-v', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument("--input", required=True, nargs='+', help="Input file(s) or glob pattern")
    parser.add_argument("--names", action="store_true", help="Redact names")
    parser.add_argument("--dates", action="store_true", help="Redact dates")
    parser.add_argument("--phones", action="store_true", help="Redact phone numbers")
    parser.add_argument("--address", action="store_true", help="Redact addresses")
    parser.add_argument("--concept", action="append", help="Redact sentences containing specified concepts")
    parser.add_argument("--output", required=True, help="Directory to store redacted files")
    parser.add_argument("--stats", required=True, help="Where to output statistics (stderr, stdout, or file path)")
    
    args = parser.parse_args()
    
    flags = []
    if args.names:
        flags.append('names')
    if args.dates:
        flags.append('dates')
    if args.phones:
        flags.append('phones')
    if args.address:
        flags.append('address')
    
    concepts = args.concept if args.concept else []
    
    os.makedirs(args.output, exist_ok=True)
    
    total_stats = {"files_processed": 0, "total_chars_original": 0, "total_chars_redacted": 0}
    
    for input_file in args.input:
        output_file = os.path.join(args.output, os.path.basename(input_file) + ".censored")
        file_stats = process_file(input_file, output_file, flags, concepts)
        total_stats["files_processed"] += 1
        total_stats["total_chars_original"] += file_stats["original_length"]
        total_stats["total_chars_redacted"] += file_stats["redacted_length"]
    
    total_stats["redaction_percentage"] = (total_stats["total_chars_redacted"] - total_stats["total_chars_original"]) / total_stats["total_chars_original"] * 100
    
    generate_stats(total_stats, args.stats)

if __name__ == "__main__":
    main()
