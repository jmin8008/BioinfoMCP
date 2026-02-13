from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List
import shlex

mcp = FastMCP()

@mcp.tool()
def lib_unifrac(
    i_table: Path,
    i_phylogeny: Path,
    o_distance_matrix: Path,
    p_threads: int = 1,
    p_variance_adjusted: bool = False,
    p_bypass_tips: bool = False,
) -> dict:
    """
    Computes UniFrac, a phylogenetic distance metric.

    This is a stand-alone script for computing UniFrac which can be used
    outside of a QIIME 2 environment. It is not recommended for use by most
    users.

    Args:
        i_table: The feature table artifact containing the samples over which to compute UniFrac.
        i_phylogeny: The rooted phylogenetic tree artifact.
        o_distance_matrix: The path for the resulting distance matrix artifact.
        p_threads: The number of threads to use for computation.
        p_variance_adjusted: Perform variance adjustment to account for phylogenetic diversity that is not present in the table.
        p_bypass_tips: In a bifurcating tree, the tips make up about 50% of the nodes. Bypassing tips speeds up the calculation by about 50%.
    
    Returns:
        A dictionary containing the execution command, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found: {i_table}")
    if not i_phylogeny.is_file():
        raise FileNotFoundError(f"Input phylogeny file not found: {i_phylogeny}")
    if p_threads <= 0:
        raise ValueError(f"p_threads must be a positive integer, but got {p_threads}")

    # Ensure output directory exists
    o_distance_matrix.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "diversity", "lib-unifrac",
        "--i-table", str(i_table),
        "--i-phylogeny", str(i_phylogeny),
        "--o-distance-matrix", str(o_distance_matrix),
        "--p-threads", str(p_threads),
    ]

    if p_variance_adjusted:
        cmd.append("--p-variance-adjusted")

    if p_bypass_tips:
        cmd.append("--p-bypass-tips")

    command_str = shlex.join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        output_files = [str(o_distance_matrix)] if o_distance_matrix.exists() else []

    except FileNotFoundError:
        error_message = "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": error_message,
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": []
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files
    }

if __name__ == '__main__':
    mcp.run()