import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def diversity_beta_phylogenetic(
    i_table: Path,
    i_phylogeny: Path,
    o_distance_matrix: Path,
    p_metric: str,
    p_threads: int = 1,
    p_variance_adjusted: bool = False,
    p_alpha: Optional[float] = None,
    p_bypass_tips: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict:
    """
    Computes a user-specified phylogenetic beta diversity metric for all pairs
    of samples in a feature table.

    This tool is part of the QIIME 2 diversity plugin.

    Parameters
    ----------
    i_table : Path
        The feature table artifact (FeatureTable[Frequency]) containing the samples
        over which beta diversity should be computed.
    i_phylogeny : Path
        The phylogenetic tree artifact (Phylogeny[Rooted]) containing tip
        identifiers that correspond to the feature identifiers in the table.
    o_distance_matrix : Path
        The path to write the resulting distance matrix artifact (DistanceMatrix).
    p_metric : str
        The beta diversity metric to be computed.
        Choices: 'faith_pd', 'weighted_unifrac', 'unweighted_unifrac'.
    p_threads : int, optional
        The number of threads to use for computation. (Default: 1)
    p_variance_adjusted : bool, optional
        Perform variance adjustment to the UniFrac distance matrices. This is not
        applied to Faith's PD. (Default: False)
    p_alpha : Optional[float], optional
        This parameter is only used when the metric is 'weighted_unifrac' for the
        generalized UniFrac calculation. If not provided, the default of 1.0 is
        used by QIIME 2 (original weighted UniFrac).
    p_bypass_tips : bool, optional
        In a bifurcating tree, bypassing tips can speed up traversal by up to 50%.
        This is safe if the table and tree are not empty. (Default: False)
    verbose : bool, optional
        Display verbose output to stdout. (Default: False)
    quiet : bool, optional
        Suppress all output to stdout. (Default: False)

    Returns
    -------
    Dict
        A dictionary containing the command executed, stdout, stderr, and a
        list of output files generated.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table artifact not found at: {i_table}")
    if not i_phylogeny.is_file():
        raise FileNotFoundError(f"Input phylogeny artifact not found at: {i_phylogeny}")

    allowed_metrics = ['faith_pd', 'weighted_unifrac', 'unweighted_unifrac']
    if p_metric not in allowed_metrics:
        raise ValueError(f"Invalid metric '{p_metric}'. Must be one of {allowed_metrics}")

    if p_threads < 1:
        raise ValueError("p_threads must be a positive integer.")

    if p_alpha is not None and p_metric != 'weighted_unifrac':
        raise ValueError("The 'p_alpha' parameter can only be used with the 'weighted_unifrac' metric.")

    # Ensure output directory exists
    o_distance_matrix.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "diversity", "beta-phylogenetic",
        "--i-table", str(i_table),
        "--i-phylogeny", str(i_phylogeny),
        "--o-distance-matrix", str(o_distance_matrix),
        "--p-metric", p_metric,
        "--p-threads", str(p_threads),
    ]

    if p_variance_adjusted:
        cmd.append("--p-variance-adjusted")
    if p_alpha is not None:
        cmd.extend(["--p-alpha", str(p_alpha)])
    if p_bypass_tips:
        cmd.append("--p-bypass-tips")
    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_distance_matrix)]
        }
    except subprocess.CalledProcessError as e:
        # Re-raise with a more informative error message for the MCP context
        error_message = (
            f"QIIME 2 diversity beta-phylogenetic command failed with exit code {e.returncode}.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        )
        raise RuntimeError(error_message) from e
    except FileNotFoundError:
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and in your PATH.")

if __name__ == '__main__':
    mcp.run()