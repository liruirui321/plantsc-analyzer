# scPlantDB 和 LLM 注释使用指南

## 概览

PlantSC-Analyzer 现在支持两种高级注释方法：
1. **scPlantDB 集成** - 自动获取 17 个物种的 Marker 基因
2. **LLM 辅助注释** - 使用 GPT-4/Claude 智能推断细胞类型

---

## 1. scPlantDB 集成

### 支持的物种

scPlantDB 支持 17 个植物物种：

| 物种 | 学名 | 本地 Marker |
|------|------|------------|
| arabidopsis | *Arabidopsis thaliana* | ✅ |
| rice | *Oryza sativa* | ❌ |
| maize | *Zea mays* | ❌ |
| tomato | *Solanum lycopersicum* | ❌ |
| soybean | *Glycine max* | ❌ |
| poplar | *Populus trichocarpa* | ❌ |
| cotton | *Gossypium hirsutum* | ❌ |
| wheat | *Triticum aestivum* | ❌ |
| barley | *Hordeum vulgare* | ❌ |
| sorghum | *Sorghum bicolor* | ❌ |
| tobacco | *Nicotiana tabacum* | ❌ |
| medicago | *Medicago truncatula* | ❌ |
| brachypodium | *Brachypodium distachyon* | ❌ |
| setaria | *Setaria viridis* | ❌ |
| lotus | *Lotus japonicus* | ❌ |
| pepper | *Capsicum annuum* | ❌ |
| cucumber | *Cucumis sativus* | ❌ |

### 使用方法

#### 列出支持的物种

```bash
python agent/scplantdb_client.py --list_species
```

#### 获取 Marker 基因

```bash
# 获取拟南芥根的 Marker
python agent/scplantdb_client.py --species arabidopsis --tissue root

# 获取水稻所有 Marker
python agent/scplantdb_client.py --species rice

# 获取特定细胞类型
python agent/scplantdb_client.py --species arabidopsis --tissue root --cell_type xylem
```

#### 同步到本地

```bash
# 同步水稻 Marker 到本地
python agent/scplantdb_client.py --species rice --sync --output ./knowledge_base/markers/

# 同步所有物种
for species in arabidopsis rice maize; do
    python agent/scplantdb_client.py --species $species --sync --output ./knowledge_base/markers/
done
```

### Python API

```python
from agent.scplantdb_client import scPlantDBClient

# 初始化
client = scPlantDBClient()

# 列出物种
species_list = client.list_species()
print(species_list)

# 获取 Marker
markers = client.get_marker_genes('arabidopsis', tissue='root')
print(f"Found {len(markers)} markers")

# 获取物种信息
info = client.get_species_info('rice')
print(info)
```

### 集成到分析流程

```python
import scanpy as sc
from agent.scplantdb_client import scPlantDBClient

# 加载数据
adata = sc.read_h5ad('clustered.h5ad')

# 获取 Marker
client = scPlantDBClient()
markers = client.get_marker_genes('arabidopsis', tissue='root')

# 使用 Marker 注释
# ... (与现有注释流程相同)
```

---

## 2. LLM 辅助注释

### 支持的 LLM

| Provider | 模型 | 推荐用途 |
|----------|------|---------|
| OpenAI | gpt-4 | 最准确（推荐） |
| OpenAI | gpt-3.5-turbo | 快速、便宜 |
| Anthropic | claude-3-opus | 高质量 |
| Anthropic | claude-3-sonnet | 平衡 |

### 安装依赖

```bash
# OpenAI
pip install openai

# Anthropic
pip install anthropic
```

### 设置 API Key

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 使用方法

#### 命令行使用

```bash
# 使用 GPT-4 注释
python scripts/05_annotate/llm_annotate.py \
    --input clustered.h5ad \
    --output llm_annotations.csv \
    --species "Arabidopsis thaliana" \
    --tissue root \
    --model gpt-4 \
    --provider openai

# 使用 Claude
python scripts/05_annotate/llm_annotate.py \
    --input clustered.h5ad \
    --output llm_annotations.csv \
    --species "Arabidopsis thaliana" \
    --tissue root \
    --model claude-3-opus-20240229 \
    --provider anthropic
```

#### Nextflow 集成

在 `nextflow.config` 中启用：

```groovy
params {
    annotation {
        use_llm = true
        llm_provider = 'openai'
        llm_model = 'gpt-4'
        llm_n_genes = 20
    }
}
```

运行流程：

```bash
export OPENAI_API_KEY="sk-..."

nextflow run workflows/main.nf \
    --input data.h5ad \
    --species "Arabidopsis thaliana" \
    --tissue root
```

#### Python API

```python
from scripts.llm_annotate import LLMAnnotator
import scanpy as sc

# 加载数据
adata = sc.read_h5ad('clustered.h5ad')

# 初始化 LLM 注释器
annotator = LLMAnnotator(
    model='gpt-4',
    provider='openai'
)

# 注释单个 cluster
marker_genes = ['VND7', 'VND6', 'IRX3', 'IRX5']
result = annotator.annotate_cluster(
    marker_genes=marker_genes,
    species='Arabidopsis thaliana',
    tissue='root'
)

print(f"Cell Type: {result['cell_type']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")

# 注释所有 clusters
annotations = annotator.annotate_all_clusters(
    adata,
    cluster_key='leiden',
    n_genes=20,
    species='Arabidopsis thaliana',
    tissue='root'
)

print(annotations)
```

### 输出格式

LLM 注释输出 CSV 包含：

| 列 | 说明 |
|----|------|
| cluster | Cluster ID |
| cell_type | 推断的细胞类型 |
| confidence | 置信度 (0-1) |
| reasoning | LLM 的推理过程 |
| marker_genes | 使用的 Marker 基因 |

示例：

```csv
cluster,cell_type,confidence,reasoning,marker_genes
0,Xylem vessel,0.95,"High expression of VND7, VND6, IRX3 indicates xylem vessel differentiation",VND7,VND6,IRX3,IRX5
1,Phloem,0.88,"APL, SUC2, CALS7 are phloem-specific markers",APL,SUC2,CALS7
2,Endodermis,0.92,"SCR, SHR, CASP1 are endodermis markers",SCR,SHR,CASP1
```

---

## 3. 混合注释策略

推荐使用混合策略：**传统 Marker 匹配 + LLM 验证**

### 工作流程

```bash
# Step 1: 传统 Marker 匹配
python scripts/05_annotate/annotate.py \
    --input clustered.h5ad \
    --markers knowledge_base/markers/arabidopsis/root_markers.csv \
    --output annotated_traditional.h5ad

# Step 2: LLM 辅助注释
python scripts/05_annotate/llm_annotate.py \
    --input clustered.h5ad \
    --output llm_annotations.csv \
    --species "Arabidopsis thaliana" \
    --tissue root

# Step 3: 比较和验证
python scripts/05_annotate/compare_annotations.py \
    --traditional annotated_traditional.h5ad \
    --llm llm_annotations.csv \
    --output final_annotations.csv
```

### 决策规则

| 情况 | 决策 |
|------|------|
| 两者一致 | 采用该注释 |
| 两者不一致，LLM 置信度 > 0.9 | 采用 LLM |
| 两者不一致，LLM 置信度 < 0.7 | 采用传统方法 |
| 两者不一致，0.7 ≤ 置信度 ≤ 0.9 | 标记为需要人工检查 |

---

## 4. 成本估算

### LLM API 成本

**GPT-4** (截至 2024):
- Input: $0.03 / 1K tokens
- Output: $0.06 / 1K tokens
- 每个 cluster: ~500 tokens
- 10 个 clusters: ~$0.30

**GPT-3.5-turbo**:
- Input: $0.0015 / 1K tokens
- Output: $0.002 / 1K tokens
- 10 个 clusters: ~$0.02

**Claude-3-Opus**:
- Input: $0.015 / 1K tokens
- Output: $0.075 / 1K tokens
- 10 个 clusters: ~$0.25

### 优化建议

1. **先用传统方法** - 只对低置信度 cluster 使用 LLM
2. **使用 GPT-3.5** - 对于简单数据集
3. **批量处理** - 减少 API 调用次数
4. **缓存结果** - 避免重复注释

---

## 5. 最佳实践

### scPlantDB

1. ✅ **优先使用本地 Marker** - 速度快，无网络依赖
2. ✅ **定期同步** - 每月同步一次 scPlantDB
3. ✅ **验证 Marker** - 检查 Marker 基因在数据中的表达
4. ✅ **跨物种比较** - 使用同源基因映射

### LLM 注释

1. ✅ **提供上下文** - 指定物种和组织类型
2. ✅ **使用足够的 Marker** - 至少 15-20 个基因
3. ✅ **设置合理阈值** - 置信度 < 0.7 需要人工检查
4. ✅ **交叉验证** - 与传统方法比较
5. ✅ **保存推理过程** - 便于后续审查

---

## 6. 故障排除

### scPlantDB 问题

**Q: 无法连接 scPlantDB**
```bash
# 使用本地 Marker
python agent/scplantdb_client.py --species arabidopsis --tissue root
# 会自动 fallback 到本地文件
```

**Q: 物种不支持**
```bash
# 检查支持的物种
python agent/scplantdb_client.py --list_species

# 使用最接近的物种或自定义 Marker
```

### LLM 问题

**Q: API Key 错误**
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 或在命令行指定
python scripts/05_annotate/llm_annotate.py --api_key "sk-..."
```

**Q: 速率限制**
```python
# 添加延迟
import time
for cluster in clusters:
    result = annotator.annotate_cluster(...)
    time.sleep(1)  # 1 秒延迟
```

**Q: 成本过高**
```bash
# 使用 GPT-3.5
--model gpt-3.5-turbo

# 或只注释不确定的 cluster
--confidence_threshold 0.8
```

---

## 7. 示例

完整示例见：
- `examples/scplantdb_example.py`
- `examples/llm_annotation_example.py`
- `examples/hybrid_annotation_example.py`

---

**Sources**:
- [scPlantDB Help](https://biobigdata.nju.edu.cn/scplantdb/_helpmenu/index.html)
- [GPT-4 Annotation Paper](https://www.nature.com/articles/s41592-024-02235-4)
