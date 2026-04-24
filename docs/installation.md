# Installation Guide

## Prerequisites

- Linux or macOS (Windows via WSL2)
- Conda or Mamba
- Git
- 16GB+ RAM recommended
- (Optional) NVIDIA GPU for scVI/scGPT

## Quick Install

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/plantsc-analyzer.git
cd plantsc-analyzer
```

### 2. Create Conda Environment

```bash
# Using conda
conda env create -f envs/environment.yml

# Or using mamba (faster)
mamba env create -f envs/environment.yml

# Activate environment
conda activate plantsc
```

### 3. Install Nextflow

```bash
# Via conda (recommended)
conda install -c bioconda nextflow

# Or via curl
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

### 4. Verify Installation

```bash
# Check Python packages
python -c "import scanpy; print(scanpy.__version__)"

# Check Nextflow
nextflow -version

# Run test
nextflow run workflows/main.nf -profile test
```

## Install R Packages (Optional)

For SoupX and Seurat integration:

```bash
# Start R
R

# Install packages
install.packages("Seurat")
install.packages("SoupX")
install.packages("BiocManager")
BiocManager::install("SingleCellExperiment")
```

## Docker Installation (Alternative)

```bash
# Pull Docker image
docker pull plantsc-analyzer:latest

# Run container
docker run -it -v $(pwd):/data plantsc-analyzer:latest
```

## HPC Setup

### SLURM

Edit `workflows/nextflow.config`:

```groovy
profiles {
    slurm {
        process.executor = 'slurm'
        process.queue = 'normal'
        process.clusterOptions = '--account=YOUR_ACCOUNT'
    }
}
```

### PBS

```groovy
profiles {
    pbs {
        process.executor = 'pbs'
        process.queue = 'batch'
    }
}
```

## Troubleshooting

### Issue: Nextflow not found

```bash
# Add to PATH
export PATH=$PATH:/path/to/nextflow
```

### Issue: GPU not detected

```bash
# Check CUDA
nvidia-smi

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Memory error

Increase memory in `nextflow.config`:

```groovy
process.memory = '128.GB'
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [User Guide](user_guide.md)
- [Tutorials](tutorials/)
