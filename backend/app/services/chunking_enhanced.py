"""
Enhanced hierarchical chunking service for legal documents.
Preserves document structure, sections, headings, and metadata.
"""
from typing import List, Dict, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class EnhancedChunkingService:
    """
    Advanced chunking service that preserves document structure.
    Features:
    - Section-aware chunking
    - Heading detection and preservation
    - Sentence-safe splitting
    - Paragraph preservation
    - Table and list detection
    - Section title attachment to chunks
    """
    
    # Legal section heading patterns
    SECTION_PATTERNS = [
        r'^SECTION\s+\d+[\.:]?\s*[A-Z]',  # SECTION 1: Title
        r'^Article\s+\d+[\.:]?\s*[A-Z]',    # Article 1: Title
        r'^\d+\.\s+[A-Z][A-Z\s]{10,}',    # 1. TITLE IN CAPS
        r'^[A-Z][A-Z\s]{15,}$',           # ALL CAPS HEADING
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:\s*$',  # Title Case Heading:
    ]
    
    # Legal clause patterns
    CLAUSE_PATTERNS = [
        r'^\d+\.\d+\.?\s+[A-Z]',          # 1.1. Clause
        r'^\([a-z]\)\s+[A-Z]',            # (a) Clause
        r'^\([ivx]+\)\s+[A-Z]',           # (i) Clause
    ]
    
    # Exhibit/Attachment patterns
    EXHIBIT_PATTERNS = [
        r'EXHIBIT\s+[A-Z]',
        r'ATTACHMENT\s+[A-Z]',
        r'APPENDIX\s+[A-Z]',
        r'SCHEDULE\s+[A-Z]',
    ]
    
    def __init__(
        self,
        chunk_size: int = 800,  # Smaller chunks for better precision
        overlap: int = 150,     # More overlap for context
        min_chunk_size: int = 100  # Minimum chunk size
    ):
        """
        Initialize enhanced chunking service.
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to avoid tiny fragments
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict = None,
        page_number: Optional[int] = None
    ) -> List[Dict]:
        """
        Chunk a document with hierarchical structure preservation.
        
        Args:
            text: Full document text
            metadata: Base metadata for all chunks
            page_number: Optional page number
            
        Returns:
            List of chunks with structure metadata
        """
        if not text or not text.strip():
            return []
        
        # Step 1: Identify document structure (sections, headings, exhibits)
        structure = self._identify_structure(text)
        
        # Step 2: Split into sections
        sections = self._split_into_sections(text, structure)
        
        # Step 3: Chunk each section while preserving context
        all_chunks = []
        chunk_index = 0
        
        for section in sections:
            section_chunks = self._chunk_section(
                section,
                chunk_index,
                metadata,
                page_number
            )
            all_chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from document structure")
        return all_chunks
    
    def _identify_structure(self, text: str) -> Dict:
        """Identify document structure: sections, headings, exhibits."""
        lines = text.split('\n')
        structure = {
            'sections': [],
            'headings': [],
            'exhibits': [],
            'tables': []
        }
        
        current_section = None
        current_heading = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check for section heading
            for pattern in self.SECTION_PATTERNS:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    current_section = {
                        'type': 'section',
                        'title': line_stripped,
                        'line_number': i,
                        'level': self._detect_heading_level(line_stripped)
                    }
                    structure['sections'].append(current_section)
                    current_heading = current_section
                    break
            
            # Check for clause
            for pattern in self.CLAUSE_PATTERNS:
                if re.match(pattern, line_stripped):
                    clause = {
                        'type': 'clause',
                        'title': line_stripped,
                        'line_number': i,
                        'parent_section': current_section
                    }
                    structure['headings'].append(clause)
                    current_heading = clause
                    break
            
            # Check for exhibit
            for pattern in self.EXHIBIT_PATTERNS:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    exhibit = {
                        'type': 'exhibit',
                        'title': line_stripped,
                        'line_number': i
                    }
                    structure['exhibits'].append(exhibit)
                    break
        
        return structure
    
    def _detect_heading_level(self, heading: str) -> int:
        """Detect heading hierarchy level."""
        if re.match(r'^SECTION\s+\d+', heading, re.IGNORECASE):
            return 1
        elif re.match(r'^Article\s+\d+', heading, re.IGNORECASE):
            return 1
        elif re.match(r'^\d+\.\s+[A-Z]', heading):
            return 2
        elif re.match(r'^\d+\.\d+\.', heading):
            return 3
        else:
            return 2
    
    def _split_into_sections(self, text: str, structure: Dict) -> List[Dict]:
        """Split text into sections based on identified structure."""
        if not structure['sections'] and not structure['headings']:
            # No clear structure - split by double newlines
            return [{'type': 'paragraph', 'title': None, 'text': text}]
        
        lines = text.split('\n')
        sections = []
        current_section = None
        current_text = []
        current_title = None
        
        for i, line in enumerate(lines):
            is_heading = False
            
            # Check if this line is a section heading
            for section in structure['sections']:
                if section['line_number'] == i:
                    # Save previous section
                    if current_section:
                        sections.append({
                            'type': 'section',
                            'title': current_title,
                            'text': '\n'.join(current_text),
                            'level': current_section.get('level', 2)
                        })
                    # Start new section
                    current_section = section
                    current_title = section['title']
                    current_text = []
                    is_heading = True
                    break
            
            # Check if this line is a clause heading
            if not is_heading:
                for heading in structure['headings']:
                    if heading['line_number'] == i:
                        # Save previous section if it exists
                        if current_section and current_text:
                            sections.append({
                                'type': 'section',
                                'title': current_title,
                                'text': '\n'.join(current_text),
                                'level': current_section.get('level', 2)
                            })
                        # Start new subsection
                        current_section = heading
                        current_title = heading['title']
                        current_text = []
                        is_heading = True
                        break
            
            if not is_heading:
                current_text.append(line)
        
        # Add final section
        if current_section and current_text:
            sections.append({
                'type': 'section',
                'title': current_title,
                'text': '\n'.join(current_text),
                'level': current_section.get('level', 2)
            })
        
        # If no sections were created, return full text as one section
        if not sections:
            sections.append({
                'type': 'paragraph',
                'title': None,
                'text': text
            })
        
        return sections
    
    def _chunk_section(
        self,
        section: Dict,
        start_index: int,
        base_metadata: Dict = None,
        page_number: Optional[int] = None
    ) -> List[Dict]:
        """Chunk a single section while preserving context."""
        text = section['text']
        section_title = section.get('title')
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_index = start_index
        
        for para in paragraphs:
            # If paragraph is too large, split by sentences
            if len(para) > self.chunk_size:
                sentences = self._split_sentences(para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 <= self.chunk_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk.strip() and len(current_chunk.strip()) >= self.min_chunk_size:
                            chunks.append(self._create_enhanced_chunk(
                                current_chunk.strip(),
                                chunk_index,
                                section_title,
                                base_metadata,
                                page_number
                            ))
                            chunk_index += 1
                        
                        # Start new chunk with overlap
                        if chunks and self.overlap > 0:
                            overlap_text = current_chunk[-self.overlap:].strip()
                            current_chunk = overlap_text + " " + sentence + " "
                        else:
                            current_chunk = sentence + " "
            else:
                # Paragraph fits - add to current chunk
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    # Save current chunk
                    if current_chunk.strip() and len(current_chunk.strip()) >= self.min_chunk_size:
                        chunks.append(self._create_enhanced_chunk(
                            current_chunk.strip(),
                            chunk_index,
                            section_title,
                            base_metadata,
                            page_number
                        ))
                        chunk_index += 1
                    
                    # Start new chunk with overlap
                    if chunks and self.overlap > 0:
                        overlap_text = current_chunk[-self.overlap:].strip()
                        current_chunk = overlap_text + "\n\n" + para + "\n\n"
                    else:
                        current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk.strip() and len(current_chunk.strip()) >= self.min_chunk_size:
            chunks.append(self._create_enhanced_chunk(
                current_chunk.strip(),
                chunk_index,
                section_title,
                base_metadata,
                page_number
            ))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, preserving legal numbering."""
        # Split by sentence endings, but preserve legal numbering
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_enhanced_chunk(
        self,
        text: str,
        index: int,
        section_title: Optional[str],
        base_metadata: Dict = None,
        page_number: Optional[int] = None
    ) -> Dict:
        """Create a chunk with enhanced metadata."""
        chunk = {
            "chunk_index": index,
            "text": text,
            "char_count": len(text),
            "token_estimate": len(text) // 4,
            "section_title": section_title,
            "has_section_title": section_title is not None
        }
        
        # Add base metadata
        if base_metadata:
            chunk["metadata"] = {**base_metadata}
            if page_number is not None:
                chunk["metadata"]["page"] = page_number
        elif page_number is not None:
            chunk["metadata"] = {"page": page_number}
        
        # Detect clause types in chunk
        chunk["detected_clauses"] = self._detect_clause_types(text)
        
        return chunk
    
    def _detect_clause_types(self, text: str) -> List[str]:
        """Detect what types of legal clauses are in this chunk."""
        text_lower = text.lower()
        detected = []
        
        clause_keywords = {
            "payment": ["payment", "compensation", "fee", "invoice", "billing", "price"],
            "termination": ["termination", "terminate", "cancel", "expire", "end of agreement"],
            "liability": ["liability", "liable", "damage", "loss"],
            "indemnification": ["indemnif", "hold harmless", "defend"],
            "confidentiality": ["confidential", "non-disclosure", "nda", "proprietary"],
            "scope": ["scope of work", "services", "deliverables", "work to be performed"],
            "warranty": ["warranty", "warrant", "guarantee"],
            "insurance": ["insurance", "coverage", "policy"],
            "dispute": ["dispute", "arbitration", "mediation", "jurisdiction"],
        }
        
        for clause_type, keywords in clause_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(clause_type)
        
        return detected
    
    def chunk_by_pages(
        self,
        pages: List[Dict],
        file_id: str = None
    ) -> List[Dict]:
        """
        Chunk text that's already separated by pages, preserving structure.
        
        Args:
            pages: List of page dictionaries with 'page_number' and 'text'
            file_id: Optional file ID for metadata
            
        Returns:
            List of chunks with enhanced metadata
        """
        all_chunks = []
        base_metadata = {"file_id": file_id} if file_id else {}
        
        for page in pages:
            page_num = page.get("page_number", 0)
            page_text = page.get("text", "")
            
            if not page_text.strip():
                continue
            
            # Use enhanced chunking for each page
            page_chunks = self.chunk_document(
                page_text,
                metadata=base_metadata,
                page_number=page_num
            )
            all_chunks.extend(page_chunks)
        
        return all_chunks


# Global enhanced chunking service instance
enhanced_chunking_service = EnhancedChunkingService(
    chunk_size=800,
    overlap=150,
    min_chunk_size=100
)

