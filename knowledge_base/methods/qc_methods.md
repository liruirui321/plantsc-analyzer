# 单细胞分析 QC 方法选择指南

## 概览

质量控制是单细胞分析最关键的步骤。**错误的 QC 会导致所有下游分析失败**。

## QC 决策流程图

```
原始矩阵
    ↓
[1] 第一轮 QC：实验级质控
    ├─ Knee Plot → 判断有效细胞数
    ├─ 饱和度曲线 → 判断测序深度是否足够
    └─ 比对率 → 判断实验质量
    ↓
    质量合格? → 否 → 重新实验
    ↓ 是
[2] 环境 RNA 去除 (SoupX)
    ├─ 需要 raw + filtered 矩阵
    ├─ 估计污染率 rho
    └─ rho > 0.2 → 严重污染，需关注
    ↓
[3] Doublet 检测 (Scrublet)
    ├─ 自动阈值检测
    ├─ 预期 doublet 率：~5-10%
    └─ 标记或删除 doublets
    ↓
[4] 细胞过滤
    ├─ min_genes → 过滤空液滴
    ├─ max_genes → 过滤 doublets
    ├─ pct_mito → 过滤死细胞
    └─ 植物特异：过滤叶绿体/线粒体基因
    ↓
[5] 基因过滤
    └─ min_cells → 过滤不表达的基因
    ↓
过滤后矩阵 → 进入标准化
```

## 各方法详解

### 1. SoupX - 环境 RNA 去除

**什么时候用？**
- ✅ 所有 droplet-based 实验（10X, BGI）
- ✅ 当 rho > 0.05 时必须使用
- ❌ 如果没有 raw matrix，无法使用

**关键参数**:
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| tfidfMin | 1.0 | TF-IDF 最小值，用于估计污染基因 |
| forceAccept | TRUE | 强制接受估计结果 |

**判断标准**:
| 指标 | 正常 | 异常 |
|------|------|------|
| rho | < 0.1 | > 0.2 |
| 状态 | 继续分析 | 检查实验质量 |

**植物特异注意事项**:
- 叶绿体基因（ATCG 前缀）可能被大量检测到
- 这些不是污染，而是植物细胞特有
- 需要在 SoupX 之后单独处理

### 2. Scrublet - Doublet 检测

**什么时候用？**
- ✅ 细胞数 > 1,000 时推荐使用
- ✅ 所有 droplet-based 实验
- ❌ 细胞数 < 500 时结果不可靠

**关键参数**:
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| expected_doublet_rate | 0.06 | 预期 doublet 率 |
| threshold | auto | 自动检测阈值 |

**预期 doublet 率参考**:
| 加载细胞数 | 预期 doublet 率 |
|-----------|----------------|
| 1,000 | ~0.8% |
| 5,000 | ~3.9% |
| 10,000 | ~7.6% |
| 20,000 | ~15.4% |

### 3. 细胞过滤阈值

**如何确定阈值？**

1. **min_genes**: 看 violin plot 的下尾
   - 推荐：200-500（取决于组织）
   - 植物组织通常更低（200）

2. **max_genes**: 看 violin plot 的上尾
   - 推荐：基因数分布 95th percentile
   - 或者 2-3 倍中位数

3. **pct_mito**: 植物特异
   | 组织 | 推荐阈值 |
   |------|---------|
   | 根 | 5-10% |
   | 叶 | 10-20%（叶绿体基因较多）|
   | 茎 | 5-10% |
   | 花 | 5-10% |

4. **植物特异过滤**:
   - 线粒体基因前缀：ATMG（拟南芥）、OSMT（水稻）
   - 叶绿体基因前缀：ATCG（拟南芥）、OSCP（水稻）
   - 建议：保留叶绿体信息但不作为过滤标准

## 常见问题

### Q: 过滤后细胞数大幅减少怎么办？
- 检查阈值是否太严格
- 使用 violin plot 重新确定阈值
- 考虑降低 min_genes 到 100-150

### Q: 如何区分真正的低质量细胞和特殊细胞类型？
- 某些细胞类型（如红细胞、根毛细胞）确实基因数较低
- 建议先用宽松阈值，聚类后再检查

### Q: SoupX 和 Scrublet 的顺序？
- 推荐顺序：SoupX → Scrublet → 细胞过滤
- SoupX 先去除背景噪音，Scrublet 再检测 doublets

## 参考文献

1. Young MD, Behjati S. SoupX removes ambient RNA contamination from droplet-based single-cell RNA sequencing data. GigaScience. 2020.
2. Wolock SL, Lopez R, Klein AM. Scrublet: Computational Identification of Cell Doublets in Single-Cell Transcriptomic Data. Cell Systems. 2019.
3. Luecken MD, Theis FJ. Current best practices in single-cell RNA-seq analysis: a tutorial. Mol Syst Biol. 2019.
