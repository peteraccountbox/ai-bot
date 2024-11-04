import base64
import io
from typing import Optional
import aiohttp
from PyPDF2 import PdfReader

class FileExtractor:
    async def extract_text_from_url(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download file: HTTP {response.status}")
                
                file_bytes = await response.read()
                file_obj = io.BytesIO(file_bytes)
                file_type = self._detect_file_type(file_bytes)
                
                return await self.extract_text(file_obj, file_type)
            
    async def extract_text_from_base64(self, content: str, file_type: Optional[str] = None) -> str:
        try:
            file_bytes = base64.b64decode(content)
            file_obj = io.BytesIO(file_bytes)
            
            if not file_type:
                file_type = self._detect_file_type(file_bytes)
            
            return await self.extract_text(file_obj, file_type)
            
        except Exception as e:
            raise Exception(f"Failed to process file: {str(e)}")

    def _detect_file_type(self, file_bytes: bytes) -> str:
        if file_bytes.startswith(b'%PDF'):
            return 'application/pdf'
        elif file_bytes.startswith(b'PK\x03\x04'):
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return 'text/plain'

    async def extract_text(self, file_obj: io.BytesIO, file_type: str) -> str:
        if file_type == 'text/plain':
            try:
                # Read the contents of the BytesIO object and decode as UTF-8
                text_content = file_obj.getvalue().decode('utf-8')
                return text_content
            except UnicodeDecodeError:
                raise ValueError("Failed to decode file content as UTF-8. Please ensure the file contains valid text.")
            
        elif file_type == 'application/pdf':
            try:
                # Create PDF reader object
                pdf_reader = PdfReader(file_obj)
                
                # Extract text from all pages
                text_content = []
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                
                # Join all pages with newlines
                return "\n".join(text_content)
            except Exception as e:
                raise ValueError(f"Failed to extract text from PDF: {str(e)}")
            
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Currently supported formats: text/plain, application/pdf")
            