"""
Local filesystem storage service with abstraction for future cloud migration.
Provides a consistent interface for file operations that can be easily swapped
for S3, Google Cloud Storage, or Azure Blob Storage.
"""
from pathlib import Path
from datetime import datetime
from typing import BinaryIO, Optional
import shutil
import uuid
from app.core.config import settings


class StorageService:
    """
    Local filesystem storage service.
    
    This service provides file storage operations on the local filesystem.
    The interface is designed to be compatible with cloud storage services,
    making future migration to S3/GCS/Azure straightforward.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize storage service.
        
        Args:
            base_path: Base directory for file storage. Defaults to settings.FILE_STORAGE_PATH
        """
        self.base_path = Path(base_path or settings.FILE_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_file_path(self, filename: str, file_type: str = "uploads") -> Path:
        """
        Generate a unique file path with year/month/day directory structure.
        
        Args:
            filename: Original filename
            file_type: Type of file (uploads, processed, contracts, etc.)
            
        Returns:
            Path object for the file
        """
        # Get current date for directory structure
        now = datetime.utcnow()
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        
        # Create directory structure: base_path/file_type/year/month/day/
        dir_path = self.base_path / file_type / year / month / day
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        return dir_path / unique_filename
    
    def save_file(
        self,
        file_data: BinaryIO,
        filename: str,
        file_type: str = "uploads"
    ) -> str:
        """
        Save a file to storage.
        
        Args:
            file_data: Binary file data (file object)
            filename: Original filename
            file_type: Type of file for organization
            
        Returns:
            Relative path to saved file (from base_path)
        """
        file_path = self._generate_file_path(filename, file_type)
        
        # Save file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_data, f)
        
        # Return relative path from base_path
        return str(file_path.relative_to(self.base_path))
    
    def get_file_path(self, relative_path: str) -> Path:
        """
        Get absolute path for a relative storage path.
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            Absolute Path object
        """
        return self.base_path / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            True if file exists, False otherwise
        """
        return self.get_file_path(relative_path).exists()
    
    def delete_file(self, relative_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            True if deleted, False if file didn't exist
        """
        file_path = self.get_file_path(relative_path)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_file_size(self, relative_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            File size in bytes, or None if file doesn't exist
        """
        file_path = self.get_file_path(relative_path)
        if file_path.exists():
            return file_path.stat().st_size
        return None
    
    def read_file(self, relative_path: str) -> Optional[bytes]:
        """
        Read file contents.
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            File contents as bytes, or None if file doesn't exist
        """
        file_path = self.get_file_path(relative_path)
        if file_path.exists():
            with open(file_path, "rb") as f:
                return f.read()
        return None
    
    def save_text(
        self,
        text_content: str,
        filename: str,
        file_type: str = "processed"
    ) -> str:
        """
        Save text content to a file.
        
        Args:
            text_content: Text to save
            filename: Filename (will be made unique)
            file_type: Type of file for organization
            
        Returns:
            Relative path to saved file
        """
        file_path = self._generate_file_path(filename, file_type)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        return str(file_path.relative_to(self.base_path))


# Global storage service instance
storage = StorageService()
