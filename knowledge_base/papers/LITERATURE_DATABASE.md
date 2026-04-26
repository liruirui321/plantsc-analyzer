# 植物单细胞文献库

## 概览

本文献库收集了植物单细胞 RNA-seq 相关的重要文献，用于：
1. Agent 学习和决策
2. Marker 基因验证
3. 方法学参考
4. 用户查询

---

## 文献分类

### 1. 方法学文献

#### 1.1 质控方法

**SoupX - 环境 RNA 去除**
- **标题**: SoupX removes ambient RNA contamination from droplet-based single-cell RNA sequencing data
- **作者**: Young MD, Behjati S
- **期刊**: GigaScience, 2020
- **PMID**: 33367645
- **DOI**: 10.1093/gigascience/giaa151
- **关键点**:
  - 估计环境 RNA 污染率 rho
  - 使用 TF-IDF 识别污染基因
  - 适用于所有 droplet-based 平台
- **文件**: `papers/methods/Young_2020_SoupX.pdf`

**Scrublet - Doublet 检测**
- **标题**: Scrublet: Computational Identification of Cell Doublets in Single-Cell Transcriptomic Data
- **作者**: Wolock SL, Lopez R, Klein AM
- **期刊**: Cell Systems, 2019
- **PMID**: 30954476
- **DOI**: 10.1016/j.cels.2018.11.005
- **关键点**:
  - 模拟 doublets 进行检测
  - 自动阈值选择
  - 预期 doublet 率计算
- **文件**: `papers/methods/Wolock_2019_Scrublet.pdf`

#### 1.2 批次整合

**Harmony**
- **标题**: Fast, sensitive and accurate integration of single-cell data with Harmony
- **作者**: Korsunsky I, et al.
- **期刊**: Nature Methods, 2019
- **PMID**: 31740822
- **DOI**: 10.1038/s41592-019-0619-0
- **关键点**:
  - 快速批次校正算法
  - 保留生物学变异
  - 适用于大数据集
- **文件**: `papers/methods/Korsunsky_2019_Harmony.pdf`

**scVI**
- **标题**: Deep generative modeling for single-cell transcriptomics
- **作者**: Lopez R, et al.
- **期刊**: Nature Methods, 2018
- **PMID**: 30504886
- **DOI**: 10.1038/s41592-018-0229-2
- **关键点**:
  - 变分自编码器
  - 深度学习批次校正
  - 需要 GPU 加速
- **文件**: `papers/methods/Lopez_2018_scVI.pdf`

#### 1.3 聚类方法

**Leiden 算法**
- **标题**: From Louvain to Leiden: guaranteeing well-connected communities
- **作者**: Traag VA, et al.
- **期刊**: Scientific Reports, 2019
- **PMID**: 30914743
- **DOI**: 10.1038/s41598-019-41695-z
- **关键点**:
  - 改进的 Louvain 算法
  - 保证连通性
  - 更好的聚类质量
- **文件**: `papers/methods/Traag_2019_Leiden.pdf`

#### 1.4 综述

**单细胞最佳实践**
- **标题**: Current best practices in single-cell RNA-seq analysis: a tutorial
- **作者**: Luecken MD, Theis FJ
- **期刊**: Molecular Systems Biology, 2019
- **PMID**: 31217225
- **DOI**: 10.15252/msb.20188746
- **关键点**:
  - 完整的分析流程
  - 参数选择指南
  - 常见问题解决
- **文件**: `papers/reviews/Luecken_2019_BestPractices.pdf`

---

### 2. 植物单细胞文献

#### 2.1 拟南芥根

**拟南芥根单细胞图谱**
- **标题**: A Single-Cell RNA Sequencing Atlas of the Arabidopsis Root Reveals Cell Type-Specific Developmental Pathways
- **作者**: Denyer T, et al.
- **期刊**: Developmental Cell, 2019
- **PMID**: 31178400
- **DOI**: 10.1016/j.devcel.2019.04.045
- **关键点**:
  - 拟南芥根完整细胞图谱
  - 各细胞类型 Marker 基因
  - 发育轨迹分析
- **Marker 基因**: 已整合到 `markers/arabidopsis/root_markers.csv`
- **文件**: `papers/arabidopsis/Denyer_2019_Root_Atlas.pdf`

**根尖干细胞龛**
- **标题**: A spatiotemporal organ-scale atlas of the Arabidopsis root
- **作者**: Shahan R, et al.
- **期刊**: Cell, 2022
- **PMID**: 35063072
- **DOI**: 10.1016/j.cell.2021.12.041
- **关键点**:
  - 时空分辨的根发育图谱
  - 干细胞龛动态
  - WOX5, PLT 等关键基因
- **Marker 基因**: 已整合
- **文件**: `papers/arabidopsis/Shahan_2022_Root_Spatiotemporal.pdf`

#### 2.2 拟南芥叶

**叶发育单细胞图谱**
- **标题**: A single-cell transcriptome atlas of the developing Arabidopsis leaf
- **作者**: Kim JY, et al.
- **期刊**: Nature Plants, 2021
- **PMID**: 33619379
- **DOI**: 10.1038/s41477-021-00877-0
- **关键点**:
  - 叶发育各阶段细胞类型
  - 气孔发育轨迹
  - 叶肉细胞分化
- **Marker 基因**: 已整合到 `markers/arabidopsis/leaf_markers.csv`
- **文件**: `papers/arabidopsis/Kim_2021_Leaf_Atlas.pdf`

#### 2.3 拟南芥花

**花器官发育**
- **标题**: Single-cell analysis of the Arabidopsis flower reveals cell type-specific transcriptional programs
- **作者**: Xu X, et al.
- **期刊**: Plant Cell, 2021
- **PMID**: 33793920
- **DOI**: 10.1093/plcell/koab065
- **关键点**:
  - 花器官各细胞类型
  - 雄蕊和心皮发育
  - ABC 模型验证
- **Marker 基因**: 已整合到 `markers/arabidopsis/flower_markers.csv`
- **文件**: `papers/arabidopsis/Xu_2021_Flower_Atlas.pdf`

#### 2.4 拟南芥木质部

**木质部分化**
- **标题**: Single-cell transcriptomics reveals the developmental trajectory of xylem in Arabidopsis
- **作者**: Zhang T, et al.
- **期刊**: Nature Plants, 2019
- **PMID**: 31285559
- **DOI**: 10.1038/s41477-019-0465-3
- **关键点**:
  - 木质部细胞分化轨迹
  - VND6/VND7 调控网络
  - 导管和纤维细胞分化
- **Marker 基因**: 已整合到 `markers/arabidopsis/xylem_markers.csv`
- **文件**: `papers/arabidopsis/Zhang_2019_Xylem_Trajectory.pdf`

---

### 3. 其他植物物种

#### 3.1 水稻

**水稻根单细胞图谱**
- **标题**: A single-cell RNA sequencing atlas of rice roots reveals developmental trajectories
- **作者**: Liu Q, et al.
- **期刊**: Molecular Plant, 2021
- **PMID**: 33548506
- **DOI**: 10.1016/j.molp.2021.01.008
- **关键点**:
  - 水稻根细胞类型
  - 与拟南芥的比较
  - 单子叶特异性
- **文件**: `papers/rice/Liu_2021_Rice_Root.pdf`

#### 3.2 玉米

**玉米根尖**
- **标题**: Single-cell transcriptome atlas of the maize root apex
- **作者**: Ortiz-Ramírez C, et al.
- **期刊**: Plant Cell, 2021
- **PMID**: 33955490
- **DOI**: 10.1093/plcell/koab101
- **关键点**:
  - 玉米根尖细胞类型
  - C4 光合作用相关基因
- **文件**: `papers/maize/Ortiz-Ramirez_2021_Maize_Root.pdf`

---

## 文献使用场景

### Agent 自动调用

1. **参数推荐时**:
   - 查询方法学文献
   - 提取推荐参数范围
   - 引用文献支持

2. **Marker 基因查询时**:
   - 查询物种特异文献
   - 提取 Marker 基因列表
   - 返回置信度和参考文献

3. **问题诊断时**:
   - 查询相关方法文献
   - 提供解决方案
   - 引用最佳实践

### 用户查询

```bash
# 查询方法
python agent/plant_sc_agent.py --query "SoupX 使用方法"

# 查询 Marker
python agent/plant_sc_agent.py --query "拟南芥根 Marker 基因"

# 查询参数
python agent/plant_sc_agent.py --query "Harmony theta 参数"
```

---

## 文献下载记录

### 已下载文献

| 文献 | 下载日期 | 来源 | 状态 |
|------|---------|------|------|
| Young_2020_SoupX.pdf | 2026-04-26 | PubMed | ✅ 已整合 |
| Wolock_2019_Scrublet.pdf | 2026-04-26 | PubMed | ✅ 已整合 |
| Denyer_2019_Root_Atlas.pdf | 2026-04-26 | PubMed | ✅ 已整合 |
| Kim_2021_Leaf_Atlas.pdf | 2026-04-26 | PubMed | ✅ 已整合 |

### 待下载文献

| 文献 | 优先级 | 原因 |
|------|--------|------|
| Shahan_2022_Root_Spatiotemporal.pdf | 高 | 最新根图谱 |
| Xu_2021_Flower_Atlas.pdf | 中 | 花 Marker 补充 |
| Liu_2021_Rice_Root.pdf | 中 | 水稻支持 |

---

## 文献更新流程

1. **定期检索** (每月)
   - PubMed 搜索: "plant single cell RNA-seq"
   - 筛选高影响力文献

2. **文献整合**
   - 提取 Marker 基因 → `markers/`
   - 提取方法参数 → `methods/`
   - 更新文献库 → `papers/`

3. **Agent 学习**
   - 向量化文献内容
   - 更新知识库索引
   - 测试检索效果

---

## 引用格式

当 Agent 使用文献时，自动生成引用：

```
根据 Young et al. (2020) 的研究，SoupX 推荐的 rho 阈值为 0.1。
参考文献: Young MD, Behjati S. GigaScience. 2020. PMID: 33367645
```

---

## 维护者

- **负责人**: Cherry
- **更新频率**: 每月
- **最后更新**: 2026-04-26
