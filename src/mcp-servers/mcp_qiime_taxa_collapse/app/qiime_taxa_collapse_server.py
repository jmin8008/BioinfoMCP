from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP application
mcp = FastMCP()

@mcp.tool()
def taxa_collapse(
    i_table: Path,
    i_taxonomy: Path,
    p_level: int,
    o_collapsed_table: Path,
    verbose: bool = False,
) -> dict:
    """
    Collapse features by their taxonomic assignment at a specified level.

    This tool wraps the 'qiime taxa collapse' command from QIIME 2. It collapses
    a feature table to a user-specified taxonomic level.

    Args:
        i_table (Path): Path to the input feature table artifact (.qza).
                        This table contains the feature frequencies to be collapsed.
        i_taxonomy (Path): Path to the taxonomy artifact (.qza) corresponding to the
                           features in the input table.
        p_level (int): The taxonomic level at which the features should be collapsed.
                       Must be an integer greater than or equal to 1.
        o_collapsed_table (Path): The path where the resulting collapsed feature
                                  table artifact (.qza) will be saved.
        verbose (bool): If True, display verbose output during command execution.
                        Defaults to False.

    Returns:
        dict: A dictionary containing the execution details, including the command,
              stdout, stderr, and a mapping of output file keys to their paths.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found at: {i_table}")
    if not i_taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy file not found at: {i_taxonomy}")
    if p_level < 1:
        raise ValueError(f"p_level must be an integer >= 1, but got {p_level}")

    # Ensure the output directory exists
    o_collapsed_table.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "taxa", "collapse",
        "--i-table", str(i_table),
        "--i-taxonomy", str(i_taxonomy),
        "--p-level", str(p_level),
        "--o-collapsed-table", str(o_collapsed_table),
    ]

    if verbose:
        cmd.append("--verbose")

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        # This error occurs if 'qiime' is not in the system's PATH
        return {
            "error": "QIIME 2 command-line tool not found. Please ensure it is installed and in your PATH.",
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Executable 'qiime' not found.",
        }
    except subprocess.CalledProcessError as e:
        # This error occurs if QIIME 2 returns a non-zero exit code
        logger.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "error": "QIIME 2 command execution failed.",
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "collapsed_table": str(o_collapsed_table)
        }
    }

if __name__ == '__main__':
    mcp.run()