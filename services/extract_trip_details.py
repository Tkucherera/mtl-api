"""
Extract trip details service module.
author: Tinashe Kucherera
date: 2024-06-20
description: Service to extract trip details from various data sources.
"""



"""
The goal here is to have a dedicated service that can handle the extraction of trip details from different formats or sources.
For now the idea is to be avle to get details from a pdf, email body, or image (OCR).
"""
import sys
import os
import camelot
from pypdf import PdfReader
from messages import *
import pandas as pd




def check_pdf_tables(file_path: str):
    tables = camelot.read_pdf(file_path, flavor="stream")
    return tables.n
    # come back and revisit logic



def extract_from_pdf(file_path: str) -> dict:
    """
    Extract trip details from a PDF file.
    """
    # check if file exists
    if not os.path.exists(file_path):
        return ResourceNotFound({'file': file_path})
    
    # see if there are any tables 
    tables = check_pdf_tables(file_path)

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Here we would implement actual parsing logic to extract trip details from the text
    # For now, we will return the raw text
    return ResourceCreated({'raw_text': text})

def process_pdf_text(text: str) -> dict:
    """
    Process extracted text from PDF to find trip details.
    """
    # Placeholder implementation
    trip_details = {
        "broker": None,
        "rate_con_number": None,
        "rate": None,
        "pickup_location": None,
        "dropoff_location": None,
        "pickup_date": None,
        "delivery_date": None,
        "weight": None,
    }

    keywords_map = {
        "broker": ("broker", "brokerage", "shipper"),
        "rate_con_number": ("rate confirmation number", "RCN", "rate con #", "rate con", "invoice #"),
        "rate": ("rate:", "amount"),
        "pickup_location": ("Pickup Location", "from"),
        "dropoff_location": ("Dropoff Location", "to"),
        "pickup_date": ("Pickup Date", "pick up"),
        "delivery_date": ("Delivery Date", "deliver by", "due date"),
    }

    lines = text.splitlines()
    for line in lines:
        lower_line = line.lower()
        for key, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword.lower() in lower_line and ':' in lower_line and trip_details[key] is None:
                    # Try to extract value after the keyword
                    parts = lower_line.split(': ')
                    if len(parts) > 1:
                        value = parts[1]
                        trip_details[key] = value if value else None
                    else:
                        trip_details[key] = None
    
    return trip_details

# TODO - Test against more pdfs 
# TODO - explore ways ai can read this information

