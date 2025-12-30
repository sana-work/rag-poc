import os
import argparse
from pathlib import Path
import json
import logging
from typing import List

# Import parsers
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_pdf(file_path: Path) -> str:
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return ""

def parse_docx(file_path: Path) -> str:
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        return ""

def parse_html(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        logger.error(f"Error parsing HTML {file_path}: {e}")
        return ""

def ingest_docs(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    supported_extensions = {'.pdf': parse_pdf, '.docx': parse_docx, '.html': parse_html}
    
    count = 0
    for file_path in input_path.rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            parser = supported_extensions[file_path.suffix.lower()]
            logger.info(f"Processing {file_path.name}...")
            
            text = parser(file_path)
            if text:
                # Normalize whitespace
                text = " ".join(text.split())
                
                doc_id = file_path.stem
                output_file = output_path / f"{doc_id}.txt"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Save metadata
                meta_file = output_path / f"{doc_id}.meta.json"
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "sourcePath": str(file_path),
                        "docTitle": file_path.name,
                        "docId": doc_id
                    }, f)
                
                count += 1
                
    logger.info(f"Ingested {count} documents to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents")
    parser.add_argument("--input", required=True, help="Input directory containing docs")
    parser.add_argument("--output", default="data/interim", help="Output directory for text")
    args = parser.parse_args()
    
    ingest_docs(args.input, args.output)
