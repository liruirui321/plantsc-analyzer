# PlantSC Marker 基因库

本目录存放植物细胞类型标记基因数据库。

## 目录结构

```
markers/
├── arabidopsis/           # 拟南芥 (优先构建)
│   ├── all_markers.csv    # 全部 Marker 汇总
│   ├── root_markers.csv   # 根
│   ├── leaf_markers.csv   # 叶
│   ├── stem_markers.csv   # 茎
│   ├── flower_markers.csv # 花
│   └── seed_markers.csv   # 种子
├── rice/                  # 水稻 (Phase 2)
├── maize/                 # 玉米 (Phase 2)
├── poplar/                # 杨树 (Phase 2)
├── cross_species/         # 跨物种同源映射
│   └── ortholog_mapping.tsv
└── custom/                # 用户自定义 Marker
    └── template.csv
```

## CSV 格式规范

```csv
gene_id,gene_symbol,cell_type,tissue,sub_type,confidence,source,pmid
AT1G01010,NAC001,vessel,xylem,,high,literature,12345678
AT2G02020,MYB46,fiber,xylem,,high,literature,23456789
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| gene_id | 是 | 基因唯一标识符 |
| gene_symbol | 是 | 基因名称 |
| cell_type | 是 | 细胞类型 |
| tissue | 是 | 组织来源 |
| sub_type | 否 | 细胞亚型 |
| confidence | 是 | 可信度: high/medium/low |
| source | 是 | 来源: literature/database/prediction |
| pmid | 否 | PubMed 文献 ID |

## 数据来源

- PubMed 文献手工标注
- PlantscRNAdb 数据库
- CellMarker 2.0
- 社区贡献

## 贡献新 Marker

1. 复制 `custom/template.csv`
2. 按格式填入 Marker 信息
3. 提交 Pull Request
