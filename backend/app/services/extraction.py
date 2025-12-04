"""
Text extraction service for PDF and DOCX files.
"""
import fitz  # PyMuPDF
from docx import Document
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from various document formats."""
    
    @staticmethod
    def extract_pdf_text(file_path: Path) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text, page count, and metadata
        """
        try:
            doc = fitz.open(file_path)
            pages = []
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                pages.append({
                    "page_number": page_num + 1,
                    "text": text.strip()
                })
                full_text.append(text)
            
            doc.close()
            
            return {
                "success": True,
                "pages_count": len(pages),
                "pages": pages,
                "full_text": "\n\n".join(full_text),
                "metadata": {
                    "format": "pdf",
                    "total_chars": len("".join(full_text))
                }
            }
        
        except Exception as e:
            logger.error(f"PDF extraction error for {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "pages_count": 0
            }
    
    @staticmethod
    def extract_docx_text(file_path: Path) -> Dict[str, any]:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            doc = Document(file_path)
            paragraphs = []
            full_text = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
                    full_text.append(text)
            
            return {
                "success": True,
                "paragraphs_count": len(paragraphs),
                "paragraphs": paragraphs,
                "full_text": "\n\n".join(full_text),
                "metadata": {
                    "format": "docx",
                    "total_chars": len("".join(full_text))
                }
            }
        
        except Exception as e:
            logger.error(f"DOCX extraction error for {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def extract_text(file_path: Path, file_type: str) -> Dict[str, any]:
        """
        Extract text from a file based on its type.
        
        Args:
            file_path: Path to file
            file_type: Type of file (pdf, docx, txt)
            
        Returns:
            Extraction results dictionary
        """
        if file_type.lower() == "pdf":
            return TextExtractionService.extract_pdf_text(file_path)
        elif file_type.lower() == "docx":
            return TextExtractionService.extract_docx_text(file_path)
        elif file_type.lower() == "txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                return {
                    "success": True,
                    "full_text": text,
                    "metadata": {
                        "format": "txt",
                        "total_chars": len(text)
                    }
                }
            except Exception as e:
                logger.error(f"TXT extraction error for {file_path}: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_type}"
            }


# Global extraction service instance
text_extractor = TextExtractionService()
