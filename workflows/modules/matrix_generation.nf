#!/usr/bin/env nextflow

/*
 * Step 0: Platform Detection & Matrix Generation
 * Supports: BGI (dnbc4tools) and 10X (CellRanger)
 */

process DETECT_PLATFORM {
    label 'low_cpu'

    input:
    tuple val(sample_id), path(fastq_dir), val(batch), val(condition)

    output:
    tuple val(sample_id), val(platform), path(fastq_dir), val(batch), val(condition), emit: detected

    script:
    """
    python ${projectDir}/../scripts/00_matrix_generation/detect_platform.py \\
        --fastq_dir ${fastq_dir} \\
        --sample_id ${sample_id} \\
        --output platform_info.txt

    platform=\$(cat platform_info.txt)
    echo \$platform > platform.txt
    """
}

process TRIM_BGI_OLIGO {
    label 'medium_cpu'
    publishDir "${params.outdir}/00_matrix/trimmed_oligo", mode: 'copy'

    input:
    tuple val(sample_id), path(oligo1), path(oligo2), val(kit_version)

    output:
    tuple val(sample_id), path("${sample_id}_oligo1_trim.fastq.gz"), path("${sample_id}_oligo2_trim.fastq.gz"), emit: trimmed

    when:
    kit_version == 'V2.0' || kit_version == 'V2.5'

    script:
    """
    python ${projectDir}/../scripts/00_matrix_generation/trim_bgi_oligo.py \\
        ${oligo1} \\
        ${oligo2} \\
        ./
    """
}

process RUN_DNBC4TOOLS {
    label 'high_cpu'
    publishDir "${params.outdir}/00_matrix/bgi_${sample_id}", mode: 'copy'

    input:
    tuple val(sample_id), path(read1), path(read2), path(oligo1), path(oligo2), path(genome), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}/filter_matrix"), val(batch), val(condition), emit: matrix
    path "${sample_id}/report.html", emit: report

    script:
    def oligo1_input = oligo1.name != 'NO_FILE' ? "--oligo1 ${oligo1}" : ""
    def oligo2_input = oligo2.name != 'NO_FILE' ? "--oligo2 ${oligo2}" : ""
    """
    dnbc4tools run \\
        --cDNAfastq1 ${read1} \\
        --cDNAfastq2 ${read2} \\
        ${oligo1_input} \\
        ${oligo2_input} \\
        --genomeDir ${genome} \\
        --name ${sample_id} \\
        --threads ${task.cpus}
    """
}

process RUN_CELLRANGER {
    label 'high_cpu'
    publishDir "${params.outdir}/00_matrix/10x_${sample_id}", mode: 'copy'

    input:
    tuple val(sample_id), path(fastq_dir), path(genome), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}/outs/filtered_feature_bc_matrix"), val(batch), val(condition), emit: matrix
    path "${sample_id}/outs/web_summary.html", emit: report

    script:
    """
    cellranger count \\
        --id=${sample_id} \\
        --transcriptome=${genome} \\
        --fastqs=${fastq_dir} \\
        --sample=${sample_id} \\
        --localcores=${task.cpus} \\
        --localmem=${task.memory.toGiga()}
    """
}

process CONVERT_TO_H5AD {
    label 'low_cpu'
    publishDir "${params.outdir}/00_matrix/h5ad", mode: 'copy'

    input:
    tuple val(sample_id), path(matrix_dir), val(batch), val(condition)

    output:
    tuple val(sample_id), path("${sample_id}.h5ad"), val(batch), val(condition), emit: h5ad

    script:
    """
    python ${projectDir}/../scripts/00_matrix_generation/convert_to_h5ad.py \\
        --matrix_dir ${matrix_dir} \\
        --sample_id ${sample_id} \\
        --batch ${batch} \\
        --condition ${condition} \\
        --output ${sample_id}.h5ad
    """
}

workflow MATRIX_GENERATION {
    take:
    raw_data_ch  // tuple(sample_id, fastq_dir, batch, condition, platform, kit_version, genome)

    main:
    // Split by platform
    raw_data_ch
        .branch {
            bgi: it[4] == 'BGI'
            tenx: it[4] == '10X'
        }
        .set { platform_split }

    // BGI pipeline
    bgi_data = platform_split.bgi
        .map { sample_id, fastq_dir, batch, condition, platform, kit_version, genome ->
            // Find FASTQ files
            def read1 = file("${fastq_dir}/*_1.fq.gz")
            def read2 = file("${fastq_dir}/*_2.fq.gz")
            def oligo1 = file("${fastq_dir}/*oligo*_1.fq.gz", checkIfExists: false)
            def oligo2 = file("${fastq_dir}/*oligo*_2.fq.gz", checkIfExists: false)

            tuple(sample_id, read1, read2, oligo1 ?: file('NO_FILE'), oligo2 ?: file('NO_FILE'),
                  kit_version, genome, batch, condition)
        }

    // Trim oligo if V2.0/V2.5
    bgi_data
        .filter { it[5] in ['V2.0', 'V2.5'] && it[3].name != 'NO_FILE' }
        .map { sample_id, r1, r2, o1, o2, kit, genome, batch, cond ->
            tuple(sample_id, o1, o2, kit)
        }
        .set { oligo_to_trim }

    if (oligo_to_trim) {
        TRIM_BGI_OLIGO(oligo_to_trim)
        trimmed_oligo = TRIM_BGI_OLIGO.out.trimmed
    } else {
        trimmed_oligo = Channel.empty()
    }

    // Merge trimmed and non-trimmed
    bgi_data
        .join(trimmed_oligo, by: 0, remainder: true)
        .map { sample_id, r1, r2, o1_old, o2_old, kit, genome, batch, cond, o1_new, o2_new ->
            def o1_final = o1_new ?: o1_old
            def o2_final = o2_new ?: o2_old
            tuple(sample_id, r1, r2, o1_final, o2_final, genome, batch, cond)
        }
        .set { bgi_ready }

    RUN_DNBC4TOOLS(bgi_ready)
    bgi_matrix = RUN_DNBC4TOOLS.out.matrix

    // 10X pipeline
    tenx_data = platform_split.tenx
        .map { sample_id, fastq_dir, batch, condition, platform, kit_version, genome ->
            tuple(sample_id, fastq_dir, genome, batch, condition)
        }

    RUN_CELLRANGER(tenx_data)
    tenx_matrix = RUN_CELLRANGER.out.matrix

    // Merge both platforms
    all_matrix = bgi_matrix.mix(tenx_matrix)

    // Convert to h5ad
    CONVERT_TO_H5AD(all_matrix)

    emit:
    h5ad = CONVERT_TO_H5AD.out.h5ad
    bgi_reports = RUN_DNBC4TOOLS.out.report
    tenx_reports = RUN_CELLRANGER.out.report
}
