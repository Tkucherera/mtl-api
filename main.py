import sys
import os


from services.trip import Trip
from logger import activity_logger, error_logger, stdout_logger
from services.extract_trip_details import extract_from_pdf, process_pdf_text
from messages import *


resp = extract_from_pdf('/home/tinashe/Desktop/projects/mtl-api/tests/test-data/pdfs/VAR-2001.pdf')

if resp.apicode == 201:
    content = resp.raw()
    text = content['created']['raw_text']
    p = process_pdf_text(text)
    print(p)