# 文献下载和 RAG 系统使用指南

## 快速开始

### 1. 下载文献

```bash
# 下载单篇文献（通过 PMID）
python scripts/utils/download_papers.py --pmid 33367645 --output knowledge_base/papers/methods/

# 下载单篇文献（通过 DOI）
python scripts/utils/download_papers.py --doi 10.1093/gigascience/giaa151 --output knowledge_base/papers/methods/

# 批量下载（从列表文件）
python scripts/utils/download_papers.py \
    --list knowledge_base/papers/download_list.txt \
    --output knowledge_base/papers/ \
    --delay 10
```

**注意**:
- 使用 Sci-Hub 下载需要遵守版权法
- 建议设置 `--delay 10` 避免被限流
- 如果某个镜像失败，可以用 `--mirror` 指定其他镜像

### 2. 索引知识库（RAG）

```bash
# 首次索引
python agent/rag_retriever.py --knowledge_dir ./knowledge_base --index

# 更新索引（文献下载后）
python agent/rag_retriever.py --knowledge_dir ./knowledge_base --reindex
```

### 3. 查询知识库

```bash
# 查询方法
python agent/rag_retriever.py --query "如何使用 SoupX？"

# 查询 Marker 基因
python agent/rag_retriever.py --query "拟南芥木质部 Marker 基因"

# 查询参数
python agent/rag_retriever.py --query "Harmony theta 参数如何选择？"
```

---

## 完整工作流

### 步骤 1: 准备文献列表

编辑 `knowledge_base/papers/download_list.txt`:

```
# 添加 PMID（每行一个）
33367645  # SoupX paper
30954476  # Scrublet paper
31740822  # Harmony paper
```

### 步骤 2: 批量下载

```bash
cd plantsc-analyzer

# 下载所有文献
python scripts/utils/download_papers.py \
    --list knowledge_base/papers/download_list.txt \
    --output knowledge_base/papers/ \
    --delay 10

# 查看下载结果
ls -lh knowledge_base/papers/
```

**预期输出**:
```
knowledge_base/papers/
├── 33367645.pdf  # SoupX
├── 30954476.pdf  # Scrublet
├── 31740822.pdf  # Harmony
└── ...
```

### 步骤 3: 整理文献

```bash
# 按类别整理
mkdir -p knowledge_base/papers/methods
mkdir -p knowledge_base/papers/arabidopsis
mkdir -p knowledge_base/papers/rice

# 移动文件
mv knowledge_base/papers/33367645.pdf knowledge_base/papers/methods/Young_2020_SoupX.pdf
mv knowledge_base/papers/31178400.pdf knowledge_base/papers/arabidopsis/Denyer_2019_Root.pdf
```

### 步骤 4: 索引知识库

```bash
# 索引所有文档（包括新下载的文献）
python agent/rag_retriever.py --knowledge_dir ./knowledge_base --reindex
```

**预期输出**:
```
[INFO] Indexing documents...
[INFO] Adding 523 documents to vector database...
[SUCCESS] Indexed 523 documents
```

### 步骤 5: 测试查询

```bash
# 测试查询
python agent/rag_retriever.py --query "SoupX 推荐参数"
```

**预期输出**:
```
============================================================
Query: SoupX 推荐参数
============================================================

Context:
------------------------------------------------------------
[Source: methods/qc_methods.md]
SoupX 关键参数:
- tfidfMin: 1.0 (推荐)
- forceAccept: TRUE
...

Sources:
------------------------------------------------------------
  - methods/qc_methods.md
  - papers/LITERATURE_DATABASE.md
```

---

## 集成到 Agent

### 修改 plant_sc_agent.py

```python
from agent.rag_retriever import RAGKnowledgeRetriever

class PlantSCAgent:
    def __init__(self, knowledge_dir='./knowledge_base'):
        # 初始化 RAG
        self.rag = RAGKnowledgeRetriever(knowledge_dir)
        self.rag.index_documents()
    
    def get_parameter_recommendation(self, data_characteristics):
        """使用 RAG 获取参数推荐"""
        query = f"推荐参数：细胞数 {data_characteristics['n_cells']}, "
        query += f"批次数 {data_characteristics['n_batches']}"
        
        response = self.rag.query_with_context(query, n_results=3)
        return response
    
    def answer_user_question(self, question):
        """回答用户问题"""
        response = self.rag.query_with_context(question, n_results=5)
        return response['answer']
```

---

## 常见问题

### Q1: Sci-Hub 镜像无法访问？

**A**: 更换镜像

```bash
python scripts/utils/download_papers.py \
    --pmid 33367645 \
    --mirror https://sci-hub.st
```

可用镜像：
- https://sci-hub.se
- https://sci-hub.st
- https://sci-hub.ru

### Q2: 下载速度慢？

**A**: 
1. 增加延迟：`--delay 15`
2. 分批下载
3. 使用代理

### Q3: RAG 查询结果不准确？

**A**: 
1. 重新索引：`--reindex`
2. 增加结果数：`--n_results 10`
3. 检查知识库内容是否完整

### Q4: 如何添加自己的文献？

**A**: 
1. 手动下载 PDF 到 `knowledge_base/papers/`
2. 更新 `LITERATURE_DATABASE.md`
3. 重新索引：`python agent/rag_retriever.py --reindex`

---

## 维护

### 定期更新

```bash
# 每月更新一次
cd plantsc-analyzer

# 1. 添加新文献到 download_list.txt
echo "12345678  # New paper" >> knowledge_base/papers/download_list.txt

# 2. 下载新文献
python scripts/utils/download_papers.py \
    --list knowledge_base/papers/download_list.txt \
    --output knowledge_base/papers/

# 3. 重新索引
python agent/rag_retriever.py --reindex

# 4. 提交到 Git
git add knowledge_base/papers/
git commit -m "Add new literature"
git push
```

---

## 性能优化

### 索引优化

```python
# 使用更快的嵌入模型
retriever = RAGKnowledgeRetriever(
    './knowledge_base',
    model_name='all-MiniLM-L6-v2'  # 快速
)

# 或使用更准确的模型
retriever = RAGKnowledgeRetriever(
    './knowledge_base',
    model_name='all-mpnet-base-v2'  # 准确
)
```

### 查询优化

```python
# 只搜索特定类型
results = retriever.search(
    "SoupX parameters",
    n_results=5,
    filter_type="method_doc"  # 只搜索方法文档
)
```

---

## 下一步

1. ✅ 下载关键文献（15+ 篇）
2. ✅ 索引知识库
3. ✅ 测试 RAG 查询
4. 🔄 集成到 Agent
5. 🔄 添加 LLM 生成（OpenAI/Claude）
6. 🔄 优化检索质量

---

**现在你可以开始下载文献并使用 RAG 系统了！** 🎉
