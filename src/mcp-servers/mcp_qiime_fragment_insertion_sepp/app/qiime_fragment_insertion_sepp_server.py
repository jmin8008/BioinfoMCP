from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Dict
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def sepp(
    representative_sequences: Path,
    reference_database: Path,
    tree: Path,
    placements: Path,
    threads: int = 1,
    alignment_subset_size: int = 1000,
    placement_subset_size: int = 1000,
    debug: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict:
    """
    Build a phylogenetic tree by inserting fragment sequences into a reference phylogeny using SEPP.

    This method is a wrapper around the SEPP (SATe-enabled Phylogenetic Placement) algorithm,
    which is designed for phylogenetic placement of short-read sequences. It is part of the
    QIIME 2 fragment-insertion plugin.

    Args:
        representative_sequences (Path): The sequences (QIIME 2 artifact) to be inserted into the reference tree.
        reference_database (Path): The reference database (QIIME 2 artifact of type Phylogeny[Rooted]).
        tree (Path): The path for the resulting phylogenetic tree output artifact.
        placements (Path): The path for the placement information output artifact.
        threads (int): The number of threads to use for parallel processing. Defaults to 1.
        alignment_subset_size (int): The number of sequences to include in each sub-alignment. Defaults to 1000.
        placement_subset_size (int): The number of sequences from the reference database to be used for placement. Defaults to 1000.
        debug (bool): Print debug information to STDOUT. Defaults to False.
        verbose (bool): Print verbose output to stdout and stderr. Defaults to False.
        quiet (bool): Suppress all output during execution. Defaults to False.

    Returns:
        Dict: A dictionary containing the executed command, stdout, stderr, and a dictionary of output file paths.
    """
    # --- Input Validation ---
    if not representative_sequences.is_file():
        raise FileNotFoundError(f"Input representative sequences file not found: {representative_sequences}")
    if not reference_database.is_file():
        raise FileNotFoundError(f"Input reference database file not found: {reference_database}")

    if threads <= 0:
        raise ValueError("The number of threads must be a positive integer.")
    if alignment_subset_size <= 0:
        raise ValueError("The alignment subset size must be a positive integer.")
    if placement_subset_size <= 0:
        raise ValueError("The placement subset size must be a positive integer.")

    # Ensure output directories exist
    try:
        tree.parent.mkdir(parents=True, exist_ok=True)
        placements.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Could not create output directories: {e}")

    # --- Command Construction ---
    cmd = [
        "qiime", "fragment-insertion", "sepp",
        "--i-representative-sequences", str(representative_sequences),
        "--i-reference-database", str(reference_database),
        "--o-tree", str(tree),
        "--o-placements", str(placements),
        "--p-threads", str(threads),
        "--p-alignment-subset-size", str(alignment_subset_size),
        "--p-placement-subset-size", str(placement_subset_size),
    ]

    if debug:
        cmd.append("--p-debug")
    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # --- Structured Result Return (Success) ---
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "tree": str(tree),
                "placements": str(placements)
            }
        }
    except FileNotFoundError:
        # This error occurs if 'qiime' is not in the system's PATH
        error_message = "Error: 'qiime' command not found. Make sure QIIME 2 is installed and the environment is activated."
        logger.error(error_message)
        # In a real server, you might raise an exception that translates to a 500 error.
        # For this spec, we return a structured error.
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": error_message,
            "output_files": {}
        }
    except subprocess.CalledProcessError as e:
        # --- Structured Result Return (Tool Failure) ---
        logger.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": {}
        }

if __name__ == '__main__':
    mcp.run()