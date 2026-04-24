#!/usr/bin/env nextflow

/*
 * QC Workflow Module
 * Includes: SoupX, Scrublet, filtering
 */

process SOUPX {
    label 'medium_cpu'
    publishDir "${params.outdir}/01_qc/soupx", mode: 'copy'

    input:
    tuple val(sample_id), path(matrix), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}_soupx_corrected.h5ad"), val(batch), val(condition), emit: corrected
    tuple val(sample_id), path("${sample_id}_before_soupx.h5ad"), emit: before_soupx
    path "${sample_id}_soupx_report.txt", emit: report

    script:
    """
    # Save original matrix before SoupX
    cp ${matrix} ${sample_id}_before_soupx.h5ad

    # Run SoupX correction
    python ${projectDir}/../scripts/01_qc/soupx.py \\
        --sample_id ${sample_id} \\
        --matrix ${matrix} \\
        --min_genes ${params.qc.min_genes} \\
        --output ${sample_id}_soupx_corrected.h5ad \\
        --report ${sample_id}_soupx_report.txt
    """
}

process SCRUBLET {
    label 'medium_cpu'
    publishDir "${params.outdir}/01_qc/scrublet", mode: 'copy'

    input:
    tuple val(sample_id), path(adata), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}_scrublet.h5ad"), val(batch), val(condition), emit: filtered
    path "${sample_id}_doublet_scores.csv", emit: scores

    script:
    """
    python ${projectDir}/../scripts/01_qc/scrublet.py \\
        --input ${adata} \\
        --sample_id ${sample_id} \\
        --threshold ${params.qc.doublet_threshold} \\
        --output ${sample_id}_scrublet.h5ad \\
        --scores ${sample_id}_doublet_scores.csv
    """
}

process FILTER_CELLS {
    label 'low_cpu'
    publishDir "${params.outdir}/01_qc/filtered", mode: 'copy'

    input:
    tuple val(sample_id), path(adata), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}_filtered.h5ad"), val(batch), val(condition), emit: filtered
    path "${sample_id}_qc_metrics.csv", emit: metrics

    script:
    """
    python ${projectDir}/../scripts/01_qc/filter_cells.py \\
        --input ${adata} \\
        --sample_id ${sample_id} \\
        --min_genes ${params.qc.min_genes} \\
        --max_genes ${params.qc.max_genes} \\
        --min_cells ${params.qc.min_cells} \\
        --mito_threshold ${params.qc.mito_threshold} \\
        --output ${sample_id}_filtered.h5ad \\
        --metrics ${sample_id}_qc_metrics.csv
    """
}

process QC_REPORT {
    label 'low_cpu'
    publishDir "${params.outdir}/01_qc", mode: 'copy'

    input:
    path(metrics_files)

    output:
    path "qc_summary_report.html"

    script:
    """
    python ${projectDir}/../scripts/01_qc/qc_report.py \\
        --metrics ${metrics_files} \\
        --output qc_summary_report.html
    """
}

workflow QC_WORKFLOW {
    take:
    samples_ch

    main:
    // Run SoupX if enabled
    if (params.qc.run_soupx) {
        SOUPX(samples_ch)
        soupx_out = SOUPX.out.corrected
    } else {
        soupx_out = samples_ch
    }

    // Run Scrublet if enabled
    if (params.qc.run_scrublet) {
        SCRUBLET(soupx_out)
        scrublet_out = SCRUBLET.out.filtered
    } else {
        scrublet_out = soupx_out
    }

    // Filter cells
    FILTER_CELLS(scrublet_out)

    // Generate QC report
    QC_REPORT(FILTER_CELLS.out.metrics.collect())

    emit:
    filtered_data = FILTER_CELLS.out.filtered
}
