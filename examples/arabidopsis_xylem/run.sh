#!/bin/bash

# Example: Run PlantSC-Analyzer for Arabidopsis xylem samples

# Activate conda environment
conda activate plantsc

# Run with interactive agent
python ../../agent/plant_sc_agent.py \
    --config config.yaml \
    --mode interactive

# Or run Nextflow directly (non-interactive)
# nextflow run ../../workflows/main.nf \
#     -c config.yaml \
#     -profile slurm \
#     -resume
