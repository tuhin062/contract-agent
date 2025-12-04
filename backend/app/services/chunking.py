"""
Text chunking service for splitting documents into manageable pieces.
Used for embedding generation and vector storage.
"""
from typing import List, Dict
import re


class ChunkingService:
    """Service for splitting text into overlapping chunks."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 100,
        separator: str = "\n\n"
    ):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            separator: Primary separator for splitting (paragraphs by default)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separator = separator
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to include with each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split by primary separator (paragraphs)
        sections = text.split(self.separator)
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If section itself is larger than chunk_size, split it further
            if len(section) > self.chunk_size:
                # Split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', section)
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                        current_chunk += (sentence + " ")
                    else:
                        if current_chunk:
                            chunks.append(self._create_chunk(
                                current_chunk.strip(),
                                chunk_index,
                                metadata
                            ))
                            chunk_index += 1
                        
                        # Start new chunk with overlap from previous
                        if chunks and self.overlap > 0:
                            overlap_text = current_chunk[-self.overlap:].strip()
                            current_chunk = overlap_text + " " + sentence + " "
                        else:
                            current_chunk = sentence + " "
            else:
                # Section fits, add to current chunk
                if len(current_chunk) + len(section) + 2 <= self.chunk_size:
                    current_chunk += (section + "\n\n")
                else:
                    if current_chunk:
                        chunks.append(self._create_chunk(
                            current_chunk.strip(),
                            chunk_index,
                            metadata
                        ))
                        chunk_index += 1
                    
                    # Start new chunk with overlap
                    if chunks and self.overlap > 0:
                        overlap_text = current_chunk[-self.overlap:].strip()
                        current_chunk = overlap_text + "\n\n" + section + "\n\n"
                    else:
                        current_chunk = section + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(
                current_chunk.strip(),
                chunk_index,
                metadata
            ))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, metadata: Dict = None) -> Dict:
        """
        Create a chunk dictionary.
        
        Args:
            text: Chunk text
            index: Chunk index
            metadata: Optional metadata
            
        Returns:
            Chunk dictionary
        """
        chunk = {
            "chunk_index": index,
            "text": text,
            "char_count": len(text),
            "token_estimate": len(text) // 4  # Rough estimate: 1 token ≈ 4 chars
        }
        
        if metadata:
            chunk["metadata"] = metadata
        
        return chunk
    
    def chunk_by_pages(
        self,
        pages: List[Dict],
        file_id: str = None
    ) -> List[Dict]:
        """
        Chunk text that's already separated by pages.
        
        Args:
            pages: List of page dictionaries with 'page_number' and 'text'
            file_id: Optional file ID for metadata
            
        Returns:
            List of chunk dictionaries with page metadata
        """
        all_chunks = []
        
        for page in pages:
            page_num = page.get("page_number", 0)
            page_text = page.get("text", "")
            
            if not page_text.strip():
                continue
            
            page_metadata = {
                "page": page_num
            }
            if file_id:
                page_metadata["file_id"] = file_id
            
            page_chunks = self.chunk_text(page_text, page_metadata)
            all_chunks.extend(page_chunks)
        
        return all_chunks


# Global chunking service instance
chunking_service = ChunkingService(chunk_size=1000, overlap=100)
