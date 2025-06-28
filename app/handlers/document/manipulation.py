"""
PDF Manipulation Utilities (merge, split, info)
"""

import os
import json
import logging
from typing import List

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

logger = logging.getLogger('gmail-mcp')

# --- PDF Manipulation Functions ---

def merge_pdfs_util(
    input_files: List[str],
    output_filename: str
) -> str:
    if not PYPDF2_AVAILABLE:
        return "Error: PyPDF2 not available. Cannot merge PDFs."
    try:
        writer = PdfWriter()
        for pdf_file in input_files:
            if not os.path.exists(pdf_file):
                return f"Error: File '{pdf_file}' not found."
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        with open(output_filename, 'wb') as output_file:
            writer.write(output_file)
        file_size = os.path.getsize(output_filename)
        result = {
            'status': 'success',
            'output_filename': output_filename,
            'input_files': input_files,
            'total_files_merged': len(input_files),
            'size_bytes': file_size
        }
        logger.info(f"Merged {len(input_files)} PDFs into '{output_filename}'")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        return f"Error: {str(e)}"

def split_pdf_util(
    input_file: str,
    output_directory: str,
    pages_per_file: int = 1
) -> str:
    if not PYPDF2_AVAILABLE:
        return "Error: PyPDF2 not available. Cannot split PDFs."
    try:
        if not os.path.exists(input_file):
            return f"Error: File '{input_file}' not found."
        os.makedirs(output_directory, exist_ok=True)
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        output_files = []
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        for i in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            end_page = min(i + pages_per_file, total_pages)
            for page_num in range(i, end_page):
                writer.add_page(reader.pages[page_num])
            if pages_per_file == 1:
                output_filename = f"{base_name}_page_{i+1}.pdf"
            else:
                output_filename = f"{base_name}_pages_{i+1}-{end_page}.pdf"
            output_path = os.path.join(output_directory, output_filename)
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            output_files.append(output_path)
        result = {
            'status': 'success',
            'input_file': input_file,
            'output_directory': output_directory,
            'output_files': output_files,
            'total_pages': total_pages,
            'files_created': len(output_files),
            'pages_per_file': pages_per_file
        }
        logger.info(f"Split PDF '{input_file}' into {len(output_files)} files")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        return f"Error: {str(e)}"

def pdf_info_util(filename: str) -> str:
    if not PYPDF2_AVAILABLE:
        return "Error: PyPDF2 not available. Cannot read PDF info."
    try:
        if not os.path.exists(filename):
            return f"Error: File '{filename}' not found."
        reader = PdfReader(filename)
        info = {
            'filename': filename,
            'size_bytes': os.path.getsize(filename),
            'total_pages': len(reader.pages),
            'encrypted': reader.is_encrypted
        }
        if reader.metadata:
            metadata = {}
            for key, value in reader.metadata.items():
                if key.startswith('/'):
                    clean_key = key[1:].lower()
                    metadata[clean_key] = str(value) if value else ""
            info['metadata'] = metadata
        if len(reader.pages) > 0:
            first_page = reader.pages[0]
            mediabox = first_page.mediabox
            info['page_size'] = {
                'width': float(mediabox.width),
                'height': float(mediabox.height),
                'width_inches': float(mediabox.width) / 72,
                'height_inches': float(mediabox.height) / 72
            }
        logger.info(f"Retrieved info for PDF '{filename}'")
        return json.dumps(info, indent=2)
    except Exception as e:
        logger.error(f"Error getting PDF info: {str(e)}")
        return f"Error: {str(e)}" 