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

# Add sentencizer to the pipeline for sentence segmentation
nlp.add_pipe("sentencizer")

def redact_names(doc):
    """Redact person and organization names from the document."""
    redacted = doc.text
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG'] and ent.text not in EXCEPTION_WORDS:
            redacted = redacted.replace(ent.text, REDACTION_CHAR * len(ent.text))
    return redacted

def redact_dates(doc):
    """Redact dates from the document using regular expressions."""
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
    """Redact phone numbers from the document using regular expressions."""
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
    """Redact addresses and location entities from the document."""
    address_pattern = r'\d+\s+(?:[A-Za-z]+\s*)+,\s*(?:[A-Za-z]+\s*)+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?'
    redacted = re.sub(address_pattern, lambda m: REDACTION_CHAR * len(m.group()), doc.text)
    
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC', 'FAC']:
            redacted = redacted.replace(ent.text, REDACTION_CHAR * len(ent.text))
    
    return redacted

def redact_concept(doc, concepts):
    """Redact entire sentences containing specified concepts."""
    redacted = []
    sents = list(doc.sents)
    i = 0
    while i < len(sents):
        sent = sents[i]
        if any(concept.lower() in sent.text.lower() for concept in concepts):
            redacted.append(REDACTION_CHAR * len(sent.text))
        else:
            redacted.append(sent.text)
        i += 1
    return " ".join(redacted)

def process_file(input_file, output_file, flags, concepts):
    """Process a single file, applying all specified redactions."""
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Preprocess text once
    doc = nlp(text)
    
    # Apply each redaction step
    if 'names' in flags:
        text = redact_names(doc)
    if 'dates' in flags:
        text = redact_dates(doc)
    if 'phones' in flags:
        text = redact_phones(doc)
    if 'address' in flags:
        text = redact_address(doc)
    if concepts:
        text = redact_concept(doc, concepts)
    
    # Process final redacted text with spaCy for sentence boundary info
    redacted_doc = nlp(text)

    # Calculate statistics
    original_length = len(doc.text)
    redacted_length = len(redacted_doc.text)
    stats = {
        "original_length": original_length,
        "redacted_length": redacted_length,
        "redaction_percentage": (original_length - redacted_length) / original_length * 100
    }

    # Write redacted text and statistics to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(redacted_doc.text)
        f.write("\n\n--- Statistics ---\n")
        f.write(f"Original length: {stats['original_length']}\n")
        f.write(f"Redacted length: {stats['redacted_length']}\n")
        f.write(f"Redaction percentage: {stats['redaction_percentage']:.2f}%\n")
    
    return stats

def generate_stats(stats, stats_output):
    """Generate and output overall statistics."""
    # Create a list of formatted strings for each statistic
    stats_lines = [f"{k}: {v}" for k, v in stats.items()]
    
    # Join the formatted strings into a single text
    stats_text = "\n".join(stats_lines)
    
    # Output the statistics based on the specified output location
    if stats_output in ("stderr", "stdout"):
        output_stream = sys.stderr if stats_output == "stderr" else sys.stdout
        print(stats_text, file=output_stream)
    else:
        with open(stats_output, 'w', encoding='utf-8') as f:
            f.write(stats_text)

def main():
    """Main function to handle command-line arguments and process files."""
    # Set up command-line argument parser
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
    
    # Determine which redaction flags are active
    flags = [flag for flag, value in vars(args).items() if value and flag in {'names', 'dates', 'phones', 'address'}]
    concepts = args.concept or []
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize total statistics
    total_stats = {
        "files_processed": 0,
        "total_chars_original": 0,
        "total_chars_redacted": 0
    }
    
    # Process each input file
    for input_file in args.input:
        output_file = os.path.join(args.output, f"{os.path.basename(input_file)}.censored")
        file_stats = process_file(input_file, output_file, flags, concepts)
        
        # Update total statistics
        total_stats["files_processed"] += 1
        total_stats["total_chars_original"] += file_stats["original_length"]
        total_stats["total_chars_redacted"] += file_stats["redacted_length"]
    
    # Calculate overall redaction percentage
    total_chars_diff = total_stats["total_chars_redacted"] - total_stats["total_chars_original"]
    total_stats["redaction_percentage"] = (total_chars_diff / total_stats["total_chars_original"]) * 100
    
    # Generate and output overall statistics
    generate_stats(total_stats, args.stats)

if __name__ == "__main__":
    main()
