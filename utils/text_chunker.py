from typing import List, Dict
import re

class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, meta: Dict) -> List[Dict]:
        """
        Splits text into chunks with overlap.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # If not at the end, try to break at a newline or space
            if end < text_len:
                # Look for last newline in the chunk
                last_newline = text.rfind('\n', start, end)
                if last_newline != -1:
                    end = last_newline + 1
                else:
                    # Look for last space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "meta": meta,
                    "chunkId": f"{meta.get('docId')}_{len(chunks)}"
                })
            
            start += (self.chunk_size - self.overlap)
            
        return chunks
