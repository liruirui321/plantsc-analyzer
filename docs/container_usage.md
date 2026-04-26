# Container Usage Guide

## Docker

### Build Docker Image

```bash
# From project root
docker build -t plantsc-analyzer:0.1.0-alpha .

# Build with specific tag
docker build -t plantsc-analyzer:latest .
```

### Run with Docker

```bash
# Run Nextflow pipeline
docker run --rm -v $(pwd)/data:/data -v $(pwd)/results:/results \
    plantsc-analyzer:latest \
    nextflow run /opt/plantsc-analyzer/workflows/main.nf \
    --sample_sheet /data/samples.csv \
    --outdir /results

# Run Agent interactively
docker run --rm -it -v $(pwd)/data:/data \
    plantsc-analyzer:latest \
    python /opt/plantsc-analyzer/agent/plant_sc_agent.py

# Run specific script
docker run --rm -v $(pwd)/data:/data \
    plantsc-analyzer:latest \
    python /opt/plantsc-analyzer/scripts/01_qc/filter_cells.py \
    --input /data/raw.h5ad --output /data/filtered.h5ad
```

### Docker Compose (Optional)

```yaml
# docker-compose.yml
version: '3.8'
services:
  plantsc:
    image: plantsc-analyzer:latest
    volumes:
      - ./data:/data
      - ./results:/results
    command: nextflow run /opt/plantsc-analyzer/workflows/main.nf --help
```

Run with:
```bash
docker-compose up
```

---

## Singularity

### Build Singularity Image

```bash
# From project root
singularity build plantsc-analyzer.sif envs/singularity.def

# Build from Docker Hub (when published)
singularity build plantsc-analyzer.sif docker://plantsc/plantsc-analyzer:latest
```

### Run with Singularity

```bash
# Run Nextflow pipeline
singularity run \
    --bind $(pwd)/data:/data,$(pwd)/results:/results \
    plantsc-analyzer.sif \
    nextflow run /opt/plantsc-analyzer/workflows/main.nf \
    --sample_sheet /data/samples.csv \
    --outdir /results

# Run Agent
singularity exec \
    --bind $(pwd)/data:/data \
    plantsc-analyzer.sif \
    conda run -n plantsc python /opt/plantsc-analyzer/agent/plant_sc_agent.py

# Run specific script
singularity exec \
    --bind $(pwd)/data:/data \
    plantsc-analyzer.sif \
    conda run -n plantsc python /opt/plantsc-analyzer/scripts/01_qc/filter_cells.py \
    --input /data/raw.h5ad --output /data/filtered.h5ad
```

### Singularity on HPC

```bash
# SLURM example
#!/bin/bash
#SBATCH --job-name=plantsc
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00

module load singularity

singularity run \
    --bind $SCRATCH/data:/data,$SCRATCH/results:/results \
    plantsc-analyzer.sif \
    nextflow run /opt/plantsc-analyzer/workflows/main.nf \
    --sample_sheet /data/samples.csv \
    --outdir /results \
    -profile slurm
```

---

## Volume Mounts

### Required Mounts

- **Data directory**: `-v /path/to/data:/data`
- **Results directory**: `-v /path/to/results:/results`

### Optional Mounts

- **Config files**: `-v /path/to/config.yaml:/config/config.yaml`
- **Custom markers**: `-v /path/to/markers:/opt/plantsc-analyzer/knowledge_base/markers`

---

## Environment Variables

```bash
# Set number of threads
docker run --rm -e OMP_NUM_THREADS=16 plantsc-analyzer:latest ...

# Set memory limit
docker run --rm -e JAVA_OPTS="-Xmx32g" plantsc-analyzer:latest ...
```

---

## GPU Support (for scVI)

### Docker with GPU

```bash
# Requires nvidia-docker
docker run --rm --gpus all \
    -v $(pwd)/data:/data \
    plantsc-analyzer:latest \
    python /opt/plantsc-analyzer/scripts/03_integrate/scvi_integration.py \
    --input /data/normalized.h5ad \
    --output /data/integrated.h5ad \
    --use_gpu
```

### Singularity with GPU

```bash
singularity exec --nv \
    --bind $(pwd)/data:/data \
    plantsc-analyzer.sif \
    conda run -n plantsc python /opt/plantsc-analyzer/scripts/03_integrate/scvi_integration.py \
    --input /data/normalized.h5ad \
    --output /data/integrated.h5ad \
    --use_gpu
```

---

## Troubleshooting

### Permission Issues

```bash
# Run as current user
docker run --rm --user $(id -u):$(id -g) ...
```

### Memory Issues

```bash
# Increase Docker memory limit
docker run --rm --memory=64g ...
```

### Check Container

```bash
# Test Docker image
docker run --rm plantsc-analyzer:latest conda run -n plantsc python -c "import scanpy; print(scanpy.__version__)"

# Test Singularity image
singularity test plantsc-analyzer.sif
```

---

## Publishing Images

### Docker Hub

```bash
# Tag image
docker tag plantsc-analyzer:latest username/plantsc-analyzer:0.1.0-alpha

# Push to Docker Hub
docker push username/plantsc-analyzer:0.1.0-alpha
```

### Singularity Library

```bash
# Sign in
singularity remote login

# Push to library
singularity push plantsc-analyzer.sif library://username/plantsc-analyzer:0.1.0-alpha
```

---

## Best Practices

1. **Always bind mount data directories** - Don't copy large files into containers
2. **Use specific version tags** - Avoid `latest` in production
3. **Set resource limits** - Prevent containers from consuming all resources
4. **Use read-only mounts when possible** - `--bind /data:/data:ro`
5. **Clean up after runs** - Use `--rm` flag with Docker
