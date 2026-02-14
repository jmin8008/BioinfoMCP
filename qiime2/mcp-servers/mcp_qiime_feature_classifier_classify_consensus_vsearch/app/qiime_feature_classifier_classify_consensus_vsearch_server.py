import subprocess
import logging
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

logging.basicConfig(level=logging.INFO)

@mcp.tool()
def qiime_feature_classifier_classify_consensus_vsearch(
    i_query: Path,
    i_reference_reads: Path,
    i_reference_taxonomy: Path,
    o_classification: Path,
    o_search_results: Optional[Path] = None,
    p_maxaccepts: str = "10",
    p_perc_identity: float = 0.8,
    p_query_cov: float = 0.8,
    p_strand: str = "both",
    p_min_consensus: float = 0.51,
    p_unassignable_label: str = "Unassigned",
    p_threads: int = 1,
    verbose: bool = False,
) -> dict:
    """
    Assigns taxonomy to query sequences using VSEARCH global alignment.

    This tool performs VSEARCH global alignment between query and reference
    sequences, then assigns a consensus taxonomy to each query sequence from
    among the top hits.

    Args:
        i_query (Path): QIIME 2 artifact (.qza) of sequences to classify (FeatureData[Sequence]).
        i_reference_reads (Path): QIIME 2 artifact (.qza) of reference sequences (FeatureData[Sequence]).
        i_reference_taxonomy (Path): QIIME 2 artifact (.qza) of reference taxonomy (FeatureData[Taxonomy]).
        o_classification (Path): Path to write the output taxonomy classifications artifact (.qza).
        o_search_results (Optional[Path]): Path to write the output top hits for each query (.qza). Defaults to None.
        p_maxaccepts (str): Maximum number of hits to keep for each query. Set to "all" to keep all hits > perc_identity. Defaults to "10".
        p_perc_identity (float): Reject match if percent identity to query is lower. Must be between 0.0 and 1.0. Defaults to 0.8.
        p_query_cov (float): Reject match if query coverage is lower. Must be between 0.0 and 1.0. Defaults to 0.8.
        p_strand (str): Align against reference sequences in forward ("plus") or both directions ("both"). Defaults to "both".
        p_min_consensus (float): Minimum fraction of assignments that must match top hit to be accepted. Must be between 0.5 and 1.0. Defaults to 0.51.
        p_unassignable_label (str): Label for features that cannot be classified. Defaults to "Unassigned".
        p_threads (int): Number of threads to use for the job. Defaults to 1.
        verbose (bool): Display verbose output. Defaults to False.

    Returns:
        dict: A dictionary containing the executed command, stdout, stderr, and a list of output file paths.
    """
    # --- Input Validation ---
    if not i_query.exists():
        raise FileNotFoundError(f"Input query file not found: {i_query}")
    if not i_reference_reads.exists():
        raise FileNotFoundError(f"Input reference reads file not found: {i_reference_reads}")
    if not i_reference_taxonomy.exists():
        raise FileNotFoundError(f"Input reference taxonomy file not found: {i_reference_taxonomy}")

    if p_maxaccepts.lower() != 'all':
        try:
            maxaccepts_int = int(p_maxaccepts)
            if maxaccepts_int < 1:
                raise ValueError("p_maxaccepts must be a positive integer or 'all'.")
        except ValueError:
            raise ValueError("p_maxaccepts must be a string representing a positive integer or 'all'.")

    if not (0.0 <= p_perc_identity <= 1.0):
        raise ValueError("p_perc_identity must be between 0.0 and 1.0.")
    if not (0.0 <= p_query_cov <= 1.0):
        raise ValueError("p_query_cov must be between 0.0 and 1.0.")
    if p_strand not in ["both", "plus"]:
        raise ValueError("p_strand must be either 'both' or 'plus'.")
    if not (0.5 < p_min_consensus <= 1.0):
        raise ValueError("p_min_consensus must be greater than 0.5 and at most 1.0.")
    if p_threads < 1:
        raise ValueError("p_threads must be a positive integer.")

    # --- File Path Handling ---
    o_classification.parent.mkdir(parents=True, exist_ok=True)
    if o_search_results:
        o_search_results.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-classifier", "classify-consensus-vsearch",
        "--i-query", str(i_query),
        "--i-reference-reads", str(i_reference_reads),
        "--i-reference-taxonomy", str(i_reference_taxonomy),
        "--o-classification", str(o_classification),
        "--p-maxaccepts", str(p_maxaccepts),
        "--p-perc-identity", str(p_perc_identity),
        "--p-query-cov", str(p_query_cov),
        "--p-strand", p_strand,
        "--p-min-consensus", str(p_min_consensus),
        "--p-unassignable-label", p_unassignable_label,
        "--p-threads", str(p_threads),
    ]

    if o_search_results:
        cmd.extend(["--o-search-results", str(o_search_results)])
    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        stdout = result.stdout
        stderr = result.stderr
        logging.info("QIIME 2 command executed successfully.")

    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your PATH.",
            "output_files": [],
            "return_code": 1
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
            "return_code": e.returncode
        }

    # --- Structured Result Return ---
    output_files: List[str] = [str(o_classification)]
    if o_search_results and o_search_results.exists():
        output_files.append(str(o_search_results))

    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
        "return_code": 0
    }

if __name__ == '__main__':
    mcp.run()