#!/usr/bin/env nextflow

/*
 * Clustering Workflow Module
 */

process CLUSTER {
    label 'medium_cpu'
    publishDir "${params.outdir}/04_cluster", mode: 'copy'

    input:
    path(adata)

    output:
    path "clustered.h5ad", emit: clustered
    path "cluster_assignments.csv", emit: assignments
    path "*_pca_elbow.pdf", emit: pca_plot
    path "*_umap_resolutions.pdf", emit: umap_plot
    path "*_cluster_sizes.pdf", emit: size_plot

    script:
    def resolutions = params.cluster.resolution.join(' ')
    """
    python ${projectDir}/../scripts/04_cluster/cluster.py \\
        --input ${adata} \\
        --sample_id ${params.project_name} \\
        --n_pcs ${params.cluster.n_pcs} \\
        --n_neighbors ${params.cluster.n_neighbors} \\
        --resolution ${resolutions} \\
        --algorithm ${params.cluster.algorithm} \\
        --metric ${params.cluster.metric} \\
        --output clustered.h5ad \\
        --clusters_csv cluster_assignments.csv \\
        --plot_dir ./
    """
}

workflow CLUSTER_WORKFLOW {
    take:
    integrated_data  // path to integrated h5ad

    main:
    CLUSTER(integrated_data)

    emit:
    clustered_data = CLUSTER.out.clustered
    cluster_assignments = CLUSTER.out.assignments
}
