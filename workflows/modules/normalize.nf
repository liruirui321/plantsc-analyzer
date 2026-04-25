#!/usr/bin/env nextflow

/*
 * Normalization Workflow Module
 */

process NORMALIZE {
    label 'medium_cpu'
    publishDir "${params.outdir}/02_normalize", mode: 'copy'

    input:
    tuple val(sample_id), path(adata), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}_normalized.h5ad"), val(batch), val(condition), emit: normalized
    path "${sample_id}_hvg_list.csv", emit: hvg_list
    path "${sample_id}_normalization_qc.pdf", emit: qc_plot

    script:
    def batch_key = params.normalize.hvg_batch_key ?: 'null'
    """
    python ${projectDir}/../scripts/02_normalize/normalize.py \\
        --input ${adata} \\
        --sample_id ${sample_id} \\
        --method ${params.normalize.method} \\
        --target_sum ${params.normalize.target_sum} \\
        --n_top_genes ${params.normalize.n_hvg} \\
        --hvg_flavor ${params.normalize.hvg_flavor} \\
        --batch_key ${batch_key} \\
        --scale \\
        --output ${sample_id}_normalized.h5ad \\
        --hvg_list ${sample_id}_hvg_list.csv \\
        --plot_dir ./
    """
}

process MERGE_SAMPLES {
    label 'medium_cpu'
    publishDir "${params.outdir}/02_normalize", mode: 'copy'

    input:
    path(adata_files)

    output:
    path "merged_normalized.h5ad", emit: merged

    script:
    """
    python ${projectDir}/../scripts/02_normalize/merge_samples.py \\
        --inputs ${adata_files} \\
        --output merged_normalized.h5ad
    """
}

workflow NORMALIZE_WORKFLOW {
    take:
    filtered_data  // tuple(sample_id, path, batch, condition)

    main:
    // Normalize each sample
    NORMALIZE(filtered_data)

    // Merge all samples if multiple
    all_normalized = NORMALIZE.out.normalized.map { it[1] }.collect()

    if (all_normalized.size() > 1) {
        MERGE_SAMPLES(all_normalized)
        merged_data = MERGE_SAMPLES.out.merged
    } else {
        merged_data = all_normalized
    }

    emit:
    normalized_data = merged_data
    hvg_lists = NORMALIZE.out.hvg_list
    qc_plots = NORMALIZE.out.qc_plot
}
