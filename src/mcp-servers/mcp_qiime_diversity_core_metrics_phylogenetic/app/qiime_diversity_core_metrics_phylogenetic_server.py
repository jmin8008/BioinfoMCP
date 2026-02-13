from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List, Dict
import logging

# It's a good practice to have a logger for debugging purposes.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def qiime_diversity_core_metrics_phylogenetic(
    phylogeny: Path,
    table: Path,
    sampling_depth: int,
    metadata: List[Path],
    rarefied_table: Path,
    faith_pd_vector: Path,
    observed_features_vector: Path,
    shannon_vector: Path,
    evenness_vector: Path,
    unweighted_unifrac_distance_matrix: Path,
    weighted_unifrac_distance_matrix: Path,
    jaccard_distance_matrix: Path,
    bray_curtis_distance_matrix: Path,
    unweighted_unifrac_pcoa_results: Path,
    weighted_unifrac_pcoa_results: Path,
    jaccard_pcoa_results: Path,
    bray_curtis_pcoa_results: Path,
    unweighted_unifrac_emperor: Path,
    weighted_unifrac_emperor: Path,
    jaccard_emperor: Path,
    bray_curtis_emperor: Path,
    n_jobs: int = 1,
    verbose: bool = False,
) -> Dict:
    """
    Applies a core set of diversity metrics to a feature table, including phylogenetic metrics.

    This is a QIIME 2 pipeline that rarefies a feature table to a specified depth,
    computes several alpha and beta diversity metrics, and generates PCoA results
    and Emperor plots for the beta diversity metrics. This pipeline requires a
    phylogenetic tree.

    Args:
        phylogeny: Path to the phylogenetic tree artifact (.qza).
        table: Path to the feature table artifact (.qza).
        sampling_depth: The total frequency that each sample should be rarefied to.
        metadata: List of paths to sample metadata files (.tsv).
        rarefied_table: Path to save the rarefied feature table artifact (.qza).
        faith_pd_vector: Path to save the Faith's Phylogenetic Diversity (PD) vector artifact (.qza).
        observed_features_vector: Path to save the Observed Features vector artifact (.qza).
        shannon_vector: Path to save the Shannon's diversity vector artifact (.qza).
        evenness_vector: Path to save the Pielou's evenness vector artifact (.qza).
        unweighted_unifrac_distance_matrix: Path to save the unweighted UniFrac distance matrix artifact (.qza).
        weighted_unifrac_distance_matrix: Path to save the weighted UniFrac distance matrix artifact (.qza).
        jaccard_distance_matrix: Path to save the Jaccard distance matrix artifact (.qza).
        bray_curtis_distance_matrix: Path to save the Bray-Curtis distance matrix artifact (.qza).
        unweighted_unifrac_pcoa_results: Path to save the PCoA results from unweighted UniFrac (.qza).
        weighted_unifrac_pcoa_results: Path to save the PCoA results from weighted UniFrac (.qza).
        jaccard_pcoa_results: Path to save the PCoA results from Jaccard distances (.qza).
        bray_curtis_pcoa_results: Path to save the PCoA results from Bray-Curtis distances (.qza).
        unweighted_unifrac_emperor: Path to save the Emperor plot from unweighted UniFrac PCoA (.qzv).
        weighted_unifrac_emperor: Path to save the Emperor plot from weighted UniFrac PCoA (.qzv).
        jaccard_emperor: Path to save the Emperor plot from Jaccard PCoA (.qzv).
        bray_curtis_emperor: Path to save the Emperor plot from Bray-Curtis PCoA (.qzv).
        n_jobs: The number of jobs to use for the computation. (default: 1)
        verbose: Display verbose output to stdout. (default: False)

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a dictionary of output file paths.
    """
    # --- Input Validation ---
    if not phylogeny.is_file():
        raise FileNotFoundError(f"Input phylogeny file not found at: {phylogeny}")
    if not table.is_file():
        raise FileNotFoundError(f"Input feature table file not found at: {table}")
    if not metadata:
        raise ValueError("At least one metadata file must be provided.")
    for meta_file in metadata:
        if not meta_file.is_file():
            raise FileNotFoundError(f"Metadata file not found at: {meta_file}")
    if sampling_depth <= 0:
        raise ValueError(f"sampling_depth must be a positive integer, but got {sampling_depth}")
    if n_jobs == 0:
        raise ValueError("n_jobs cannot be 0.")

    # --- Command Construction ---
    cmd = [
        "qiime", "diversity", "core-metrics-phylogenetic",
        "--i-phylogeny", str(phylogeny),
        "--i-table", str(table),
        "--p-sampling-depth", str(sampling_depth),
        "--p-n-jobs-or-threads", str(n_jobs),
        "--o-rarefied-table", str(rarefied_table),
        "--o-faith-pd-vector", str(faith_pd_vector),
        "--o-observed-features-vector", str(observed_features_vector),
        "--o-shannon-vector", str(shannon_vector),
        "--o-evenness-vector", str(evenness_vector),
        "--o-unweighted-unifrac-distance-matrix", str(unweighted_unifrac_distance_matrix),
        "--o-weighted-unifrac-distance-matrix", str(weighted_unifrac_distance_matrix),
        "--o-jaccard-distance-matrix", str(jaccard_distance_matrix),
        "--o-bray-curtis-distance-matrix", str(bray_curtis_distance_matrix),
        "--o-unweighted-unifrac-pcoa-results", str(unweighted_unifrac_pcoa_results),
        "--o-weighted-unifrac-pcoa-results", str(weighted_unifrac_pcoa_results),
        "--o-jaccard-pcoa-results", str(jaccard_pcoa_results),
        "--o-bray-curtis-pcoa-results", str(bray_curtis_pcoa_results),
        "--o-unweighted-unifrac-emperor", str(unweighted_unifrac_emperor),
        "--o-weighted-unifrac-emperor", str(weighted_unifrac_emperor),
        "--o-jaccard-emperor", str(jaccard_emperor),
        "--o-bray-curtis-emperor", str(bray_curtis_emperor),
    ]

    for meta_file in metadata:
        cmd.extend(["--m-metadata-file", str(meta_file)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("`qiime` command not found. Please ensure QIIME 2 is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        error_message = (
            f"QIIME 2 command failed with exit code {e.returncode}.\n"
            f"Command: '{command_str}'\n"
            f"Stderr: {e.stderr.strip()}\n"
            f"Stdout: {e.stdout.strip()}"
        )
        raise RuntimeError(error_message)

    # --- Structured Result Return ---
    output_files = {
        "rarefied_table": str(rarefied_table),
        "faith_pd_vector": str(faith_pd_vector),
        "observed_features_vector": str(observed_features_vector),
        "shannon_vector": str(shannon_vector),
        "evenness_vector": str(evenness_vector),
        "unweighted_unifrac_distance_matrix": str(unweighted_unifrac_distance_matrix),
        "weighted_unifrac_distance_matrix": str(weighted_unifrac_distance_matrix),
        "jaccard_distance_matrix": str(jaccard_distance_matrix),
        "bray_curtis_distance_matrix": str(bray_curtis_distance_matrix),
        "unweighted_unifrac_pcoa_results": str(unweighted_unifrac_pcoa_results),
        "weighted_unifrac_pcoa_results": str(weighted_unifrac_pcoa_results),
        "jaccard_pcoa_results": str(jaccard_pcoa_results),
        "bray_curtis_pcoa_results": str(bray_curtis_pcoa_results),
        "unweighted_unifrac_emperor": str(unweighted_unifrac_emperor),
        "weighted_unifrac_emperor": str(weighted_unifrac_emperor),
        "jaccard_emperor": str(jaccard_emperor),
        "bray_curtis_emperor": str(bray_curtis_emperor),
    }

    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()