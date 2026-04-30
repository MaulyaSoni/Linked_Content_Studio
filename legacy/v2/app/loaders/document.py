"""
Document Loader - File Upload Processing
========================================
Handles uploaded documents and text files for RAG.
"""

import os
import logging
from typing import Optional, List
from .base import BaseLoader


logger = logging.getLogger(__name__)


class DocumentLoader(BaseLoader):
    """Document loader for various file formats."""
    
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.html', '.css', 
        '.json', '.xml', '.csv', '.log', '.yaml', '.yml'
    }
    
    def load(self, file_path: str) -> Optional[str]:
        """Load content from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            File content as string, or None if failed
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            if not self.is_supported(file_path):
                logger.error(f"Unsupported file type: {file_path}")
                return None
            
            logger.info(f"📄 Loading document: {file_path}")
            
            # Determine file type and load accordingly
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.txt':
                return self._load_text_file(file_path)
            elif ext == '.md':
                return self._load_markdown_file(file_path)
            elif ext in ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml']:
                return self._load_code_file(file_path)
            elif ext == '.csv':
                return self._load_csv_file(file_path)
            else:
                # Default to text loading
                return self._load_text_file(file_path)
                
        except Exception as e:
            logger.error(f"❌ Document loading failed: {e}")
            return None
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file type is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def load_from_bytes(self, file_bytes: bytes, filename: str) -> Optional[str]:
        """Load content from file bytes (for Streamlit uploads).
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            File content as string, or None if failed
        """
        try:
            # Check file extension
            if not self.is_supported(filename):
                logger.error(f"Unsupported file type: {filename}")
                return None
            
            # Decode bytes to string
            try:
                content = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Try different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        content = file_bytes.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.error(f"Could not decode file: {filename}")
                    return None
            
            logger.info(f"✅ Loaded {len(content)} characters from {filename}")
            return content
            
        except Exception as e:
            logger.error(f"❌ Bytes loading failed: {e}")
            return None
    
    def _load_text_file(self, file_path: str) -> Optional[str]:
        """Load plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"✅ Text file loaded: {len(content)} characters")
            return content
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"✅ Text file loaded ({encoding}): {len(content)} characters")
                    return content
                except UnicodeDecodeError:
                    continue
            logger.error(f"Could not decode text file: {file_path}")
            return None
    
    def _load_markdown_file(self, file_path: str) -> Optional[str]:
        """Load markdown file with special handling."""
        content = self._load_text_file(file_path)
        if content:
            # Extract headings for better structure
            lines = content.split('\n')
            structured_content = []
            
            for line in lines:
                if line.startswith('#'):
                    # Add emphasis to headings
                    structured_content.append(f"HEADING: {line}")
                else:
                    structured_content.append(line)
            
            return '\n'.join(structured_content)
        return None
    
    def _load_code_file(self, file_path: str) -> Optional[str]:
        """Load source code file with comments extraction."""
        content = self._load_text_file(file_path)
        if content:
            # For code files, focus on comments and structure
            lines = content.split('\n')
            extracted_content = []
            
            for line in lines:
                stripped = line.strip()
                # Extract comments from various languages
                if (stripped.startswith('#') or 
                    stripped.startswith('//') or 
                    stripped.startswith('/*') or
                    stripped.startswith('*') or
                    stripped.startswith('"""') or
                    stripped.startswith("'''")):
                    extracted_content.append(f"COMMENT: {stripped}")
                elif len(stripped) < 100:  # Include short lines (function defs, etc.)
                    extracted_content.append(line)
            
            return '\n'.join(extracted_content)
        return None
    
    def _load_csv_file(self, file_path: str) -> Optional[str]:
        """Load CSV file and convert to text."""
        try:
            import csv
            
            content_parts = []
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for i, row in enumerate(csv_reader):
                    if i < 10:  # Limit to first 10 rows
                        content_parts.append(f"Row {i+1}: {', '.join(row)}")
                    else:
                        break
            
            content = '\n'.join(content_parts)
            logger.info(f"✅ CSV loaded: {len(content_parts)} rows")
            return content
            
        except Exception as e:
            logger.error(f"CSV loading failed: {e}")
            # Fallback to text loading
            return self._load_text_file(file_path)
    
    def get_file_info(self, file_path: str) -> dict:
        """Get information about the file."""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'extension': os.path.splitext(file_path)[1].lower(),
                'supported': self.is_supported(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {
                'name': file_path,
                'size': 0,
                'extension': '',
                'supported': False
            }
