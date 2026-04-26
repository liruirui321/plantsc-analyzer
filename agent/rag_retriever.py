#!/usr/bin/env python3
"""
RAG Knowledge Retriever

Implements Retrieval-Augmented Generation for knowledge base queries.
Uses vector embeddings for semantic search and LLM for answer generation.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("[ERROR] Required packages not installed. Run:")
    print("  pip install sentence-transformers chromadb")
    sys.exit(1)


class RAGKnowledgeRetriever:
    """RAG-based knowledge retrieval system"""

    def __init__(self, knowledge_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG retriever

        Args:
            knowledge_dir: Path to knowledge base directory
            model_name: Sentence transformer model name
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.model = SentenceTransformer(model_name)

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.knowledge_dir / "embeddings" / "vector_db")
        ))

        self.collection = None

    def index_documents(self, force_reindex: bool = False):
        """
        Index all documents in knowledge base

        Args:
            force_reindex: Force re-indexing even if collection exists
        """
        collection_name = "plantsc_knowledge"

        # Check if collection exists
        try:
            if not force_reindex:
                self.collection = self.chroma_client.get_collection(collection_name)
                print(f"[INFO] Loaded existing collection with {self.collection.count()} documents")
                return
        except:
            pass

        # Create new collection
        if self.collection:
            self.chroma_client.delete_collection(collection_name)

        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "PlantSC-Analyzer knowledge base"}
        )

        print("[INFO] Indexing documents...")

        documents = []
        metadatas = []
        ids = []

        # Index markdown files
        for md_file in self.knowledge_dir.rglob("*.md"):
            if md_file.name in ['README.md', 'LITERATURE_DATABASE.md']:
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Split into chunks (simple paragraph-based splitting)
                chunks = self._split_into_chunks(content)

                for i, chunk in enumerate(chunks):
                    doc_id = f"{md_file.stem}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(md_file.relative_to(self.knowledge_dir)),
                        "type": "method_doc",
                        "chunk_id": i
                    })
                    ids.append(doc_id)

            except Exception as e:
                print(f"[WARNING] Failed to index {md_file}: {e}")

        # Index marker files
        for csv_file in self.knowledge_dir.rglob("*_markers.csv"):
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)

                # Create searchable text from markers
                for idx, row in df.iterrows():
                    text = f"Gene: {row['gene_symbol']}, Cell type: {row['cell_type']}, "
                    text += f"Confidence: {row['confidence']}"
                    if 'description' in row and pd.notna(row['description']):
                        text += f", Description: {row['description']}"

                    doc_id = f"marker_{csv_file.stem}_{idx}"
                    documents.append(text)
                    metadatas.append({
                        "source": str(csv_file.relative_to(self.knowledge_dir)),
                        "type": "marker",
                        "gene": row['gene_symbol'],
                        "cell_type": row['cell_type']
                    })
                    ids.append(doc_id)

            except Exception as e:
                print(f"[WARNING] Failed to index {csv_file}: {e}")

        # Add to collection
        if documents:
            print(f"[INFO] Adding {len(documents)} documents to vector database...")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[SUCCESS] Indexed {len(documents)} documents")
        else:
            print("[WARNING] No documents found to index")

    def _split_into_chunks(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks"""
        # Simple paragraph-based splitting
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) < max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def search(self, query: str, n_results: int = 5, filter_type: Optional[str] = None) -> List[Dict]:
        """
        Search knowledge base

        Args:
            query: Search query
            n_results: Number of results to return
            filter_type: Filter by document type (method_doc, marker)

        Returns:
            List of search results with documents and metadata
        """
        if self.collection is None:
            self.index_documents()

        where_filter = {"type": filter_type} if filter_type else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted_results

    def query_with_context(self, query: str, n_results: int = 3) -> Dict:
        """
        Query with retrieved context

        Args:
            query: User query
            n_results: Number of context documents to retrieve

        Returns:
            Dict with query, context, and answer
        """
        # Retrieve relevant documents
        results = self.search(query, n_results=n_results)

        # Build context
        context = "\n\n".join([
            f"[Source: {r['metadata']['source']}]\n{r['document']}"
            for r in results
        ])

        # For now, return context (LLM integration would go here)
        return {
            'query': query,
            'context': context,
            'sources': [r['metadata']['source'] for r in results],
            'answer': self._generate_answer(query, context)
        }

    def _generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer from context

        Note: This is a simple template-based answer.
        In production, integrate with LLM (OpenAI, Claude, etc.)
        """
        # Simple template-based answer
        answer = f"Based on the knowledge base:\n\n{context}\n\n"
        answer += f"This information is relevant to your query: '{query}'"

        return answer


def main():
    parser = argparse.ArgumentParser(description='RAG Knowledge Retriever')
    parser.add_argument('--knowledge_dir', default='./knowledge_base',
                        help='Knowledge base directory')
    parser.add_argument('--index', action='store_true',
                        help='Index documents')
    parser.add_argument('--reindex', action='store_true',
                        help='Force re-index')
    parser.add_argument('--query', help='Query string')
    parser.add_argument('--n_results', type=int, default=5,
                        help='Number of results')

    args = parser.parse_args()

    retriever = RAGKnowledgeRetriever(args.knowledge_dir)

    if args.index or args.reindex:
        retriever.index_documents(force_reindex=args.reindex)

    if args.query:
        print(f"\n{'='*60}")
        print(f"Query: {args.query}")
        print(f"{'='*60}\n")

        result = retriever.query_with_context(args.query, n_results=args.n_results)

        print("Context:")
        print("-" * 60)
        print(result['context'])
        print()

        print("Sources:")
        print("-" * 60)
        for source in result['sources']:
            print(f"  - {source}")
        print()


if __name__ == '__main__':
    main()
