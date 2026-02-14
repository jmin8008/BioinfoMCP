import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List

from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def qiime_tools_validate(
    metadata_paths: List[Path],
) -> dict:
    """
    Inspects QIIME 2 metadata file(s) for validity and provides a summary.
    This function corresponds to the 'qiime tools inspect-metadata' command.
    """
    command = ["qiime", "tools", "inspect-metadata"]
    
    for path in metadata_paths:
        if not path.exists():
            raise FileNotFoundError(f"Metadata file not found: {path}")
        command.append(str(path))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": " ".join(command),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(command),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 inspect-metadata failed with exit code {e.returncode}",
            "output_files": []
        }

@mcp.tool()
def qiime_tools_import(
    type: str,
    input_path: Path,
    output_path: str,
    input_format: Optional[str] = None,
) -> dict:
    """
    Imports data into a QIIME 2 artifact (.qza). This corresponds to 'qiime tools import'.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / output_path
        
        command = [
            "qiime", "tools", "import",
            "--type", type,
            "--input-path", str(input_path),
            "--output-path", str(output_file)
        ]
        if input_format:
            command.extend(["--input-format", input_format])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            # The output file is the artifact itself
            final_output_path = Path.cwd() / output_path
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully imported artifact.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 import failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_tools_export(
    input_path: Path,
    output_path: str,
) -> dict:
    """
    Exports data from a QIIME 2 artifact. This corresponds to 'qiime tools export'.
    The output path is a directory where the contents will be exported.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input artifact not found: {input_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_dir = Path(temp_dir) / "export_dir"
        
        command = [
            "qiime", "tools", "export",
            "--input-path", str(input_path),
            "--output-path", str(temp_output_dir)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_dir = Path.cwd() / output_path
            if final_output_dir.exists():
                shutil.rmtree(final_output_dir)
            shutil.move(temp_output_dir, final_output_dir)
            
            exported_files = [str(p) for p in final_output_dir.rglob('*')]

            return {
                "command_executed": " ".join(command),
                "stdout": f"Successfully exported artifact to {final_output_dir}",
                "stderr": "",
                "output_files": exported_files
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 export failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_tools_peek(
    artifact_path: Path,
) -> dict:
    """
    Peeks at a QIIME 2 artifact's metadata (UUID, type, format). Corresponds to 'qiime tools peek'.
    """
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact file not found: {artifact_path}")

    command = ["qiime", "tools", "peek", str(artifact_path)]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": " ".join(command),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(command),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 peek failed with exit code {e.returncode}",
            "output_files": []
        }

@mcp.tool()
def qiime_metadata_tabulate(
    m_input_file: Path,
    o_visualization: str,
) -> dict:
    """
    Visualizes metadata or an artifact as a table. Corresponds to 'qiime metadata tabulate'.
    """
    if not m_input_file.exists():
        raise FileNotFoundError(f"Input file not found: {m_input_file}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "metadata", "tabulate",
            "--m-input-file", str(m_input_file),
            "--o-visualization", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created visualization.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 metadata tabulate failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_demux_summarize(
    i_data: Path,
    o_visualization: str,
) -> dict:
    """
    Summarizes demultiplexed sequence data. Corresponds to 'qiime demux summarize'.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input data artifact not found: {i_data}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "demux", "summarize",
            "--i-data", str(i_data),
            "--o-visualization", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created demux summary visualization.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 demux summarize failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_cutadapt_trim_paired(
    i_demultiplexed_sequences: Path,
    o_trimmed_sequences: str,
    p_cores: int = 1,
    p_front_f: Optional[str] = None,
    p_front_r: Optional[str] = None,
    p_overlap: int = 3,
    p_discard_untrimmed: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Trims adapters from paired-end reads using cutadapt. Corresponds to 'qiime cutadapt trim-paired'.
    """
    if not i_demultiplexed_sequences.exists():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_demultiplexed_sequences}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_trimmed_sequences
        
        command = [
            "qiime", "cutadapt", "trim-paired",
            "--i-demultiplexed-sequences", str(i_demultiplexed_sequences),
            "--o-trimmed-sequences", str(output_file),
            "--p-cores", str(p_cores),
            "--p-overlap", str(p_overlap)
        ]
        if p_front_f:
            command.extend(["--p-front-f", p_front_f])
        if p_front_r:
            command.extend(["--p-front-r", p_front_r])
        if p_discard_untrimmed:
            command.append("--p-discard-untrimmed")
        if verbose:
            command.append("--verbose")

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_trimmed_sequences
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 cutadapt trim-paired failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_dada2_denoise_paired(
    i_demultiplexed_seqs: Path,
    o_representative_sequences: str,
    o_table: str,
    o_denoising_stats: str,
    p_trunc_len_f: int,
    p_trunc_len_r: int,
    p_n_threads: int = 1,
) -> dict:
    """
    Denoises paired-end reads using DADA2. Corresponds to 'qiime dada2 denoise-paired'.
    """
    if not i_demultiplexed_seqs.exists():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_demultiplexed_seqs}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        out_rep_seqs = temp_path / o_representative_sequences
        out_table = temp_path / o_table
        out_stats = temp_path / o_denoising_stats
        
        command = [
            "qiime", "dada2", "denoise-paired",
            "--i-demultiplexed-seqs", str(i_demultiplexed_seqs),
            "--p-trunc-len-f", str(p_trunc_len_f),
            "--p-trunc-len-r", str(p_trunc_len_r),
            "--p-n-threads", str(p_n_threads),
            "--o-representative-sequences", str(out_rep_seqs),
            "--o-table", str(out_table),
            "--o-denoising-stats", str(out_stats)
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_out_rep_seqs = Path.cwd() / o_representative_sequences
            final_out_table = Path.cwd() / o_table
            final_out_stats = Path.cwd() / o_denoising_stats
            
            shutil.move(out_rep_seqs, final_out_rep_seqs)
            shutil.move(out_table, final_out_table)
            shutil.move(out_stats, final_out_stats)

            return {
                "command_executed": " ".join(command),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_files": [str(final_out_rep_seqs), str(final_out_table), str(final_out_stats)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 dada2 denoise-paired failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_table_summarize(
    i_table: Path,
    o_visualization: str,
    m_sample_metadata_file: Optional[Path] = None,
) -> dict:
    """
    Summarizes a feature table. Corresponds to 'qiime feature-table summarize'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "feature-table", "summarize",
            "--i-table", str(i_table),
            "--o-visualization", str(output_file)
        ]
        if m_sample_metadata_file:
            if not m_sample_metadata_file.exists():
                raise FileNotFoundError(f"Metadata file not found: {m_sample_metadata_file}")
            command.extend(["--m-sample-metadata-file", str(m_sample_metadata_file)])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created feature table summary.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 feature-table summarize failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_table_tabulate_seqs(
    i_data: Path,
    o_visualization: str,
) -> dict:
    """
    Views feature data (e.g., sequences) as a table. Corresponds to 'qiime feature-table tabulate-seqs'.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input feature data not found: {i_data}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "feature-table", "tabulate-seqs",
            "--i-data", str(i_data),
            "--o-visualization", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created sequence tabulation.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 feature-table tabulate-seqs failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_table_filter_samples(
    i_table: Path,
    o_filtered_table: str,
    m_metadata_file: Optional[Path] = None,
    p_where: Optional[str] = None,
    p_min_frequency: Optional[int] = None,
    p_min_features: Optional[int] = None,
) -> dict:
    """
    Filters samples from a feature table. Corresponds to 'qiime feature-table filter-samples'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_filtered_table
        
        command = [
            "qiime", "feature-table", "filter-samples",
            "--i-table", str(i_table),
            "--o-filtered-table", str(output_file)
        ]
        if m_metadata_file:
            if not m_metadata_file.exists():
                raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
            command.extend(["--m-metadata-file", str(m_metadata_file)])
        if p_where:
            command.extend(["--p-where", p_where])
        if p_min_frequency is not None:
            command.extend(["--p-min-frequency", str(p_min_frequency)])
        if p_min_features is not None:
            command.extend(["--p-min-features", str(p_min_features)])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_filtered_table
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully filtered samples.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 feature-table filter-samples failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_table_filter_features(
    i_table: Path,
    o_filtered_table: str,
    p_min_frequency: Optional[int] = None,
    p_min_samples: Optional[int] = None,
) -> dict:
    """
    Filters features from a feature table. Corresponds to 'qiime feature-table filter-features'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_filtered_table
        
        command = [
            "qiime", "feature-table", "filter-features",
            "--i-table", str(i_table),
            "--o-filtered-table", str(output_file)
        ]
        if p_min_frequency is not None:
            command.extend(["--p-min-frequency", str(p_min_frequency)])
        if p_min_samples is not None:
            command.extend(["--p-min-samples", str(p_min_samples)])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_filtered_table
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully filtered features.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 feature-table filter-features failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_table_filter_seqs(
    i_data: Path,
    i_table: Path,
    o_filtered_data: str,
) -> dict:
    """
    Filters sequences based on a feature table. Corresponds to 'qiime feature-table filter-seqs'.
    """
    if not i_data.exists():
        raise FileNotFoundError(f"Input feature data not found: {i_data}")
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_filtered_data
        
        command = [
            "qiime", "feature-table", "filter-seqs",
            "--i-data", str(i_data),
            "--i-table", str(i_table),
            "--o-filtered-data", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_filtered_data
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully filtered sequences.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 feature-table filter-seqs failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_feature_classifier_classify_sklearn(
    i_reads: Path,
    i_classifier: Path,
    o_classification: str,
) -> dict:
    """
    Classifies reads using a scikit-learn classifier. Corresponds to 'qiime feature-classifier classify-sklearn'.
    """
    if not i_reads.exists():
        raise FileNotFoundError(f"Input reads artifact not found: {i_reads}")
    if not i_classifier.exists():
        raise FileNotFoundError(f"Classifier artifact not found: {i_classifier}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_classification
        
        command = [
            "qiime", "feature-classifier", "classify-sklearn",
            "--i-reads", str(i_reads),
            "--i-classifier", str(i_classifier),
            "--o-classification", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_classification
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully classified sequences.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 classify-sklearn failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_taxa_filter_table(
    i_table: Path,
    i_taxonomy: Path,
    o_filtered_table: str,
    p_include: Optional[str] = None,
    p_exclude: Optional[str] = None,
    p_mode: str = 'contains',
) -> dict:
    """
    Filters a feature table based on taxonomy. Corresponds to 'qiime taxa filter-table'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not i_taxonomy.exists():
        raise FileNotFoundError(f"Input taxonomy artifact not found: {i_taxonomy}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_filtered_table
        
        command = [
            "qiime", "taxa", "filter-table",
            "--i-table", str(i_table),
            "--i-taxonomy", str(i_taxonomy),
            "--o-filtered-table", str(output_file),
            "--p-mode", p_mode
        ]
        if p_include:
            command.extend(["--p-include", p_include])
        if p_exclude:
            command.extend(["--p-exclude", p_exclude])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_filtered_table
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully filtered table by taxonomy.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 taxa filter-table failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_taxa_barplot(
    i_table: Path,
    i_taxonomy: Path,
    o_visualization: str,
    m_metadata_file: Optional[Path] = None,
) -> dict:
    """
    Creates a bar plot of taxonomic compositions. Corresponds to 'qiime taxa barplot'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not i_taxonomy.exists():
        raise FileNotFoundError(f"Input taxonomy artifact not found: {i_taxonomy}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "taxa", "barplot",
            "--i-table", str(i_table),
            "--i-taxonomy", str(i_taxonomy),
            "--o-visualization", str(output_file)
        ]
        if m_metadata_file:
            if not m_metadata_file.exists():
                raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
            command.extend(["--m-metadata-file", str(m_metadata_file)])

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created taxonomy bar plot.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 taxa barplot failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_phylogeny_align_to_tree_mafft_fasttree(
    i_sequences: Path,
    output_dir: str,
) -> dict:
    """
    Builds a phylogenetic tree with MAFFT and FastTree. Corresponds to 'qiime phylogeny align-to-tree-mafft-fasttree'.
    """
    if not i_sequences.exists():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_sequences}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_dir = Path(temp_dir) / "phylogeny_out"
        
        command = [
            "qiime", "phylogeny", "align-to-tree-mafft-fasttree",
            "--i-sequences", str(i_sequences),
            "--output-dir", str(temp_output_dir)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_dir = Path.cwd() / output_dir
            if final_output_dir.exists():
                shutil.rmtree(final_output_dir)
            shutil.move(temp_output_dir, final_output_dir)
            
            output_files = [str(p) for p in final_output_dir.rglob('*')]

            return {
                "command_executed": " ".join(command),
                "stdout": f"Successfully created phylogenetic tree in {final_output_dir}",
                "stderr": "",
                "output_files": output_files
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 phylogeny pipeline failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_diversity_core_metrics_phylogenetic(
    i_table: Path,
    i_phylogeny: Path,
    p_sampling_depth: int,
    output_dir: str,
    m_metadata_file: Path,
    p_n_jobs_or_threads: int = 1,
) -> dict:
    """
    Runs core diversity metrics with phylogeny. Corresponds to 'qiime diversity core-metrics-phylogenetic'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not i_phylogeny.exists():
        raise FileNotFoundError(f"Input phylogeny artifact not found: {i_phylogeny}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_dir = Path(temp_dir) / "diversity_out"
        
        command = [
            "qiime", "diversity", "core-metrics-phylogenetic",
            "--i-table", str(i_table),
            "--i-phylogeny", str(i_phylogeny),
            "--p-sampling-depth", str(p_sampling_depth),
            "--m-metadata-file", str(m_metadata_file),
            "--output-dir", str(temp_output_dir),
            "--p-n-jobs-or-threads", str(p_n_jobs_or_threads)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_dir = Path.cwd() / output_dir
            if final_output_dir.exists():
                shutil.rmtree(final_output_dir)
            shutil.move(temp_output_dir, final_output_dir)
            
            output_files = [str(p) for p in final_output_dir.rglob('*')]

            return {
                "command_executed": " ".join(command),
                "stdout": f"Successfully computed core diversity metrics in {final_output_dir}",
                "stderr": "",
                "output_files": output_files
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 core-metrics-phylogenetic failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_diversity_alpha_group_significance(
    i_alpha_diversity: Path,
    m_metadata_file: Path,
    o_visualization: str,
) -> dict:
    """
    Tests for significant differences in alpha diversity between groups. Corresponds to 'qiime diversity alpha-group-significance'.
    """
    if not i_alpha_diversity.exists():
        raise FileNotFoundError(f"Input alpha diversity artifact not found: {i_alpha_diversity}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "diversity", "alpha-group-significance",
            "--i-alpha-diversity", str(i_alpha_diversity),
            "--m-metadata-file", str(m_metadata_file),
            "--o-visualization", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created alpha group significance visualization.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 alpha-group-significance failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_diversity_beta_group_significance(
    i_distance_matrix: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    o_visualization: str,
    p_method: str = 'permanova',
) -> dict:
    """
    Tests for significant differences in beta diversity between groups. Corresponds to 'qiime diversity beta-group-significance'.
    """
    if not i_distance_matrix.exists():
        raise FileNotFoundError(f"Input distance matrix artifact not found: {i_distance_matrix}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
    if p_method not in ['permanova', 'permdisp', 'anosim']:
        raise ValueError("p_method must be one of 'permanova', 'permdisp', 'anosim'")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "diversity", "beta-group-significance",
            "--i-distance-matrix", str(i_distance_matrix),
            "--m-metadata-file", str(m_metadata_file),
            "--m-metadata-column", m_metadata_column,
            "--o-visualization", str(output_file),
            "--p-method", p_method
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully created beta group significance visualization.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 beta-group-significance failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_composition_ancom(
    i_table: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    o_visualization: str,
) -> dict:
    """
    Performs ANCOM differential abundance testing. Corresponds to 'qiime composition ancom'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input composition table not found: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_file = temp_path / o_visualization
        
        command = [
            "qiime", "composition", "ancom",
            "--i-table", str(i_table),
            "--m-metadata-file", str(m_metadata_file),
            "--m-metadata-column", m_metadata_column,
            "--o-visualization", str(output_file)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_path = Path.cwd() / o_visualization
            shutil.move(output_file, final_output_path)

            return {
                "command_executed": " ".join(command),
                "stdout": "Successfully performed ANCOM analysis.",
                "stderr": "",
                "output_files": [str(final_output_path)]
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 composition ancom failed with exit code {e.returncode}",
                "output_files": []
            }

@mcp.tool()
def qiime_sample_classifier_classify_samples(
    i_table: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    output_dir: str,
    p_estimator: str = 'RandomForestClassifier',
    p_random_state: Optional[int] = None,
    p_optimize_feature_selection: bool = False,
    p_parameter_tuning: bool = False,
) -> dict:
    """
    Trains and tests a supervised learning classifier for sample prediction. Corresponds to 'qiime sample-classifier classify-samples'.
    """
    if not i_table.exists():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_dir = Path(temp_dir) / "classifier_out"
        
        command = [
            "qiime", "sample-classifier", "classify-samples",
            "--i-table", str(i_table),
            "--m-metadata-file", str(m_metadata_file),
            "--m-metadata-column", m_metadata_column,
            "--p-estimator", p_estimator,
            "--output-dir", str(temp_output_dir)
        ]
        if p_random_state is not None:
            command.extend(["--p-random-state", str(p_random_state)])
        if p_optimize_feature_selection:
            command.append("--p-optimize-feature-selection")
        if p_parameter_tuning:
            command.append("--p-parameter-tuning")

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            final_output_dir = Path.cwd() / output_dir
            if final_output_dir.exists():
                shutil.rmtree(final_output_dir)
            shutil.move(temp_output_dir, final_output_dir)
            
            output_files = [str(p) for p in final_output_dir.rglob('*')]

            return {
                "command_executed": " ".join(command),
                "stdout": f"Successfully ran sample classifier, results in {final_output_dir}",
                "stderr": "",
                "output_files": output_files
            }
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(command),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": f"QIIME 2 sample-classifier failed with exit code {e.returncode}",
                "output_files": []
            }

if __name__ == '__main__':
    mcp.run()