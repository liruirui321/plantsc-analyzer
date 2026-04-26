# 植物单细胞分析完整流程图

## 总体流程

```mermaid
graph TD
    A[原始数据] --> B{数据类型?}
    B -->|FASTQ| C[Step 0: 平台检测与矩阵生成]
    B -->|Matrix| D[Step 1: 质控 QC]
    C --> D
    D --> E[Step 2: 标准化]
    E --> F{多批次?}
    F -->|是| G[Step 3: 批次整合]
    F -->|否| H[Step 4: 聚类]
    G --> H
    H --> I[Step 5: 细胞类型注释]
    I --> J{需要下游分析?}
    J -->|是| K[Step 6: 下游分析]
    J -->|否| L[生成报告]
    K --> L
    L --> M[完成]
    
    style A fill:#e1f5ff
    style M fill:#c8e6c9
    style D fill:#fff9c4
    style G fill:#ffe0b2
    style I fill:#f8bbd0
```

## Step 0: 平台检测与矩阵生成

```mermaid
graph LR
    A[FASTQ 文件] --> B[检测平台]
    B --> C{平台类型}
    C -->|BGI| D[检测 Kit 版本]
    C -->|10X| E[运行 CellRanger]
    D --> F{V2.0/V2.5?}
    F -->|是| G[Oligo 剪切]
    F -->|否| H[运行 dnbc4tools]
    G --> H
    H --> I[生成矩阵]
    E --> I
    I --> J[转换为 h5ad]
    J --> K[输出: raw + filtered 矩阵]
```

## Step 1: 质控 (QC)

```mermaid
graph TD
    A[输入矩阵] --> B[计算 QC metrics]
    B --> C[SoupX 环境 RNA 去除]
    C --> D{rho > 0.2?}
    D -->|是| E[警告: 严重污染]
    D -->|否| F[Scrublet Doublet 检测]
    E --> F
    F --> G{细胞数 > 1000?}
    G -->|是| H[标记 doublets]
    G -->|否| I[跳过 doublet 检测]
    H --> J[细胞过滤]
    I --> J
    J --> K{过滤标准}
    K --> L[min_genes: 去除空液滴]
    K --> M[max_genes: 去除 doublets]
    K --> N[pct_mito: 去除死细胞]
    L --> O[基因过滤]
    M --> O
    N --> O
    O --> P[输出: filtered.h5ad]
    
    style D fill:#ffccbc
    style E fill:#ef9a9a
```

## Step 2: 标准化

```mermaid
graph TD
    A[filtered.h5ad] --> B[保存 counts layer]
    B --> C[标准化: log1p]
    C --> D[HVG 选择]
    D --> E{多批次?}
    E -->|是| F[batch-aware HVG]
    E -->|否| G[标准 HVG]
    F --> H[Scaling]
    G --> H
    H --> I{多样本?}
    I -->|是| J[合并样本]
    I -->|否| K[输出: normalized.h5ad]
    J --> K
```

## Step 3: 批次整合 (可选)

```mermaid
graph TD
    A[normalized.h5ad] --> B{批次数}
    B -->|1| C[跳过整合]
    B -->|>1| D{数据集大小}
    D -->|大 >20K| E[Harmony 整合]
    D -->|中/小| F{有 GPU?}
    F -->|是| G[scVI 整合]
    F -->|否| E
    E --> H[评估整合效果]
    G --> H
    H --> I{批次效应消除?}
    I -->|否| J[调整参数]
    I -->|是| K[输出: integrated.h5ad]
    J --> E
    C --> K
```

## Step 4: 聚类

```mermaid
graph TD
    A[integrated.h5ad] --> B[PCA 降维]
    B --> C{选择 PC 数}
    C --> D[Elbow plot]
    D --> E[构建 KNN 图]
    E --> F[多 resolution 聚类]
    F --> G[Resolution 1]
    F --> H[Resolution 2]
    F --> I[Resolution 3]
    G --> J[UMAP 可视化]
    H --> J
    I --> J
    J --> K[评估聚类质量]
    K --> L{质量合格?}
    L -->|否| M[调整参数]
    L -->|是| N[选择最佳 resolution]
    M --> F
    N --> O[输出: clustered.h5ad]
```

## Step 5: 细胞类型注释

```mermaid
graph TD
    A[clustered.h5ad] --> B[查询 Marker 基因库]
    B --> C{物种}
    C -->|拟南芥| D[加载拟南芥 Markers]
    C -->|水稻| E[加载水稻 Markers]
    C -->|其他| F[自定义 Markers]
    D --> G[计算 Marker 表达]
    E --> G
    F --> G
    G --> H[每个 cluster 找 DEG]
    H --> I[匹配 Marker 基因]
    I --> J[计算置信度分数]
    J --> K{置信度 > 阈值?}
    K -->|是| L[自动注释]
    K -->|否| M[标记为 Unknown]
    L --> N[生成注释报告]
    M --> N
    N --> O[手动检查]
    O --> P[输出: annotated.h5ad]
```

## Step 6: 下游分析 (可选)

```mermaid
graph TD
    A[annotated.h5ad] --> B{分析类型}
    B --> C[差异表达 DEG]
    B --> D[富集分析]
    B --> E[拟时序分析]
    
    C --> F[组间比较]
    F --> G[Wilcoxon 检验]
    G --> H[Volcano plot]
    
    D --> I[GO/KEGG 富集]
    I --> J[gProfiler]
    J --> K[Enrichment plot]
    
    E --> L[PAGA 轨迹推断]
    L --> M[Diffusion pseudotime]
    M --> N[Trajectory plot]
    
    H --> O[汇总结果]
    K --> O
    N --> O
    O --> P[输出: downstream/]
```

## Agent 决策流程

```mermaid
graph TD
    A[用户输入数据] --> B[Agent 分析数据特征]
    B --> C[数据大小]
    B --> D[批次数量]
    B --> E[组织类型]
    
    C --> F[推荐 QC 参数]
    D --> F
    E --> F
    
    F --> G[推荐标准化参数]
    G --> H[推荐整合方法]
    H --> I[推荐聚类参数]
    
    I --> J{用户确认?}
    J -->|是| K[运行 Nextflow 流程]
    J -->|否| L[用户修改参数]
    L --> K
    
    K --> M[监控运行状态]
    M --> N{运行成功?}
    N -->|否| O[诊断问题]
    N -->|是| P[生成报告]
    O --> Q[提供解决方案]
    Q --> K
    P --> R[完成]
    
    style B fill:#e1bee7
    style F fill:#fff9c4
    style K fill:#c5e1a5
```

## 质量检查点

```mermaid
graph LR
    A[QC 检查点] --> B{过滤后细胞数 > 50%?}
    B -->|否| C[阈值太严格]
    B -->|是| D[继续]
    
    E[标准化检查点] --> F{HVG 分布合理?}
    F -->|否| G[调整 n_hvg]
    F -->|是| H[继续]
    
    I[整合检查点] --> J{批次混合良好?}
    J -->|否| K[调整 theta/n_latent]
    J -->|是| L[继续]
    
    M[聚类检查点] --> N{聚类数合理?}
    N -->|否| O[调整 resolution]
    N -->|是| P[继续]
    
    Q[注释检查点] --> R{置信度 > 0.6?}
    R -->|否| S[手动检查]
    R -->|是| T[完成]
```

## 文件流转图

```mermaid
graph LR
    A[FASTQ] --> B[00_matrix_generation/]
    B --> C[raw_matrix/]
    B --> D[filtered_matrix/]
    
    C --> E[01_qc/]
    D --> E
    E --> F[soupx/]
    E --> G[scrublet/]
    E --> H[filtered.h5ad]
    
    H --> I[02_normalize/]
    I --> J[normalized.h5ad]
    I --> K[hvg_plot.pdf]
    
    J --> L[03_integrate/]
    L --> M[integrated.h5ad]
    
    M --> N[04_cluster/]
    N --> O[clustered.h5ad]
    N --> P[umap.pdf]
    
    O --> Q[05_annotate/]
    Q --> R[annotated.h5ad]
    Q --> S[cell_type_annotation.csv]
    
    R --> T[06_downstream/]
    T --> U[deg/]
    T --> V[enrichment/]
    T --> W[trajectory/]
    
    style A fill:#e3f2fd
    style R fill:#c8e6c9
```

---

## 使用说明

这些流程图展示了：
1. **总体流程** - 完整的分析步骤
2. **各步骤详细流程** - 每个步骤的内部逻辑
3. **Agent 决策流程** - 智能推荐系统如何工作
4. **质量检查点** - 关键的质量控制节点
5. **文件流转** - 数据如何在各步骤间传递

可以用 Mermaid 渲染这些图表，或者导出为 PNG/SVG 格式。
