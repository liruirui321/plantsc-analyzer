# Quick Start Guide

Get started with PlantSC-Analyzer in 5 minutes!

## Step 1: Prepare Your Data

### Option A: Starting from Raw FASTQ Files (Complete Pipeline)

Create a sample sheet (`samples.csv`):

```csv
sample_id,fastq_1,fastq_2,platform,batch,condition
sample1,/data/sample1_R1.fq.gz,/data/sample1_R2.fq.gz,BGI,batch1,control
sample2,/data/sample2_R1.fq.gz,/data/sample2_R2.fq.gz,BGI,batch1,treatment
sample3,/data/sample3_R1.fq.gz,/data/sample3_R2.fq.gz,10X,batch2,control
```

**Supported platforms**:
- `BGI` - BGI DNBSEQ (V2.0/V2.5, auto-detected)
- `10X` - 10X Genomics Chromium

### Option B: Starting from Expression Matrix (Skip Step 0)

Create a sample sheet (`samples.csv`):

```csv
sample_id,matrix_path,batch,condition
sample1,/data/sample1/filtered_matrix,batch1,control
sample2,/data/sample2/filtered_matrix,batch1,treatment
```

**Supported matrix formats**:
- 10X format (matrix.mtx.gz, features.tsv.gz, barcodes.tsv.gz)
- h5ad format (AnnData)
- h5 format (10X HDF5)

## Step 2: Create Configuration

Copy the template:

```bash
cp configs/project_template.yaml my_project.yaml
```

Edit key parameters:

```yaml
project:
  name: "MyProject"
  species: "arabidopsis"
  tissue: "root"

input:
  data_type: "fastq"  # or "matrix" if starting from expression matrix
  sample_sheet: "./samples.csv"

output:
  base_dir: "./results"

# Optional: Customize parameters
qc:
  min_genes: 200
  max_genes: 6000
  mito_threshold: 5.0

normalize:
  n_hvg: 3000

cluster:
  resolution: [0.4, 0.6, 0.8, 1.0]
```

## Step 3: Run Analysis

### Option A: Complete Pipeline from FASTQ

```bash
nextflow run workflows/main.nf \
    --data_type fastq \
    --sample_sheet samples.csv \
    --species arabidopsis \
    --tissue root \
    --outdir results \
    -profile standard
```

**What happens**:
1. ✅ Platform detection (BGI/10X)
2. ✅ Matrix generation (dnbc4tools/CellRanger)
3. ✅ Quality control (SoupX + Scrublet)
4. ✅ Normalization and HVG selection
5. ✅ Batch integration (if multiple batches)
6. ✅ Clustering and UMAP
7. ✅ Cell type annotation
8. ✅ Downstream analysis (optional)

**Estimated time**: 2-6 hours (depends on data size)

### Option B: From Expression Matrix (Faster)

```bash
nextflow run workflows/main.nf \
    --data_type matrix \
    --sample_sheet samples.csv \
    --species arabidopsis \
    --tissue root \
    --outdir results \
    -profile standard
```

**What happens**:
1. ⏭️  Skip matrix generation
2. ✅ Quality control
3. ✅ Normalization → Clustering → Annotation

**Estimated time**: 30 min - 2 hours

### Option C: Interactive Mode with Agent

```bash
python agent/plant_sc_agent.py --config my_project.yaml
```

The agent will guide you through each step and provide parameter recommendations:

```
🌱 PlantSC Agent: Starting analysis...

📊 Step 1: Quality Control
  ✅ Sample1: 5,234 cells, 78% alignment
  ✅ Sample2: 4,891 cells, 82% alignment

❓ All samples passed QC. Continue? [Y/n]: Y

🔍 Recommended filter parameters:
  • min_genes: 200
  • max_genes: 5000
  • mito_threshold: 5%

❓ Accept these parameters? [Y/n/edit]: Y
```

## Step 4: View Results

```bash
# Open HTML report
open results/report.html

# Check output structure
results/
├── 00_matrix_generation/    # (if starting from FASTQ)
│   ├── sample1/
│   │   ├── raw_matrix/
│   │   └── filtered_matrix/
│   └── sample2/
├── 01_qc/
│   ├── qc_summary_report.html
│   ├── soupx/               # SoupX corrected matrices
│   ├── scrublet/            # Doublet scores
│   └── filtered.h5ad        # Filtered data
├── 02_normalize/
│   ├── normalized.h5ad
│   └── hvg_plot.pdf
├── 03_integrate/            # (if multiple batches)
│   └── integrated.h5ad
├── 04_cluster/
│   ├── clustered.h5ad
│   ├── umap_clusters.pdf
│   └── cluster_composition.pdf
├── 05_annotate/
│   ├── annotated.h5ad       # Final annotated data
│   ├── cell_type_annotation.csv
│   └── annotation_umap.pdf
├── 06_downstream/           # (optional)
│   ├── deg/
│   ├── enrichment/
│   └── trajectory/
└── report.html              # Complete analysis report
```

## Example Output

### UMAP Visualization

![UMAP](images/umap_example.png)

### Cell Type Annotation

| Cluster | Cell Type | N Cells | Confidence |
|---------|-----------|---------|------------|
| 0 | Vessel | 1,234 | 0.95 |
| 1 | Fiber | 2,456 | 0.92 |
| 2 | Ray Parenchyma | 789 | 0.88 |

## Next Steps

- **Customize analysis**: Edit `my_project.yaml`
- **Add markers**: Update `knowledge_base/markers/`
- **Run downstream**: Enable DEG, trajectory, etc.
- **Read tutorials**: Check `docs/tutorials/`

## Common Commands

```bash
# Resume failed run
nextflow run workflows/main.nf -c my_project.yaml -resume

# Run on SLURM cluster
nextflow run workflows/main.nf -c my_project.yaml -profile slurm

# Clean work directory
nextflow clean -f

# View pipeline DAG
nextflow run workflows/main.nf -c my_project.yaml -with-dag dag.png
```

## Need Help?

- 📖 [User Guide](user_guide.md)
- 🎓 [Tutorials](tutorials/)
- 💬 [GitHub Issues](https://github.com/YOUR_USERNAME/plantsc-analyzer/issues)
