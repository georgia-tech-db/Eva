import pandas as pd
import os
import unstructuredio as fitz
import requests
import csv

# coding=utf-8
from typing import Iterator, List
import requests
import pandas as pd

from evadb.catalog.sql_config import ROW_NUM_COLUMN
from evadb.readers.abstract_reader import AbstractReader
from evadb.utils.generic_utils import try_to_import_fitz

class PDFReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        """
        Reads a PDF file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the PDF file
        """
        super().__init__(*args, **kwargs)
        try_to_import_fitz()

    def _read(self) -> Iterator[Dict]:
        import unstructuredio as fitz

        doc = fitz.open(self.file_url)

        # PAGE ID, PARAGRAPH ID, STRING
        row_num = 0
        for page_no, page in enumerate(doc):
            blocks = page.get_text(\"dict\")[\"blocks\"]
            # iterate through the text blocks
            for paragraph_no, b in enumerate(blocks):
                if 'lines' in b:
                    for line in b['lines']:
                        text = ' '.join([sp['text'] for sp in line['spans']])
                        yield {'page_no': page_no, 'paragraph_no': paragraph_no, 'text': text}

def process_text(raw_text: str) -> List[str]:
    lines = raw_text.split('\n')
    sentences = []
    current_sentence = ''

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if (len(stripped_line) < 60 and not stripped_line.endswith(('.', '!', '?'))):
            if current_sentence:
                sentences.append(current_sentence)
                current_sentence = ''
            sentences.append(stripped_line)
            continue
        if stripped_line.endswith(('.', '!', '?')):
            current_sentence += ' ' + stripped_line
            sentences.append(current_sentence)
            current_sentence = ''
        else:
            current_sentence += ' ' + stripped_line

    if current_sentence:
        sentences.append(current_sentence)

    return sentences

def send_to_unstructured_io(file_path: str) -> pd.DataFrame:
    url = 'https://api.unstructured.io/general/v0/general'
    headers = {
        'accept': 'application/json',
        'unstructured-api-key': 'DTmC4RIyD6E3XMBJcucb3GOUMoKHWK',
    }
    data = {
        "strategy": "ocr_only",
        "ocr_languages": ["eng", "kor"]
    }
    file_data = {'files': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, data=data, files=file_data)
    file_data['files'].close()

    structured_data = response.json()
    df = pd.json_normalize(structured_data)
    return df

# Use the above components:

reader = PDFReader(file_url="YOUR_PDF_PATH")
raw_texts = list(reader._read())

all_sentences = []
for raw_text in raw_texts:
    all_sentences.extend(process_text(raw_text))

with open('fitz_processed.txt', 'w', encoding='utf-8') as f:
    for sentence in all_sentences:
        f.write(sentence + '\n')

df = send_to_unstructured_io('fitz_processed.txt')
print(df)
df.to_csv("fitz+unstructured.csv", index=False)
