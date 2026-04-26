# RAG Knowledge Retrieval System

## Overview

The RAG (Retrieval-Augmented Generation) system enables semantic search and intelligent question answering over the PlantSC-Analyzer knowledge base.

## Features

- **Vector Embeddings**: Uses sentence-transformers for semantic search
- **ChromaDB**: Efficient vector database for similarity search
- **Document Chunking**: Splits long documents into searchable chunks
- **Multi-source**: Indexes both markdown docs and marker gene CSVs
- **Metadata Filtering**: Filter by document type (methods, markers)

---

## Installation

```bash
# Install required packages
pip install sentence-transformers chromadb
```

---

## Usage

### 1. Index Knowledge Base

First time setup - index all documents:

```bash
python agent/rag_retriever.py --knowledge_dir ./knowledge_base --index
```

Force re-index (if documents updated):

```bash
python agent/rag_retriever.py --knowledge_dir ./knowledge_base --reindex
```

### 2. Query Knowledge Base

```bash
# Simple query
python agent/rag_retriever.py --query "How to choose Harmony theta parameter?"

# Get more results
python agent/rag_retriever.py --query "SoupX usage" --n_results 10
```

### 3. Use in Python

```python
from agent.rag_retriever import RAGKnowledgeRetriever

# Initialize
retriever = RAGKnowledgeRetriever('./knowledge_base')

# Index documents (first time)
retriever.index_documents()

# Query
results = retriever.search("Arabidopsis root markers", n_results=5)

for result in results:
    print(f"Source: {result['metadata']['source']}")
    print(f"Content: {result['document'][:200]}...")
    print()

# Query with context
response = retriever.query_with_context("How to filter cells?")
print(response['answer'])
print(f"Sources: {response['sources']}")
```

---

## How It Works

### 1. Document Indexing

```
Knowledge Base Files
    ↓
Split into Chunks (500 chars)
    ↓
Generate Embeddings (sentence-transformers)
    ↓
Store in ChromaDB
    ↓
Vector Database Ready
```

**Indexed Content**:
- Method documentation (qc_methods.md, parameter_tuning.md, etc.)
- Marker gene databases (all CSV files)
- Workflow diagrams
- Literature database

### 2. Query Processing

```
User Query
    ↓
Generate Query Embedding
    ↓
Similarity Search in ChromaDB
    ↓
Retrieve Top-K Documents
    ↓
Build Context
    ↓
Generate Answer (LLM)
    ↓
Return Answer + Sources
```

---

## Integration with Agent

### Current Implementation

```python
# In plant_sc_agent.py
from agent.rag_retriever import RAGKnowledgeRetriever

class PlantSCAgent:
    def __init__(self):
        self.rag = RAGKnowledgeRetriever('./knowledge_base')
        self.rag.index_documents()
    
    def answer_question(self, question):
        response = self.rag.query_with_context(question)
        return response['answer']
```

### Future Enhancement (with LLM)

```python
import openai  # or anthropic

def _generate_answer(self, query: str, context: str) -> str:
    """Generate answer using LLM"""
    prompt = f"""Based on the following context from the PlantSC-Analyzer knowledge base, 
answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

---

## Example Queries

### Method Questions

```bash
# QC methods
python agent/rag_retriever.py --query "When should I use SoupX?"
python agent/rag_retriever.py --query "How to set mitochondrial threshold?"

# Parameter tuning
python agent/rag_retriever.py --query "How many HVGs should I select?"
python agent/rag_retriever.py --query "Harmony vs scVI comparison"

# Clustering
python agent/rag_retriever.py --query "How to choose resolution parameter?"
```

### Marker Gene Questions

```bash
# Find markers
python agent/rag_retriever.py --query "Arabidopsis xylem markers"
python agent/rag_retriever.py --query "VND7 gene function"

# Cell type questions
python agent/rag_retriever.py --query "endodermis marker genes"
```

---

## Performance

### Indexing Speed

| Documents | Time | Vector DB Size |
|-----------|------|----------------|
| 100 chunks | ~5s | ~2 MB |
| 500 chunks | ~20s | ~10 MB |
| 1000 chunks | ~40s | ~20 MB |

### Query Speed

- **Embedding generation**: ~50ms
- **Vector search**: ~10ms
- **Total**: ~60ms per query

---

## Configuration

### Embedding Model

Default: `all-MiniLM-L6-v2` (fast, good quality)

Alternatives:
- `all-mpnet-base-v2` (better quality, slower)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

```python
retriever = RAGKnowledgeRetriever(
    './knowledge_base',
    model_name='all-mpnet-base-v2'
)
```

### Chunk Size

Default: 500 characters

Adjust in `_split_into_chunks()`:
```python
chunks = self._split_into_chunks(text, max_length=1000)
```

---

## Troubleshooting

### Issue: "No documents found to index"

**Solution**: Check knowledge_base directory structure
```bash
ls -R knowledge_base/
```

### Issue: Slow indexing

**Solution**: Use smaller embedding model or reduce chunk size

### Issue: Poor search results

**Solution**: 
1. Try different embedding model
2. Increase n_results
3. Re-index with `--reindex`

---

## Future Enhancements

1. **LLM Integration**
   - OpenAI GPT-4
   - Anthropic Claude
   - Local LLMs (Llama, Mistral)

2. **Advanced Chunking**
   - Semantic chunking
   - Overlap between chunks
   - Hierarchical chunking

3. **Multi-modal**
   - Index images (UMAP plots, diagrams)
   - Index tables
   - Index code snippets

4. **Query Enhancement**
   - Query expansion
   - Relevance feedback
   - Multi-hop reasoning

---

## References

- Sentence Transformers: https://www.sbert.net/
- ChromaDB: https://www.trychroma.com/
- RAG: https://arxiv.org/abs/2005.11401
