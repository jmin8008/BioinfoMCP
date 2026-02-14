import subprocess
import logging
from pathlib import Path
from typing import Literal, Dict
from fastmcp import FastMCP

# Initialize MCP and logger
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def feature_table_group(
    table: Path,
    metadata_file: Path,
    metadata_column: str,
    grouped_table: Path,
    axis: Literal["sample", "feature"] = "sample",
    mode: Literal["sum", "mean-ceiling", "mean-floor", "median-ceiling", "median-floor"] = "sum",
    verbose: bool = False,
) -> Dict:
    """
    Group samples or features in a feature table by a metadata column.

    This method allows for grouping of samples or features (controlled by the
    'axis' parameter) based on a categorical metadata column. All samples or
    features that have the same value in the specified metadata column will be
    collapsed into a single sample or feature. The values of the collapsed
    samples/features can be combined in different ways, which is controlled by
    the 'mode' parameter.

    Args:
        table (Path): The feature table (.qza) to be grouped.
        metadata_file (Path): The sample or feature metadata file.
        metadata_column (str): The categorical metadata column to group by.
        grouped_table (Path): The path to write the resulting grouped feature table (.qza).
        axis (Literal["sample", "feature"]): The axis to group over. Defaults to "sample".
        mode (Literal["sum", "mean-ceiling", "mean-floor", "median-ceiling", "median-floor"]):
            How to combine features of grouped samples.
            'sum': Sum the frequencies of features.
            'mean-ceiling': Take the ceiling of the mean of the frequencies.
            'mean-floor': Take the floor of the mean of the frequencies.
            'median-ceiling': Take the ceiling of the median of the frequencies.
            'median-floor': Take the floor of the median of the frequencies.
            Defaults to "sum".
        verbose (bool): Display verbose output to stdout. Defaults to False.

    Returns:
        Dict: A dictionary containing the command executed, stdout, stderr,
              and a dictionary of output files.
    """
    # --- Input Validation ---
    if not table.is_file():
        raise FileNotFoundError(f"Input table file not found at: {table}")
    if not metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata_file}")
    if not grouped_table.parent.exists():
        logger.info(f"Output directory {grouped_table.parent} does not exist. Creating it.")
        grouped_table.parent.mkdir(parents=True, exist_ok=True)
    elif not grouped_table.parent.is_dir():
        raise NotADirectoryError(f"The parent path of the output file is not a directory: {grouped_table.parent}")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "group",
        "--i-table", str(table),
        "--m-metadata-file", str(metadata_file),
        "--m-metadata-column", metadata_column,
        "--o-grouped-table", str(grouped_table),
        "--p-axis", axis,
        "--p-mode", mode,
    ]

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        error_msg = "QIIME 2 command-line tool not found. Please ensure 'qiime' is installed and in your system's PATH."
        logger.error(error_msg)
        # Return a structured error response
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": error_msg,
            "output_files": {},
            "error": "QIIME 2 not found"
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing QIIME 2 command. Stderr:\n{e.stderr}")
        # Return a structured error response
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": {},
            "error": "Command execution failed"
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {"grouped_table": str(grouped_table)}
    }

if __name__ == '__main__':
    mcp.run()