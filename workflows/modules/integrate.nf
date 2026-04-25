#!/usr/bin/env nextflow

/*
 * Batch Integration Workflow Module
 * Methods: Harmony, scVI, Scanorama
 */

process HARMONY_INTEGRATION {
    label 'medium_cpu'
    publishDir "${params.outdir}/03_integrate", mode: 'copy'

    input:
    path(adata)

    output:
    path "${adata.baseName}_harmony.h5ad", emit: integrated
    path "harmony_integration_report.pdf", emit: report

    script:
    """
    python ${projectDir}/../scripts/03_integrate/harmony_integration.py \\
        --input ${adata} \\
        --batch_key ${params.integration.batch_key} \\
        --n_pcs ${params.integration.harmony.n_pcs} \\
        --output ${adata.baseName}_harmony.h5ad \\
        --plot_dir ./
    """
}

process SCVI_INTEGRATION {
    label 'high_cpu'
    publishDir "${params.outdir}/03_integrate", mode: 'copy'

    input:
    path(adata)

    output:
    path "${adata.baseName}_scvi.h5ad", emit: integrated
    path "scvi_integration_report.pdf", emit: report

    script:
    """
    python ${projectDir}/../scripts/03_integrate/scvi_integration.py \\
        --input ${adata} \\
        --batch_key ${params.integration.batch_key} \\
        --n_latent ${params.integration.scvi.n_latent} \\
        --n_layers ${params.integration.scvi.n_layers} \\
        --n_epochs ${params.integration.scvi.n_epochs} \\
        --output ${adata.baseName}_scvi.h5ad \\
        --plot_dir ./
    """
}

workflow INTEGRATE_WORKFLOW {
    take:
    normalized_data  // path to merged h5ad

    main:
    if (params.integration.method == 'harmony') {
        HARMONY_INTEGRATION(normalized_data)
        integrated = HARMONY_INTEGRATION.out.integrated
    } else if (params.integration.method == 'scvi') {
        SCVI_INTEGRATION(normalized_data)
        integrated = SCVI_INTEGRATION.out.integrated
    } else {
        // Default to harmony
        HARMONY_INTEGRATION(normalized_data)
        integrated = HARMONY_INTEGRATION.out.integrated
    }

    emit:
    integrated_data = integrated
}
