import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP()

# #############################################################################
# QIIME 2: tools plugin
# #############################################################################


@mcp.tool()
def qiime_tools_import(
    type: str,
    input_path: Path,
    output_path: Path,
    input_format: Optional[str] = None,
):
    """
    Import data into a QIIME 2 artifact.

    Args:
        type: The semantic type of the artifact to be created.
        input_path: Path to the file or directory to be imported.
        output_path: Path where the output artifact should be written.
        input_format: The format of the data to be imported. If not provided,
                      QIIME 2 will attempt to guess the format.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    cmd = [
        "qiime",
        "tools",
        "import",
        "--type",
        type,
        "--input-path",
        str(input_path),
        "--output-path",
        str(output_path),
    ]
    if input_format:
        cmd.extend(["--input-format", input_format])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(output_path)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_tools_export(input_path: Path, output_path: Path):
    """
    Export data from a QIIME 2 artifact.

    Args:
        input_path: Path to the artifact to be exported.
        output_path: Path to the directory where the artifact's data should be exported.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input artifact does not exist: {input_path}")

    cmd = [
        "qiime",
        "tools",
        "export",
        "--input-path",
        str(input_path),
        "--output-path",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        # The output is a directory, so we list its contents
        output_files = [str(p) for p in output_path.glob("**/*") if p.is_file()]
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_tools_inspect_metadata(metadata_path: Path):
    """
    Inspect columns and types in a metadata file.

    Args:
        metadata_path: Path to the metadata file to inspect.
    """
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file does not exist: {metadata_path}")

    cmd = ["qiime", "tools", "inspect-metadata", str(metadata_path)]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_tools_peek(artifact_path: Path):
    """
    Peek at a QIIME 2 artifact's UUID and type.

    Args:
        artifact_path: Path to the artifact to peek at.
    """
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact file does not exist: {artifact_path}")

    cmd = ["qiime", "tools", "peek", str(artifact_path)]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: metadata plugin
# #############################################################################


@mcp.tool()
def qiime_metadata_tabulate(
    m_input_file: Path, o_visualization: Path
):
    """
    Visualize metadata in a table.

    Args:
        m_input_file: The metadata file or artifact to tabulate.
        o_visualization: Path where the output visualization should be written.
    """
    if not m_input_file.exists():
        raise FileNotFoundError(f"Input file does not exist: {m_input_file}")

    cmd = [
        "qiime",
        "metadata",
        "tabulate",
        "--m-input-file",
        str(m_input_file),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: demux plugin
# #############################################################################


@mcp.tool()
def qiime_demux_summarize(i_data: Path, o_visualization: Path):
    """
    Summarize counts and quality of demultiplexed sequences.

    Args:
        i_data: The demultiplexed sequences to be summarized.
        o_visualization: Path where the output visualization should be written.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input data does not exist: {i_data}")

    cmd = [
        "qiime",
        "demux",
        "summarize",
        "--i-data",
        str(i_data),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: cutadapt plugin
# #############################################################################


@mcp.tool()
def qiime_cutadapt_trim_paired(
    i_demultiplexed_sequences: Path,
    o_trimmed_sequences: Path,
    p_front_f: str,
    p_front_r: str,
    p_cores: int = 1,
    p_overlap: Optional[int] = None,
    p_discard_untrimmed: bool = False,
    verbose: bool = False,
):
    """
    Trim adapters and primers from paired-end reads using cutadapt.

    Args:
        i_demultiplexed_sequences: The demultiplexed paired-end sequences to be trimmed.
        o_trimmed_sequences: Path where the output trimmed sequences should be written.
        p_front_f: Sequence of the 5' adapter on the forward reads.
        p_front_r: Sequence of the 5' adapter on the reverse reads.
        p_cores: Number of cores to use for processing.
        p_overlap: Minimum overlap between adapter and read for trimming.
        p_discard_untrimmed: Discard reads in which no adapter was found.
        verbose: Print details of the trimming process.
    """
    if not i_demultiplexed_sequences.exists():
        raise FileNotFoundError(
            f"Input sequences do not exist: {i_demultiplexed_sequences}"
        )

    cmd = [
        "qiime",
        "cutadapt",
        "trim-paired",
        "--i-demultiplexed-sequences",
        str(i_demultiplexed_sequences),
        "--o-trimmed-sequences",
        str(o_trimmed_sequences),
        "--p-front-f",
        p_front_f,
        "--p-front-r",
        p_front_r,
        "--p-cores",
        str(p_cores),
    ]
    if p_overlap is not None:
        cmd.extend(["--p-overlap", str(p_overlap)])
    if p_discard_untrimmed:
        cmd.append("--p-discard-untrimmed")
    if verbose:
        cmd.append("--verbose")

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_trimmed_sequences)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: dada2 plugin
# #############################################################################


@mcp.tool()
def qiime_dada2_denoise_paired(
    i_demultiplexed_seqs: Path,
    o_representative_sequences: Path,
    o_table: Path,
    o_denoising_stats: Path,
    p_trunc_len_f: int,
    p_trunc_len_r: int,
    p_n_threads: int = 1,
):
    """
    Denoise paired-end sequences using DADA2.

    Args:
        i_demultiplexed_seqs: The demultiplexed paired-end sequences.
        o_representative_sequences: Path for the output representative ASV sequences.
        o_table: Path for the output feature table.
        o_denoising_stats: Path for the output denoising statistics.
        p_trunc_len_f: Position to truncate forward reads. Reads shorter are discarded.
        p_trunc_len_r: Position to truncate reverse reads. Reads shorter are discarded.
        p_n_threads: Number of threads to use for processing.
    """
    if not i_demultiplexed_seqs.exists():
        raise FileNotFoundError(
            f"Input sequences do not exist: {i_demultiplexed_seqs}"
        )

    cmd = [
        "qiime",
        "dada2",
        "denoise-paired",
        "--i-demultiplexed-seqs",
        str(i_demultiplexed_seqs),
        "--o-representative-sequences",
        str(o_representative_sequences),
        "--o-table",
        str(o_table),
        "--o-denoising-stats",
        str(o_denoising_stats),
        "--p-trunc-len-f",
        str(p_trunc_len_f),
        "--p-trunc-len-r",
        str(p_trunc_len_r),
        "--p-n-threads",
        str(p_n_threads),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [
                str(o_representative_sequences),
                str(o_table),
                str(o_denoising_stats),
            ],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: feature-table plugin
# #############################################################################


@mcp.tool()
def qiime_feature_table_summarize(
    i_table: Path,
    o_visualization: Path,
    m_sample_metadata_file: Optional[Path] = None,
):
    """
    Summarize a feature table.

    Args:
        i_table: The feature table to be summarized.
        o_visualization: Path where the output visualization should be written.
        m_sample_metadata_file: Optional sample metadata file for additional details.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "feature-table",
        "summarize",
        "--i-table",
        str(i_table),
        "--o-visualization",
        str(o_visualization),
    ]
    if m_sample_metadata_file:
        if not m_sample_metadata_file.exists():
            raise FileNotFoundError(
                f"Metadata file does not exist: {m_sample_metadata_file}"
            )
        cmd.extend(
            ["--m-sample-metadata-file", str(m_sample_metadata_file)]
        )

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_feature_table_tabulate_seqs(i_data: Path, o_visualization: Path):
    """
    View feature sequences and blast them against NCBI nt database.

    Args:
        i_data: The feature sequences to tabulate.
        o_visualization: Path where the output visualization should be written.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input data does not exist: {i_data}")

    cmd = [
        "qiime",
        "feature-table",
        "tabulate-seqs",
        "--i-data",
        str(i_data),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_feature_table_filter_samples(
    i_table: Path,
    o_filtered_table: Path,
    m_metadata_file: Optional[Path] = None,
    p_where: Optional[str] = None,
    p_min_frequency: Optional[int] = None,
    p_min_features: Optional[int] = None,
):
    """
    Filter samples from a feature table.

    Args:
        i_table: The feature table from which samples will be filtered.
        o_filtered_table: Path where the output filtered table should be written.
        m_metadata_file: Sample metadata used for filtering.
        p_where: SQLite WHERE clause for filtering based on metadata.
        p_min_frequency: Minimum total frequency for a sample to be retained.
        p_min_features: Minimum number of features for a sample to be retained.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "feature-table",
        "filter-samples",
        "--i-table",
        str(i_table),
        "--o-filtered-table",
        str(o_filtered_table),
    ]
    if m_metadata_file:
        if not m_metadata_file.exists():
            raise FileNotFoundError(
                f"Metadata file does not exist: {m_metadata_file}"
            )
        cmd.extend(["--m-metadata-file", str(m_metadata_file)])
    if p_where:
        cmd.extend(["--p-where", p_where])
    if p_min_frequency is not None:
        cmd.extend(["--p-min-frequency", str(p_min_frequency)])
    if p_min_features is not None:
        cmd.extend(["--p-min-features", str(p_min_features)])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_table)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_feature_table_filter_features(
    i_table: Path,
    o_filtered_table: Path,
    p_min_frequency: Optional[int] = None,
    p_min_samples: Optional[int] = None,
):
    """
    Filter features from a feature table.

    Args:
        i_table: The feature table from which features will be filtered.
        o_filtered_table: Path where the output filtered table should be written.
        p_min_frequency: Minimum total frequency for a feature to be retained.
        p_min_samples: Minimum number of samples for a feature to be retained.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "feature-table",
        "filter-features",
        "--i-table",
        str(i_table),
        "--o-filtered-table",
        str(o_filtered_table),
    ]
    if p_min_frequency is not None:
        cmd.extend(["--p-min-frequency", str(p_min_frequency)])
    if p_min_samples is not None:
        cmd.extend(["--p-min-samples", str(p_min_samples)])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_table)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_feature_table_filter_seqs(
    i_data: Path, i_table: Path, o_filtered_data: Path
):
    """
    Filter sequences based on a feature table.

    Args:
        i_data: The feature sequences to be filtered.
        i_table: The feature table to filter sequences by.
        o_filtered_data: Path where the output filtered sequences should be written.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input sequences do not exist: {i_data}")
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "feature-table",
        "filter-seqs",
        "--i-data",
        str(i_data),
        "--i-table",
        str(i_table),
        "--o-filtered-data",
        str(o_filtered_data),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_data)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_feature_table_core_features(
    i_table: Path, o_feature_table: Path, p_fraction: float = 0.5
):
    """
    Identify core features in a feature table.

    Args:
        i_table: The feature table to identify core features from.
        o_feature_table: Path for the output table of core features.
        p_fraction: The fraction of samples a feature must be observed in to be core.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not 0.0 <= p_fraction <= 1.0:
        raise ValueError("p_fraction must be between 0.0 and 1.0")

    cmd = [
        "qiime",
        "feature-table",
        "core-features",
        "--i-table",
        str(i_table),
        "--o-feature-table",
        str(o_feature_table),
        "--p-fraction",
        str(p_fraction),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_feature_table)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: feature-classifier plugin
# #############################################################################


@mcp.tool()
def qiime_feature_classifier_classify_sklearn(
    i_reads: Path, i_classifier: Path, o_classification: Path
):
    """
    Classify sequences using a scikit-learn classifier.

    Args:
        i_reads: The sequences to be classified.
        i_classifier: The trained classifier for taxonomy assignment.
        o_classification: Path for the output taxonomic classifications.
    """
    if not i_reads.exists():
        raise FileNotFoundError(f"Input reads do not exist: {i_reads}")
    if not i_classifier.exists():
        raise FileNotFoundError(f"Classifier does not exist: {i_classifier}")

    cmd = [
        "qiime",
        "feature-classifier",
        "classify-sklearn",
        "--i-reads",
        str(i_reads),
        "--i-classifier",
        str(i_classifier),
        "--o-classification",
        str(o_classification),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_classification)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: taxa plugin
# #############################################################################


@mcp.tool()
def qiime_taxa_filter_table(
    i_table: Path,
    i_taxonomy: Path,
    o_filtered_table: Path,
    p_include: Optional[str] = None,
    p_exclude: Optional[str] = None,
    p_mode: str = "contains",
):
    """
    Filter a feature table based on taxonomy.

    Args:
        i_table: The feature table to be filtered.
        i_taxonomy: The feature taxonomy annotations.
        o_filtered_table: Path for the output filtered table.
        p_include: Comma-separated list of taxa to include.
        p_exclude: Comma-separated list of taxa to exclude.
        p_mode: Search mode for include/exclude terms.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not i_taxonomy.exists():
        raise FileNotFoundError(f"Taxonomy file does not exist: {i_taxonomy}")

    cmd = [
        "qiime",
        "taxa",
        "filter-table",
        "--i-table",
        str(i_table),
        "--i-taxonomy",
        str(i_taxonomy),
        "--o-filtered-table",
        str(o_filtered_table),
        "--p-mode",
        p_mode,
    ]
    if p_include:
        cmd.extend(["--p-include", p_include])
    if p_exclude:
        cmd.extend(["--p-exclude", p_exclude])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_table)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_taxa_barplot(
    i_table: Path,
    i_taxonomy: Path,
    m_metadata_file: Path,
    o_visualization: Path,
):
    """
    Create an interactive bar plot of taxonomic composition.

    Args:
        i_table: The feature table to visualize.
        i_taxonomy: The feature taxonomy annotations.
        m_metadata_file: Sample metadata for sorting and coloring.
        o_visualization: Path for the output visualization.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not i_taxonomy.exists():
        raise FileNotFoundError(f"Taxonomy file does not exist: {i_taxonomy}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "taxa",
        "barplot",
        "--i-table",
        str(i_table),
        "--i-taxonomy",
        str(i_taxonomy),
        "--m-metadata-file",
        str(m_metadata_file),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: phylogeny plugin
# #############################################################################


@mcp.tool()
def qiime_phylogeny_align_to_tree_mafft_fasttree(
    i_sequences: Path, output_dir: Path
):
    """
    Build a phylogenetic tree using a MAFFT-FastTree pipeline.

    Args:
        i_sequences: The sequences to align and use for tree construction.
        output_dir: Directory where the output artifacts will be written.
    """
    if not i_sequences.exists():
        raise FileNotFoundError(f"Input sequences do not exist: {i_sequences}")

    cmd = [
        "qiime",
        "phylogeny",
        "align-to-tree-mafft-fasttree",
        "--i-sequences",
        str(i_sequences),
        "--output-dir",
        str(output_dir),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        output_files = [
            str(p) for p in output_dir.glob("*") if p.is_file()
        ]
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: diversity plugin
# #############################################################################


@mcp.tool()
def qiime_diversity_alpha_rarefaction(
    i_table: Path,
    o_visualization: Path,
    p_max_depth: int,
    i_phylogeny: Optional[Path] = None,
    m_metadata_file: Optional[Path] = None,
):
    """
    Generate alpha rarefaction curves.

    Args:
        i_table: Feature table to compute rarefaction curves from.
        o_visualization: Path for the output visualization.
        p_max_depth: The maximum rarefaction depth.
        i_phylogeny: Optional phylogenetic tree for phylogenetic metrics.
        m_metadata_file: Optional sample metadata for grouping samples.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "diversity",
        "alpha-rarefaction",
        "--i-table",
        str(i_table),
        "--o-visualization",
        str(o_visualization),
        "--p-max-depth",
        str(p_max_depth),
    ]
    if i_phylogeny:
        if not i_phylogeny.exists():
            raise FileNotFoundError(f"Phylogeny file does not exist: {i_phylogeny}")
        cmd.extend(["--i-phylogeny", str(i_phylogeny)])
    if m_metadata_file:
        if not m_metadata_file.exists():
            raise FileNotFoundError(f"Metadata file does not exist: {m_metadata_file}")
        cmd.extend(["--m-metadata-file", str(m_metadata_file)])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_diversity_core_metrics_phylogenetic(
    i_table: Path,
    i_phylogeny: Path,
    p_sampling_depth: int,
    m_metadata_file: Path,
    output_dir: Path,
    p_n_jobs_or_threads: int = 1,
):
    """
    Compute core diversity metrics with phylogeny.

    Args:
        i_table: The feature table to compute metrics from.
        i_phylogeny: The phylogenetic tree for phylogenetic metrics.
        p_sampling_depth: The depth to rarefy the table to.
        m_metadata_file: Sample metadata for diversity calculations.
        output_dir: Directory where the output artifacts will be written.
        p_n_jobs_or_threads: Number of jobs or threads to use.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not i_phylogeny.exists():
        raise FileNotFoundError(f"Phylogeny file does not exist: {i_phylogeny}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "diversity",
        "core-metrics-phylogenetic",
        "--i-table",
        str(i_table),
        "--i-phylogeny",
        str(i_phylogeny),
        "--p-sampling-depth",
        str(p_sampling_depth),
        "--m-metadata-file",
        str(m_metadata_file),
        "--output-dir",
        str(output_dir),
        "--p-n-jobs-or-threads",
        str(p_n_jobs_or_threads),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        output_files = [
            str(p) for p in output_dir.glob("*") if p.is_file()
        ]
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_diversity_alpha_group_significance(
    i_alpha_diversity: Path, m_metadata_file: Path, o_visualization: Path
):
    """
    Test for significant differences in alpha diversity between groups.

    Args:
        i_alpha_diversity: Alpha diversity vector.
        m_metadata_file: Sample metadata for grouping.
        o_visualization: Path for the output visualization.
    """
    if not i_alpha_diversity.exists():
        raise FileNotFoundError(
            f"Alpha diversity file does not exist: {i_alpha_diversity}"
        )
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "diversity",
        "alpha-group-significance",
        "--i-alpha-diversity",
        str(i_alpha_diversity),
        "--m-metadata-file",
        str(m_metadata_file),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_diversity_beta_rarefaction(
    i_table: Path,
    p_metric: str,
    p_clustering_method: str,
    p_sampling_depth: int,
    m_metadata_file: Path,
    o_visualization: Path,
):
    """
    Generate beta rarefaction plots to assess stability of beta diversity.

    Args:
        i_table: Feature table to compute rarefaction from.
        p_metric: The beta diversity metric to use.
        p_clustering_method: The clustering method for the UPGMA tree.
        p_sampling_depth: The depth to rarefy the table to.
        m_metadata_file: Sample metadata for grouping.
        o_visualization: Path for the output visualization.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "diversity",
        "beta-rarefaction",
        "--i-table",
        str(i_table),
        "--p-metric",
        p_metric,
        "--p-clustering-method",
        p_clustering_method,
        "--p-sampling-depth",
        str(p_sampling_depth),
        "--m-metadata-file",
        str(m_metadata_file),
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_diversity_umap(i_distance_matrix: Path, o_umap: Path):
    """
    Perform Uniform Manifold Approximation and Projection (UMAP).

    Args:
        i_distance_matrix: The distance matrix to use for UMAP.
        o_umap: Path for the output UMAP results.
    """
    if not i_distance_matrix.exists():
        raise FileNotFoundError(
            f"Distance matrix does not exist: {i_distance_matrix}"
        )

    cmd = [
        "qiime",
        "diversity",
        "umap",
        "--i-distance-matrix",
        str(i_distance_matrix),
        "--o-umap",
        str(o_umap),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_umap)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_diversity_beta_group_significance(
    i_distance_matrix: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    o_visualization: Path,
    p_method: str = "permanova",
):
    """
    Test for significant differences in beta diversity between groups.

    Args:
        i_distance_matrix: The distance matrix to test.
        m_metadata_file: Sample metadata for grouping.
        m_metadata_column: The metadata column to test for significance.
        o_visualization: Path for the output visualization.
        p_method: The statistical method to use ('permanova' or 'permdisp').
    """
    if not i_distance_matrix.exists():
        raise FileNotFoundError(
            f"Distance matrix does not exist: {i_distance_matrix}"
        )
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "diversity",
        "beta-group-significance",
        "--i-distance-matrix",
        str(i_distance_matrix),
        "--m-metadata-file",
        str(m_metadata_file),
        "--m-metadata-column",
        m_metadata_column,
        "--o-visualization",
        str(o_visualization),
        "--p-method",
        p_method,
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: emperor plugin
# #############################################################################


@mcp.tool()
def qiime_emperor_plot(
    i_pcoa: Path,
    m_metadata_file: List[Path],
    o_visualization: Path,
    p_custom_axes: Optional[str] = None,
):
    """
    Visualize PCoA, UMAP, or other ordination results with Emperor.

    Args:
        i_pcoa: The ordination matrix to visualize.
        m_metadata_file: List of sample metadata files for coloring/shaping points.
        o_visualization: Path for the output Emperor plot.
        p_custom_axes: Metadata columns to use as custom axes in the plot.
    """
    if not i_pcoa.exists():
        raise FileNotFoundError(f"PCoA file does not exist: {i_pcoa}")

    cmd = [
        "qiime",
        "emperor",
        "plot",
        "--i-pcoa",
        str(i_pcoa),
        "--o-visualization",
        str(o_visualization),
    ]
    for meta_file in m_metadata_file:
        if not meta_file.exists():
            raise FileNotFoundError(f"Metadata file does not exist: {meta_file}")
        cmd.extend(["--m-metadata-file", str(meta_file)])
    if p_custom_axes:
        cmd.extend(["--p-custom-axes", p_custom_axes])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: longitudinal plugin
# #############################################################################


@mcp.tool()
def qiime_longitudinal_linear_mixed_effects(
    m_metadata_file: List[Path],
    p_state_column: str,
    p_individual_id_column: str,
    p_metric: str,
    o_visualization: Path,
):
    """
    Run a linear mixed effects model for longitudinal data.

    Args:
        m_metadata_file: List of metadata files containing the data for the model.
        p_state_column: The metadata column containing the state or time variable.
        p_individual_id_column: The metadata column identifying individual subjects.
        p_metric: The dependent variable metric (e.g., an alpha diversity measure).
        o_visualization: Path for the output visualization of model results.
    """
    cmd = [
        "qiime",
        "longitudinal",
        "linear-mixed-effects",
        "--p-state-column",
        p_state_column,
        "--p-individual-id-column",
        p_individual_id_column,
        "--p-metric",
        p_metric,
        "--o-visualization",
        str(o_visualization),
    ]
    for meta_file in m_metadata_file:
        if not meta_file.exists():
            raise FileNotFoundError(f"Metadata file does not exist: {meta_file}")
        cmd.extend(["--m-metadata-file", str(meta_file)])

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: composition plugin
# #############################################################################


@mcp.tool()
def qiime_composition_add_pseudocount(
    i_table: Path, o_composition_table: Path
):
    """
    Add a pseudocount to a feature table to handle zeros.

    Args:
        i_table: The feature table to add pseudocounts to.
        o_composition_table: Path for the output composition table.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")

    cmd = [
        "qiime",
        "composition",
        "add-pseudocount",
        "--i-table",
        str(i_table),
        "--o-composition-table",
        str(o_composition_table),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_composition_table)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def qiime_composition_ancom(
    i_table: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    o_visualization: Path,
):
    """
    Perform ANCOM differential abundance testing.

    Args:
        i_table: The composition table for ANCOM analysis.
        m_metadata_file: Sample metadata for grouping.
        m_metadata_column: The metadata column to test for differential abundance.
        o_visualization: Path for the output ANCOM results visualization.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "composition",
        "ancom",
        "--i-table",
        str(i_table),
        "--m-metadata-file",
        str(m_metadata_file),
        "--m-metadata-column",
        m_metadata_column,
        "--o-visualization",
        str(o_visualization),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: sample-classifier plugin
# #############################################################################


@mcp.tool()
def qiime_sample_classifier_classify_samples(
    i_table: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    output_dir: Path,
    p_estimator: str = "RandomForestClassifier",
    p_random_state: Optional[int] = None,
    p_optimize_feature_selection: bool = False,
    p_parameter_tuning: bool = False,
):
    """
    Train and test a supervised learning classifier on sample data.

    Args:
        i_table: Feature table containing sample data.
        m_metadata_file: Sample metadata file.
        m_metadata_column: The metadata column to predict.
        output_dir: Directory where the output artifacts will be written.
        p_estimator: The scikit-learn estimator to use.
        p_random_state: Seed for random number generator.
        p_optimize_feature_selection: Enable recursive feature elimination.
        p_parameter_tuning: Enable hyperparameter tuning.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input table does not exist: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist: {m_metadata_file}"
        )

    cmd = [
        "qiime",
        "sample-classifier",
        "classify-samples",
        "--i-table",
        str(i_table),
        "--m-metadata-file",
        str(m_metadata_file),
        "--m-metadata-column",
        m_metadata_column,
        "--output-dir",
        str(output_dir),
        "--p-estimator",
        p_estimator,
    ]
    if p_random_state is not None:
        cmd.extend(["--p-random-state", str(p_random_state)])
    if p_optimize_feature_selection:
        cmd.append("--p-optimize-feature-selection")
    if p_parameter_tuning:
        cmd.append("--p-parameter-tuning")

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        output_files = [
            str(p) for p in output_dir.glob("*") if p.is_file()
        ]
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


# #############################################################################
# QIIME 2: fragment-insertion plugin
# #############################################################################


@mcp.tool()
def qiime_fragment_insertion_sepp(
    i_representative_sequences: Path,
    i_reference_database: Path,
    o_tree: Path,
    o_placements: Path,
    p_threads: int = 1,
):
    """
    Insert fragments into a reference tree using SEPP.

    Args:
        i_representative_sequences: The sequences to insert into the tree.
        i_reference_database: The SEPP reference database.
        o_tree: Path for the output insertion tree.
        o_placements: Path for the output placement metadata.
        p_threads: Number of threads to use.
    """
    if not i_representative_sequences.exists():
        raise FileNotFoundError(
            f"Representative sequences do not exist: {i_representative_sequences}"
        )
    if not i_reference_database.exists():
        raise FileNotFoundError(
            f"Reference database does not exist: {i_reference_database}"
        )

    cmd = [
        "qiime",
        "fragment-insertion",
        "sepp",
        "--i-representative-sequences",
        str(i_representative_sequences),
        "--i-reference-database",
        str(i_reference_database),
        "--o-tree",
        str(o_tree),
        "--o-placements",
        str(o_placements),
        "--p-threads",
        str(p_threads),
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_tree), str(o_placements)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


if __name__ == "__main__":
    mcp.run()