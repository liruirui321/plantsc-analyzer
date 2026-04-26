#!/usr/bin/env nextflow

/*
 * Annotation Workflow Module
 */

process ANNOTATE {
    label 'medium_cpu'
    publishDir "${params.outdir}/05_annotate", mode: 'copy'

    input:
    path(adata)
    path(marker_db)

    output:
    path "annotated.h5ad", emit: annotated
    path "cell_type_annotation.csv", emit: annotation_csv
    path "*_annotation_umap.pdf", emit: umap_plot
    path "*_annotation_confidence.pdf", emit: confidence_plot

    script:
    """
    python ${projectDir}/../scripts/05_annotate/annotate.py \\
        --input ${adata} \\
        --sample_id ${params.project_name} \\
        --markers ${marker_db} \\
        --cluster_key cluster \\
        --confidence_threshold ${params.annotation.confidence_threshold} \\
        --output annotated.h5ad \\
        --annotation_csv cell_type_annotation.csv \\
        --plot_dir ./
    """
}

process DEG_PER_CLUSTER {
    label 'medium_cpu'
    publishDir "${params.outdir}/05_annotate/deg", mode: 'copy'

    input:
    path(adata)

    output:
    path "deg_results.csv", emit: deg_csv
    path "top_markers_per_cluster.csv", emit: top_markers

    script:
    """
    python ${projectDir}/../scripts/05_annotate/deg_per_cluster.py \\
        --input ${adata} \\
        --cluster_key cluster \\
        --method wilcoxon \\
        --output deg_results.csv \\
        --top_markers top_markers_per_cluster.csv
    """
}

process LLM_ANNOTATE {
    label 'medium_cpu'
    publishDir "${params.outdir}/05_annotate/llm", mode: 'copy'

    input:
    path(adata)

    output:
    path "llm_annotations.csv", emit: llm_csv
    path "llm_annotation_report.txt", emit: report

    when:
    params.annotation.use_llm == true

    script:
    def api_key_arg = params.annotation.llm_api_key ? "--api_key ${params.annotation.llm_api_key}" : ""
    """
    python ${projectDir}/../scripts/05_annotate/llm_annotate.py \\
        --input ${adata} \\
        --output llm_annotations.csv \\
        --cluster_key cluster \\
        --n_genes ${params.annotation.llm_n_genes} \\
        --species "${params.species}" \\
        --tissue "${params.tissue}" \\
        --model ${params.annotation.llm_model} \\
        --provider ${params.annotation.llm_provider} \\
        ${api_key_arg} \\
        > llm_annotation_report.txt 2>&1
    """
}

workflow ANNOTATE_WORKFLOW {
    take:
    clustered_data  // path to clustered h5ad
    marker_database // path to marker CSV

    main:
    ANNOTATE(clustered_data, marker_database)
    DEG_PER_CLUSTER(ANNOTATE.out.annotated)

    emit:
    annotated_data = ANNOTATE.out.annotated
    annotation_csv = ANNOTATE.out.annotation_csv
    deg_results = DEG_PER_CLUSTER.out.deg_csv
}
