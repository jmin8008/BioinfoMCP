import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def classify_consensus_blast(
    query: Path,
    reference_reads: Path,
    reference_taxonomy: Path,
    classification: Path,
    search_results: Optional[Path] = None,
    maxaccepts: int = 10,
    perc_identity: float = 0.8,
    query_cov: float = 0.8,
    strand: str = 'both',
    evalue: float = 0.001,
    min_consensus: float = 0.51,
    unassignable_label: str = 'Unassigned',
    num_threads: int = 1,
    verbose: bool = False,
):
    """
    Assign taxonomy to query sequences using BLAST+.

    This method performs BLAST+ local alignment between query and reference
    sequences to determine the taxonomy of the query sequences. It is a
    reimplementation of the QIIME 1 blast taxonomy assigner.

    Parameters
    ----------
    query : Path
        QIIME 2 artifact (.qza) of type FeatureData[Sequence]. Sequences to classify.
    reference_reads : Path
        QIIME 2 artifact (.qza) of type FeatureData[Sequence]. Reference sequences.
    reference_taxonomy : Path
        QIIME 2 artifact (.qza) of type FeatureData[Taxonomy]. Reference taxonomy labels.
    classification : Path
        Path to write the output QIIME 2 artifact (.qza) for taxonomy classification results.
    search_results : Optional[Path], optional
        Path to write the optional output QIIME 2 artifact (.qza) for top hits for each query.
    maxaccepts : int, optional
        Maximum number of hits to keep for each query. Defaults to 10.
    perc_identity : float, optional
        Reject match if percent identity to query is lower. Must be between 0.0 and 1.0. Defaults to 0.8.
    query_cov : float, optional
        Reject match if query alignment coverage is lower. Must be between 0.0 and 1.0. Defaults to 0.8.
    strand : str, optional
        Align against 'plus' strand, 'minus' strand, or 'both'. Defaults to 'both'.
    evalue : float, optional
        BLAST expectation value (E) for saving hits. Defaults to 0.001.
    min_consensus : float, optional
        Minimum fraction of assignments that must match top hit to be retained. Must be between 0.501 and 1.0. Defaults to 0.51.
    unassignable_label : str, optional
        Label for unassignable features. Defaults to 'Unassigned'.
    num_threads : int, optional
        Number of threads to use for job parallelization. Defaults to 1.
    verbose : bool, optional
        Display verbose output. Defaults to False.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    for input_file in [query, reference_reads, reference_taxonomy]:
        if not input_file.is_file():
            raise FileNotFoundError(f"Input file not found: {input_file}")

    for output_path in [classification, search_results]:
        if output_path and not output_path.parent.is_dir():
            raise NotADirectoryError(f"Output directory does not exist: {output_path.parent}")

    if maxaccepts < 1:
        raise ValueError("maxaccepts must be an integer greater than or equal to 1.")
    if not (0.0 <= perc_identity <= 1.0):
        raise ValueError("perc_identity must be between 0.0 and 1.0.")
    if not (0.0 <= query_cov <= 1.0):
        raise ValueError("query_cov must be between 0.0 and 1.0.")
    if strand not in ['both', 'plus', 'minus']:
        raise ValueError("strand must be one of 'both', 'plus', or 'minus'.")
    if not (0.501 < min_consensus <= 1.0):
        raise ValueError("min_consensus must be between 0.501 (exclusive) and 1.0 (inclusive).")
    if num_threads < 1:
        raise ValueError("num_threads must be an integer greater than or equal to 1.")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-classifier", "classify-consensus-blast",
        "--i-query", str(query),
        "--i-reference-reads", str(reference_reads),
        "--i-reference-taxonomy", str(reference_taxonomy),
        "--o-classification", str(classification),
        "--p-maxaccepts", str(maxaccepts),
        "--p-perc-identity", str(perc_identity),
        "--p-query-cov", str(query_cov),
        "--p-strand", strand,
        "--p-evalue", str(evalue),
        "--p-min-consensus", str(min_consensus),
        "--p-unassignable-label", unassignable_label,
        "--p-num-threads", str(num_threads),
    ]

    if search_results:
        cmd.extend(["--o-search-results", str(search_results)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        output_files: List[str] = [str(classification)]
        if search_results:
            output_files.append(str(search_results))

        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files
        }
    except FileNotFoundError:
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your system's PATH.",
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": []
        }

if __name__ == '__main__':
    mcp.run()