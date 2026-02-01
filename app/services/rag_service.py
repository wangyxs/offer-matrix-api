import chromadb
from chromadb.config import Settings
import PyPDF2
from docx import Document
import os
from typing import List, Dict
from app.core.config import settings
from zhipuai import ZhipuAI

class RAGService:
    def __init__(self):
        # Initialize ZhipuAI
        self.zhipu_client = ZhipuAI(api_key=settings.ZHIPUAI_API_KEY)
        
        # Initialize ChromaDB (Persistent)
        chroma_path = str(settings.DATA_DIR / "chroma_db_v2")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(name="role_documents")

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from PDF or Docx"""
        text = ""
        file_path = str(file_path)
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            elif file_path.endswith('.docx'):
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                # Fallback for plain text or unknown
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
        return text

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from ZhipuAI"""
        try:
            response = self.zhipu_client.embeddings.create(
                model="embedding-2", # Zhipu's latest embedding model
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Zhipu Embedding Error: {e}")
            return []

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Simple text chunking"""
        chunks = []
        if not text:
            return chunks
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks

    def add_document(self, doc_id: int, role_id: int, file_path: str, file_type: str):
        """Process, Embed, and Index document"""
        text = self.extract_text(file_path, file_type)
        if not text:
            return
        
        chunks = self.chunk_text(text)
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            vector = self.get_embedding(chunk)
            if not vector:
                continue
            
            ids.append(f"doc_{doc_id}_chunk_{i}")
            embeddings.append(vector)
            metadatas.append({
                "doc_id": doc_id,
                "role_id": role_id,
                "type": file_type # RESUME or MATERIAL
            })
            documents.append(chunk)
            
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            print(f"Indexed document {doc_id} with {len(ids)} chunks.")

    def delete_document(self, doc_id: int):
        """Delete all chunks for a document"""
        try:
            self.collection.delete(
                where={"doc_id": doc_id}
            )
            print(f"Deleted index for document {doc_id}")
        except Exception as e:
            print(f"Error deleting document index: {e}")

    def search_context(self, query: str, role_id: int, top_k: int = 3) -> str:
        """Retrieve relevant context"""
        vector = self.get_embedding(query)
        if not vector:
            return ""
            
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            where={"role_id": role_id}
        )
        
        context = ""
        if results['documents']:
            # combine all retrieved chunks
            for doc_list in results['documents']:
                for doc in doc_list:
                    context += doc + "\n\n"
        
        return context

rag_service = RAGService()
