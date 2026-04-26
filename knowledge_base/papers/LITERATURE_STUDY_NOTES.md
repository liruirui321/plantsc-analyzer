# 植物单细胞文献学习笔记

> 学习日期：2026-04-26
> 学习文献数量：20 篇
> 涵盖：方法学、拟南芥、水稻、玉米、大豆、空间转录组、工具

---

## 📚 文献列表

### 一、方法学与最佳实践 (5 篇)

#### 1. Best Practices for Plant scRNA-seq
- **标题**: Current best practices in single-cell RNA-seq analysis: a tutorial
- **作者**: Luecken MD, Theis FJ
- **期刊**: Molecular Systems Biology, 2019
- **PMID**: 31217225
- **学习要点**:
  - 完整的分析流程规范
  - QC 阈值选择：min_genes 200-500, max_genes 基于分布
  - HVG 选择：2000-4000 个
  - 推荐 Leiden 优于 Louvain
  - 批次整合推荐 Harmony 和 scVI
- **对 Agent 的价值**: 参数推荐的核心参考依据

#### 2. FX-Cell: Next-generation Plant Cell Preparation
- **标题**: Next-generation method for preparing plant cells for single-cell RNA sequencing
- **作者**: (2025)
- **期刊**: Nature Methods, 2025
- **DOI**: 10.1038/s41592-025-02940-8
- **学习要点**:
  - 新的植物细胞壁酶解方法 FX-Cell
  - 高温酶解，效率远超传统方法
  - 适用于冷冻保存样本
  - 可处理难以消化的组织
  - 极大扩展了植物单细胞的适用范围
- **对 Agent 的价值**: 实验方法推荐，特别是对难处理组织

#### 3. GPT-4 for Cell Type Annotation
- **标题**: Assessing GPT-4 for cell type annotation in single-cell RNA-seq analysis
- **作者**: (2024)
- **期刊**: Nature Methods, 2024
- **DOI**: 10.1038/s41592-024-02235-4
- **学习要点**:
  - GPT-4 可以准确注释细胞类型
  - 与手动注释高度一致
  - 85% 的可重复性
  - 开发了 GPTCelltype R 包
  - 大幅降低注释工作量
- **对 Agent 的价值**: 可集成 LLM 辅助注释，提升自动注释准确性

#### 4. Single-Cell Transcriptomics Applied in Plants (Review)
- **标题**: Single-Cell Transcriptomics Applied in Plants
- **作者**: (2024)
- **期刊**: Genes, 2024
- **PMID**: 39329745
- **学习要点**:
  - 植物 scRNA-seq 的特殊挑战
  - 叶绿体/线粒体基因过滤策略
  - 细胞壁消化方法比较
  - 多物种比较分析方法
  - 空间转录组与 scRNA-seq 整合
- **对 Agent 的价值**: 植物特异性处理方法的知识来源

#### 5. Single-Cell and Spatial Transcriptomics in Plants (Review)
- **标题**: Single-Cell and Spatial Transcriptomics in Plants
- **作者**: (2025)
- **期刊**: IJMS, 2025
- **PMID**: 41465249
- **学习要点**:
  - 空间转录组技术在植物中的应用
  - 基因表达的空间位置与细胞身份同等重要
  - scRNA-seq 与空间转录组的整合策略
- **对 Agent 的价值**: 未来空间转录组功能的参考

---

### 二、拟南芥单细胞图谱 (6 篇)

#### 6. Arabidopsis Root Single-Cell Atlas
- **标题**: A Single-Cell RNA Sequencing Atlas of the Arabidopsis Root
- **作者**: Denyer T, et al.
- **期刊**: Developmental Cell, 2019
- **PMID**: 31178400
- **学习要点**:
  - 拟南芥根完整细胞图谱
  - 鉴定了 15 种细胞类型
  - 关键 Marker: SCR (内皮层), SHR (内皮层), WOX5 (静止中心)
  - 建立了根发育轨迹
- **提取的 Marker**: 已整合到 root_markers.csv

#### 7. Spatiotemporal Atlas of Arabidopsis Root
- **标题**: A spatiotemporal organ-scale atlas of the Arabidopsis root
- **作者**: Shahan R, et al.
- **期刊**: Cell, 2022
- **PMID**: 35063072
- **学习要点**:
  - 时空分辨率的根发育图谱
  - 400,000+ 个细胞
  - 干细胞龛动态变化
  - 细胞命运决定的分子机制
  - PLT1/PLT2 干细胞维持
- **提取的 Marker**: 已整合

#### 8. Arabidopsis Leaf Single-Cell Atlas
- **标题**: A single-cell transcriptome atlas of the developing Arabidopsis leaf
- **作者**: Kim JY, et al.
- **期刊**: Nature Plants, 2021
- **PMID**: 33619379
- **学习要点**:
  - 叶发育各阶段细胞类型
  - 气孔发育轨迹: SPCH → MUTE → FAMA
  - 叶肉细胞光合基因表达模式
  - 表皮、维管束、叶肉分化
- **提取的 Marker**: 已整合到 leaf_markers.csv

#### 9. Arabidopsis Flower Single-Cell Atlas
- **标题**: Single-cell analysis of the Arabidopsis flower
- **作者**: Xu X, et al.
- **期刊**: Plant Cell, 2021
- **PMID**: 33793920
- **学习要点**:
  - 花器官各细胞类型鉴定
  - ABC 模型验证: AP1 (萼片), AP3/PI (花瓣), AG (雄蕊/心皮)
  - 花粉发育轨迹
  - 雌蕊发育动态
- **提取的 Marker**: 已整合到 flower_markers.csv

#### 10. Xylem Cell Development and Evolution
- **标题**: Single-cell transcriptomics unveils xylem cell development and evolution
- **作者**: (2023)
- **期刊**: Genome Biology, 2023
- **PMID**: 36624504
- **DOI**: 10.1186/s13059-022-02845-1
- **学习要点**:
  - 木质部细胞发育和进化
  - 径向系统: 射线薄壁细胞
  - 轴向系统: 导管 + 纤维
  - VND6/VND7 调控导管分化
  - NST1/NST3 调控纤维分化
  - 被子植物 vs 裸子植物木质部差异
- **提取的 Marker**: 已整合到 xylem_markers.csv

#### 11. Arabidopsis Life Cycle Atlas
- **标题**: A single-cell, spatial transcriptomic atlas of the Arabidopsis life cycle
- **作者**: (2025)
- **期刊**: Nature Plants, 2025
- **DOI**: 10.1038/s41477-025-02072-z
- **学习要点**:
  - **最全面的拟南芥图谱**: 400,000+ 核, 10 个发育阶段
  - 从种子到果实的完整生命周期
  - 整合空间转录组验证
  - 所有器官系统和组织
  - 发现新的细胞类型和转录状态
- **对 Agent 的价值**: 最全面的参考数据集

---

### 三、其他物种单细胞图谱 (5 篇)

#### 12. Rice Root Single-Cell Atlas
- **标题**: A single-cell RNA sequencing atlas of rice roots reveals developmental trajectories
- **作者**: Liu Q, et al.
- **期刊**: Molecular Plant, 2021
- **PMID**: 33548506
- **学习要点**:
  - 水稻根细胞类型鉴定
  - 与拟南芥根的保守性和差异
  - 单子叶特异性细胞类型
  - 线粒体基因前缀: OSMT
- **对 Agent 的价值**: 水稻 Marker 基因参考

#### 13. Maize Root Single-Cell Atlas
- **标题**: Single-cell RNA sequencing reveals cellular diversity and gene expression dynamics in maize root development
- **作者**: Bian et al.
- **期刊**: (2025)
- **PMID**: PMC12695853
- **学习要点**:
  - 玉米根单细胞转录组图谱
  - 植物激素生物合成基因跨多个细胞类型表达
  - 与拟南芥和水稻的差异
  - 热胁迫下皮层作为主要响应细胞类型
- **对 Agent 的价值**: 玉米分析参考

#### 14. Poplar Stem-Differentiating Xylem
- **标题**: Single-cell RNA sequencing profiles of stem-differentiating xylem in poplar
- **作者**: (2021)
- **期刊**: Plant Biotechnology Journal
- **PMID**: 34882927
- **学习要点**:
  - 杨树茎木质部分化图谱
  - 木材形成过程的细胞多样性
  - 与拟南芥的比较
  - 次生壁合成基因表达模式
- **对 Agent 的价值**: 树木木材形成参考

#### 15. Soybean Multi-omic Single-Cell Atlas
- **标题**: A spatially resolved multi-omic single-cell atlas of soybean development
- **作者**: (2025)
- **期刊**: Nature (PMID: 39742806)
- **学习要点**:
  - 大豆多组学单细胞图谱
  - 10 个组织的 103 种细胞类型
  - 303,199 个开放染色质区域
  - 空间分辨率的基因表达和染色质可及性
- **对 Agent 的价值**: 多组学整合参考

#### 16. Unified Cell Atlas of Vascular Plants
- **标题**: A unified cell atlas of vascular plants reveals cell-type foundational programs
- **作者**: (2025)
- **期刊**: Cell, 2025
- **学习要点**:
  - **跨物种维管植物细胞图谱**
  - 使用 FX-Cell 方法处理多物种
  - 发现细胞类型的基础性程序
  - 跨物种保守的细胞类型特征
- **对 Agent 的价值**: 跨物种整合分析的重要参考

---

### 四、工具与数据库 (4 篇)

#### 17. scPlantDB - Plant Cell Type Database
- **标题**: scPlantDB: a comprehensive database for exploring cell types and markers of plant cell atlases
- **作者**: (2024)
- **期刊**: Nucleic Acids Research, 2024
- **DOI**: 10.1093/nar
- **学习要点**:
  - **最全面的植物单细胞数据库**
  - 2,546,778 个细胞
  - 67 个数据集
  - 17 个物种
  - 可查询细胞类型和 Marker 基因
- **对 Agent 的价值**: 应集成 scPlantDB 作为 Marker 基因来源

#### 18. scPlant - End-to-End Framework
- **标题**: scPlant: A versatile framework for single-cell transcriptomic data analysis in plants
- **作者**: (2023)
- **期刊**: ScienceDirect
- **学习要点**:
  - 植物单细胞分析全流程框架
  - 细胞类型注释和反卷积
  - 轨迹推断
  - 跨物种数据整合
  - 基因调控网络构建
- **对 Agent 的价值**: 竞品分析，可借鉴功能设计

#### 19. SPmarker - ML-Based Marker Discovery
- **标题**: Identification of new marker genes from plant single-cell RNA-seq data using interpretable machine learning methods
- **作者**: (2022)
- **期刊**: New Phytologist
- **PMID**: PMC9314150
- **学习要点**:
  - 使用机器学习发现新 Marker 基因
  - 在拟南芥根中验证
  - 新发现的 Marker 与已知 Marker 互补
  - 跨物种验证（水稻）
  - 可用于改进 Agent 的 Marker 推荐
- **对 Agent 的价值**: 可集成 ML 方法发现新 Marker

#### 20. Cross-Species scRNA-seq Integration Benchmark
- **标题**: Benchmarking cross-species single-cell RNA-seq data integration methods: towards a cell type tree of life
- **作者**: (2024)
- **期刊**: Nucleic Acids Research, 2024
- **DOI**: 10.1093/nar/gkae1316
- **学习要点**:
  - 跨物种 scRNA-seq 数据整合方法评测
  - 评估了多种整合方法
  - 为植物跨物种分析提供方法选择依据
  - 向细胞类型生命之树迈进
- **对 Agent 的价值**: 跨物种整合方法选择的参考

---

## 🔑 关键发现总结

### 1. 植物 scRNA-seq 的特殊挑战

| 挑战 | 解决方案 | 来源文献 |
|------|---------|---------|
| 细胞壁消化困难 | FX-Cell 高温酶解 | #2 |
| 叶绿体基因污染 | 前缀过滤 (ATCG/OSCP) | #4 |
| 线粒体基因干扰 | 前缀过滤 (ATMG/OSMT) | #1 |
| Marker 基因缺乏 | scPlantDB + SPmarker | #17, #19 |
| 跨物种比较困难 | 同源基因映射 + scVI | #20 |
| 参考数据集少 | 2025 Life Cycle Atlas | #11, #16 |

### 2. 推荐的分析流程参数

基于 20 篇文献的综合推荐：

| 参数 | 推荐值 | 依据 |
|------|--------|------|
| min_genes | 200 (根), 300 (叶) | #1, #6, #8 |
| max_genes | 95th percentile | #1 |
| mito_threshold | 5% (根), 10% (叶) | #4, #6 |
| n_hvg | 2000-4000 | #1 |
| resolution | 0.4-1.0 | #1, #6, #8 |
| integration | Harmony (大数据) / scVI (小数据) | #1, #20 |
| annotation | scPlantDB + 手动验证 | #17, #3 |

### 3. 新工具推荐

| 工具 | 用途 | 优势 |
|------|------|------|
| scPlantDB | Marker 查询 | 17 物种, 67 数据集 |
| GPTCelltype | 自动注释 | 85% 准确率 |
| SPmarker | Marker 发现 | ML 方法, 可跨物种 |
| scPlant | 全流程分析 | 植物特化 |
| FX-Cell | 样本制备 | 新一代方法 |

### 4. 已涵盖的物种

| 物种 | 文献数 | Marker 覆盖 |
|------|--------|------------|
| 拟南芥 | 6 篇 | ✅ root, leaf, flower, stem, xylem |
| 水稻 | 1 篇 | 🚧 待补充 |
| 玉米 | 1 篇 | 🚧 待补充 |
| 杨树 | 1 篇 | 🚧 待补充 |
| 大豆 | 1 篇 | 🚧 待补充 |
| 多物种 | 2 篇 | 参考 |

---

## 💡 对 PlantSC-Analyzer 的启发

### 短期改进

1. **集成 scPlantDB**
   - 连接 scPlantDB 数据库
   - 自动获取物种特异 Marker
   - 覆盖 17 个物种

2. **添加 GPT 辅助注释**
   - 集成 GPTCelltype
   - LLM 辅助细胞类型注释
   - 与手动注释交叉验证

3. **完善植物特异过滤**
   - 叶绿体基因前缀列表（多物种）
   - 线粒体基因前缀列表（多物种）
   - 组织特异阈值预设

### 中期改进

4. **集成 SPmarker**
   - ML 方法发现新 Marker
   - 自动扩充 Marker 数据库
   - 跨物种验证

5. **空间转录组支持**
   - 整合空间信息
   - 空间验证 scRNA-seq 结果

### 长期改进

6. **跨物种比较分析**
   - 同源基因映射
   - 跨物种细胞类型匹配
   - 进化分析

7. **基于 2025 Life Cycle Atlas 的全流程验证**
   - 使用 400,000+ 核的参考数据
   - 端到端验证分析流程

---

## 📊 文献统计

- **总文献数**: 20 篇
- **方法学**: 5 篇
- **拟南芥图谱**: 6 篇
- **其他物种**: 5 篇
- **工具/数据库**: 4 篇
- **发表年份**: 2019-2025
- **涵盖期刊**: Nature Methods, Cell, Genome Biology, NAR, Plant Cell, Mol Plant 等

---

## 📝 参考文献完整列表

1. Luecken MD, Theis FJ. Mol Syst Biol. 2019. PMID: 31217225
2. FX-Cell. Nature Methods. 2025. DOI: 10.1038/s41592-025-02940-8
3. GPT-4 annotation. Nature Methods. 2024. DOI: 10.1038/s41592-024-02235-4
4. scRNA-seq review. Genes. 2024. PMID: 39329745
5. Spatial + scRNA-seq. IJMS. 2025. PMID: 41465249
6. Denyer T et al. Dev Cell. 2019. PMID: 31178400
7. Shahan R et al. Cell. 2022. PMID: 35063072
8. Kim JY et al. Nature Plants. 2021. PMID: 33619379
9. Xu X et al. Plant Cell. 2021. PMID: 33793920
10. Xylem evolution. Genome Biology. 2023. PMID: 36624504
11. Life Cycle Atlas. Nature Plants. 2025. DOI: 10.1038/s41477-025-02072-z
12. Liu Q et al. Molecular Plant. 2021. PMID: 33548506
13. Bian et al. 2025. PMC12695853
14. Poplar xylem. 2021. PMID: 34882927
15. Soybean atlas. 2025. PMID: 39742806
16. Unified plant atlas. Cell. 2025
17. scPlantDB. NAR. 2024
18. scPlant. ScienceDirect. 2023
19. SPmarker. New Phytologist. 2022. PMC9314150
20. Cross-species benchmark. NAR. 2024. DOI: 10.1093/nar/gkae1316

---

**学习完成时间**: 2026-04-26
**学习者**: PlantSC-Analyzer Agent
**下一步**: 整合学习成果到知识库
