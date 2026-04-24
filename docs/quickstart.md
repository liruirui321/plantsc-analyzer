# Quick Start Guide

Get started with PlantSC-Analyzer in 5 minutes!

## Step 1: Prepare Your Data

Create a sample sheet (`samples.csv`):

```csv
sample_id,matrix_path,batch,condition
sample1,/data/sample1/filtered_matrix,batch1,control
sample2,/data/sample2/filtered_matrix,batch1,treatment
```

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
  sample_sheet: "./samples.csv"

output:
  base_dir: "./results"
```

## Step 3: Run Analysis

### Option A: Interactive Mode (Recommended)

```bash
python agent/plant_sc_agent.py --config my_project.yaml
```

The agent will guide you through each step:

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

### Option B: Automatic Mode

```bash
nextflow run workflows/main.nf -c my_project.yaml
```

## Step 4: View Results

```bash
# Open HTML report
open results/pipeline_report.html

# Check output structure
results/
├── 01_qc/
│   ├── qc_summary_report.html
│   └── filtered/
├── 02_normalize/
├── 03_integrate/
├── 04_cluster/
│   └── umap_clusters.pdf
├── 05_annotate/
│   └── cell_type_annotation.csv
└── 06_downstream/
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
