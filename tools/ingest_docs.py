import os
from pathlib import Path
from pptx import Presentation
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, BSHTMLLoader

def load_pptx(file_path: Path) -> str:
    """
    Extracts text from a PowerPoint (.pptx) file.
    
    Args:
        file_path (Path): Path to the .pptx file.
        
    Returns:
        str: Combined text from all slides.
    """
    prs = Presentation(file_path)
    text_runs = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                text_runs.append(shape.text)
    return "\n".join(text_runs)

def ingest_docs(corpus_name: str):
    """
    Parses raw documents from data/source and saves text to data/interim.
    Supports: .pdf, .docx, .html, .pptx
    """
    base_dir = Path(__file__).parent.parent
    source_dir = base_dir / "data" / "source" / corpus_name
    interim_dir = base_dir / "data" / "interim" / corpus_name

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} not found.")
        return

    interim_dir.mkdir(parents=True, exist_ok=True)

    print(f"Ingesting documents from {source_dir}...")
    
    files = list(source_dir.glob("*.*"))
    if not files:
        print("  No files found.")
        return

    for file in files:
        output_file = interim_dir / f"{file.stem}.txt"
        
        # Skip if already processed (naive check)
        # if output_file.exists():
        #     continue

        print(f"  Processing {file.name}...")
        try:
            # Load text based on extension
            text = ""
            if file.suffix == ".pdf":
                loader = PyPDFLoader(str(file))
                pages = loader.load()
                text = "\n".join([p.page_content for p in pages])
            
            elif file.suffix == ".docx":
                loader = UnstructuredWordDocumentLoader(str(file))
                docs = loader.load()
                text = "\n".join([d.page_content for d in docs])

            elif file.suffix == ".pptx":
                print(f"  [PPTX] Extracting slides from {file.name}...")
                text = load_pptx(file)

            elif file.suffix == ".html":
                loader = BSHTMLLoader(str(file))
                docs = loader.load()
                text = "\n".join([d.page_content for d in docs])
            
            else:
                print(f"  Skipping unsupported file: {file.name}")
                continue

            # Save to interim
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            
        except Exception as e:
            print(f"  Error processing {file.name}: {e}")

    print("Ingestion complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingest_docs.py <corpus_name>")
        sys.exit(1)
    ingest_docs(sys.argv[1])
