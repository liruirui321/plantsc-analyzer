#!/usr/bin/env nextflow

/*
 * PlantSC-Analyzer Main Workflow
 *
 * A modular single-cell RNA-seq analysis pipeline for plant xylem research
 *
 * Author: Cherry
 * Version: 0.1.0-alpha
 * License: MIT
 */

nextflow.enable.dsl=2

// Import modules
include { QC_WORKFLOW } from './modules/qc.nf'
include { NORMALIZE_WORKFLOW } from './modules/normalize.nf'
include { INTEGRATE_WORKFLOW } from './modules/integrate.nf'
include { CLUSTER_WORKFLOW } from './modules/cluster.nf'
include { ANNOTATE_WORKFLOW } from './modules/annotate.nf'
include { DOWNSTREAM_WORKFLOW } from './modules/downstream.nf'

// Print banner
def printBanner() {
    log.info """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🌱 PlantSC-Analyzer v${workflow.manifest.version}                    ║
    ║                                                           ║
    ║   Plant Single-Cell RNA-seq Analysis Pipeline            ║
    ║   Powered by Nextflow + Interactive Agent                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

    Project    : ${params.project_name}
    Species    : ${params.species}
    Tissue     : ${params.tissue}
    Samples    : ${params.samples.size()}
    Output Dir : ${params.outdir}

    Workflow Steps:
    ├── [1] Quality Control (QC)
    ├── [2] Normalization
    ├── [3] Batch Integration
    ├── [4] Clustering
    ├── [5] Cell Type Annotation
    └── [6] Downstream Analysis

    """.stripIndent()
}

// Main workflow
workflow {
    printBanner()

    // Create input channel from sample sheet
    Channel
        .fromPath(params.sample_sheet)
        .splitCsv(header: true)
        .map { row ->
            tuple(
                row.sample_id,
                file(row.matrix_path),
                row.batch,
                row.condition
            )
        }
        .set { samples_ch }

    // Step 1: Quality Control
    QC_WORKFLOW(samples_ch)

    // Step 2: Normalization
    NORMALIZE_WORKFLOW(QC_WORKFLOW.out.filtered_data)

    // Step 3: Batch Integration (if multiple batches)
    if (params.run_integration) {
        INTEGRATE_WORKFLOW(NORMALIZE_WORKFLOW.out.normalized_data)
        integrated_data = INTEGRATE_WORKFLOW.out.integrated_data
    } else {
        integrated_data = NORMALIZE_WORKFLOW.out.normalized_data
    }

    // Step 4: Clustering
    CLUSTER_WORKFLOW(integrated_data)

    // Step 5: Cell Type Annotation
    ANNOTATE_WORKFLOW(
        CLUSTER_WORKFLOW.out.clustered_data,
        params.marker_database
    )

    // Step 6: Downstream Analysis
    if (params.run_downstream) {
        DOWNSTREAM_WORKFLOW(ANNOTATE_WORKFLOW.out.annotated_data)
    }
}

// Workflow completion handler
workflow.onComplete {
    log.info """
    ╔═══════════════════════════════════════════════════════════╗
    ║   Pipeline Completed!                                     ║
    ╚═══════════════════════════════════════════════════════════╝

    Status      : ${workflow.success ? '✅ SUCCESS' : '❌ FAILED'}
    Duration    : ${workflow.duration}
    Results     : ${params.outdir}
    Report      : ${params.outdir}/pipeline_report.html

    """.stripIndent()
}

workflow.onError {
    log.error """
    ╔═══════════════════════════════════════════════════════════╗
    ║   Pipeline Failed!                                        ║
    ╚═══════════════════════════════════════════════════════════╝

    Error: ${workflow.errorMessage}

    Please check:
    1. Input files exist and are readable
    2. Configuration parameters are correct
    3. Sufficient compute resources available

    For help: https://github.com/YOUR_USERNAME/plantsc-analyzer/issues
    """.stripIndent()
}
