from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Dict, Optional
import logging

# Initialize MCP and logger
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def alpha_phylogenetic(
    i_table: Path,
    i_phylogeny: Path,
    o_alpha_diversity: Path,
    p_metric: str,
    verbose: bool = False,
) -> Dict[str, any]:
    """
    Computes phylogenetic alpha diversity for all samples in a feature table.

    This tool applies a user-specified phylogenetic alpha diversity metric,
    specifically Faith's Phylogenetic Diversity (faith_pd), to a feature table.
    It requires a rooted phylogenetic tree to perform the calculation.

    Args:
        i_table (Path): The feature table artifact (FeatureTable[Frequency]) containing the samples.
        i_phylogeny (Path): The rooted phylogenetic tree artifact (Phylogeny[Rooted]).
        o_alpha_diversity (Path): The path to write the output alpha diversity artifact (SampleData[AlphaDiversity]).
        p_metric (str): The phylogenetic alpha diversity metric to be computed. Must be 'faith_pd'.
        verbose (bool, optional): Display verbose output during command execution. Defaults to False.

    Returns:
        Dict[str, any]: A dictionary containing the execution details and output file paths.
    
    Raises:
        FileNotFoundError: If input files do not exist.
        ValueError: If an invalid metric is provided.
        RuntimeError: If the QIIME 2 command fails.
    """
    # Input validation
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found at: {i_table}")
    if not i_phylogeny.is_file():
        raise FileNotFoundError(f"Input phylogeny file not found at: {i_phylogeny}")

    allowed_metrics = ['faith_pd']
    if p_metric not in allowed_metrics:
        raise ValueError(f"Invalid metric '{p_metric}'. The only allowed metric is: '{allowed_metrics[0]}'")

    # Ensure output directory exists
    try:
        o_alpha_diversity.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory for {o_alpha_diversity}: {e}")
        raise

    # Command construction
    cmd = [
        "qiime", "diversity", "alpha-phylogenetic",
        "--i-table", str(i_table),
        "--i-phylogeny", str(i_phylogeny),
        "--o-alpha-diversity", str(o_alpha_diversity),
        "--p-metric", p_metric,
    ]

    if verbose:
        cmd.append("--verbose")

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # Subprocess execution and error handling
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        stdout = result.stdout
        stderr = result.stderr
        logger.info("QIIME diversity alpha-phylogenetic completed successfully.")

    except FileNotFoundError:
        error_msg = "`qiime` command not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME command failed with exit code {e.returncode}")
        error_message = (
            f"QIIME command execution failed.\n"
            f"Command: {command_executed}\n"
            f"Exit Code: {e.returncode}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )
        raise RuntimeError(error_message) from e

    # Structured result return
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "alpha_diversity": str(o_alpha_diversity)
        }
    }

if __name__ == '__main__':
    mcp.run()