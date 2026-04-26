# PlantSC-Analyzer Docker Image
# Multi-stage build for optimized image size

FROM continuumio/miniconda3:latest AS builder

LABEL maintainer="Cherry"
LABEL description="Plant single-cell RNA-seq analysis pipeline"
LABEL version="0.1.0-alpha"

# Set working directory
WORKDIR /opt/plantsc-analyzer

# Copy environment file
COPY envs/environment.yml .

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Install additional tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Final stage
FROM continuumio/miniconda3:latest

WORKDIR /opt/plantsc-analyzer

# Copy conda environment from builder
COPY --from=builder /opt/conda/envs/plantsc /opt/conda/envs/plantsc

# Copy project files
COPY workflows/ ./workflows/
COPY scripts/ ./scripts/
COPY agent/ ./agent/
COPY knowledge_base/ ./knowledge_base/
COPY configs/ ./configs/
COPY README.md LICENSE ./

# Set environment
ENV PATH="/opt/conda/envs/plantsc/bin:${PATH}"
ENV PYTHONPATH="/opt/plantsc-analyzer:${PYTHONPATH}"

# Activate conda environment
SHELL ["conda", "run", "-n", "plantsc", "/bin/bash", "-c"]

# Set entrypoint
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "plantsc"]
CMD ["nextflow", "run", "workflows/main.nf", "--help"]

# Expose ports (if needed for web interface in future)
# EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD conda run -n plantsc python -c "import scanpy; import nextflow" || exit 1

# Metadata
LABEL org.opencontainers.image.source="https://github.com/liruirui321/plantsc-analyzer"
LABEL org.opencontainers.image.documentation="https://github.com/liruirui321/plantsc-analyzer/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"
