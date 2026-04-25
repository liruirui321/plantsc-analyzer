#!/usr/bin/env nextflow

/*
 * Downstream Analysis Workflow Module
 */

process DEG_ANALYSIS {
    label 'medium_cpu'
    publishDir "${params.outdir}/06_downstream/deg", mode: 'copy'

    input:
    path(adata)

    output:
    path "deg_*.csv", emit: deg_results
    path "deg_volcano_*.pdf", emit: volcano_plots

    when:
    params.downstream.deg.run

    script:
    """
    python ${projectDir}/../scripts/06_downstream/deg_analysis.py \\
        --input ${adata} \\
        --group_key cell_type \\
        --method ${params.downstream.deg.method} \\
        --min_pct ${params.downstream.deg.min_pct} \\
        --logfc_threshold ${params.downstream.deg.logfc_threshold} \\
        --output_dir ./
    """
}

process ENRICHMENT_ANALYSIS {
    label 'low_cpu'
    publishDir "${params.outdir}/06_downstream/enrichment", mode: 'copy'

    input:
    path(deg_csv)

    output:
    path "enrichment_*.csv", emit: enrichment_results
    path "enrichment_*.pdf", emit: enrichment_plots

    when:
    params.downstream.enrichment.run

    script:
    """
    python ${projectDir}/../scripts/06_downstream/enrichment.py \\
        --input ${deg_csv} \\
        --organism ${params.downstream.enrichment.organism} \\
        --databases ${params.downstream.enrichment.databases.join(' ')} \\
        --output_dir ./
    """
}

process TRAJECTORY_ANALYSIS {
    label 'medium_cpu'
    publishDir "${params.outdir}/06_downstream/trajectory", mode: 'copy'

    input:
    path(adata)

    output:
    path "trajectory.h5ad", emit: trajectory_adata
    path "trajectory_*.pdf", emit: trajectory_plots

    when:
    params.downstream.trajectory.run

    script:
    def root_cell_type = params.downstream.trajectory.root_cell_type ?: 'null'
    """
    python ${projectDir}/../scripts/06_downstream/trajectory.py \\
        --input ${adata} \\
        --method ${params.downstream.trajectory.method} \\
        --root_cell_type ${root_cell_type} \\
        --output trajectory.h5ad \\
        --plot_dir ./
    """
}

workflow DOWNSTREAM_WORKFLOW {
    take:
    annotated_data  // path to annotated h5ad

    main:
    // DEG analysis
    if (params.downstream.deg.run) {
        DEG_ANALYSIS(annotated_data)
        deg_results = DEG_ANALYSIS.out.deg_results

        // Enrichment analysis
        if (params.downstream.enrichment.run) {
            ENRICHMENT_ANALYSIS(deg_results)
        }
    }

    // Trajectory analysis
    if (params.downstream.trajectory.run) {
        TRAJECTORY_ANALYSIS(annotated_data)
    }

    emit:
    deg_results = params.downstream.deg.run ? DEG_ANALYSIS.out.deg_results : Channel.empty()
    trajectory_data = params.downstream.trajectory.run ? TRAJECTORY_ANALYSIS.out.trajectory_adata : Channel.empty()
}
