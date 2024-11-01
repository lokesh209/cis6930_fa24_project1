#The Redactor - CIS 6930 Fall 2024 Project 1

##Project Description

This project implements a redaction tool for censoring sensitive information in text documents. It can redact names, dates, phone numbers, addresses, and specific concepts. The program processes plain text files using natural language processing to identify and censor sensitive information based on the specified flags.

##project Structure
`redactor.py`: Main script that handles command-line arguments, file processing, and orchestrates the redaction process.
`redactor_helper.py`: Contains helper functions for various redaction tasks.

##How to Install

Ensure you have Python 3.12.0  installed.

Install Required Packages:
 
`` pip install spacy argparse`` 

Download the Spacy English model:

``python -m spacy download en_core_web_sm``

How to Run

use following command 

``python redactor.py --input <input_files> --output <output_directory> [OPTIONS]``

Example

``python redactor.py --input 'docs/*.txt' --names --dates --phones --address --concept 'wine' --output 'redacted_files/' --stats stderr``

Functions

redactor.py

`main()`: Orchestrates the redaction process.

`process_file()`: Handles the redaction of a single file.

`generate_stats()`: Generates and outputs statistics.

redactor_helper.py

`redact_names()`: Redacts person and organization names.

`redact_dates()`: Redacts dates using regular expressions.

`redact_phones()`: Redacts phone numbers.

`redact_address()`: Redacts addresses and location entities.

`redact_concept()`: Redacts sentences containing specified concepts.

Testing 

To test the code

`pipenv run python -m pytest`

Bugs and Assumptions

Assumption: The code assumes that all input files are in UTF-8 encoding. Files in other encodings may cause unexpected behavior.

Bug: The redaction of dates may occasionally redact non-date numbers that match date patterns (e.g., "10/12" might be redacted even if it's not a date).

Assumption: The code assumes that redacting a word with the redaction character maintains the original word boundaries. This may not always be true for all text editors or viewers.

Bug: The concept redaction may sometimes redact entire sentences that contain common words if those words are similar to the specified concepts.

Assumption: The code assumes that all phone numbers follow North American formats. International phone numbers may not be correctly identified.

Bug: In some cases, closely spaced entities (like a name immediately followed by a date) might be merged into a single redaction, potentially over-redacting
.
Assumption: The code assumes that the SpaCy model's named entity recognition is always accurate, which may not be the case for all types of text.

Bug: The address redaction might occasionally redact non-address text that happens to match the address pattern (e.g., "123 Great Ideas").

Assumption: The code assumes that maintaining the original file's line breaks is not critical. Some redactions might alter the original line structure.

Bug: In rare cases, the redaction process might introduce extra spaces or remove necessary spaces, potentially affecting the readability of the redacted text.
