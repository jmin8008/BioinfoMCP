from fastmcp import FastMCP
import subprocess
import logging
from pathlib import Path
from typing import Literal

# Initialize the MCP server
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def composition_add_pseudocount(
    table: Path,
    composition_table: Path,
    pseudocount: int = 1,
):
    """
    Adds a pseudocount to all feature abundances in a FeatureTable.

    This is a common preprocessing step for compositional analyses like ANCOM,
    which cannot tolerate zero values in the input table.

    Args:
        table: Path to the input feature table artifact (.qza).
        composition_table: Path for the output composition table artifact (.qza).
        pseudocount: The integer value to add to all counts in the table. Must be >= 1.
    """
    # --- Input Validation ---
    if not table.is_file():
        raise FileNotFoundError(f"Input table not found at: {table}")
    if pseudocount < 1:
        raise ValueError("Pseudocount must be a positive integer (>= 1).")

    # Ensure output directory exists
    composition_table.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "composition", "add-pseudocount",
        "--i-table", str(table),
        "--o-composition-table", str(composition_table),
        "--p-pseudocount", str(pseudocount),
    ]

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

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
        logging.info("QIIME 2 command executed successfully.")

    except FileNotFoundError:
        logging.error("QIIME 2 is not installed or not in the system's PATH.")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        raise

    # --- Return Structured Output ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "composition_table": str(composition_table)
        }
    }

@mcp.tool()
def composition_ancom(
    table: Path,
    metadata_file: Path,
    metadata_column: str,
    visualization: Path,
    transform_function: Literal["sqrt", "log", "clr"] = "clr",
    difference_function: Literal["mean_difference", "difference"] = "mean_difference",
):
    """
    Performs ANCOM (Analysis of Composition of Microbiomes) differential abundance testing.

    ANCOM is used to identify features that are differentially abundant across sample groups
    defined in a metadata column. This action produces a visualization of the ANCOM results.
    Note: The input table should not contain any zero values; use the 'composition_add_pseudocount'
    tool first if necessary.

    Args:
        table: Path to the input composition table artifact (.qza).
        metadata_file: Path to the sample metadata file (TSV format).
        metadata_column: The categorical metadata column to test for differential abundance.
        visualization: Path for the output visualization artifact (.qzv).
        transform_function: The method used to transform feature abundances before calculating pairwise ratios.
        difference_function: The method used to calculate the difference of the pairwise ratios between groups.
    """
    # --- Input Validation ---
    if not table.is_file():
        raise FileNotFoundError(f"Input composition table not found at: {table}")
    if not metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata_file}")
    if not metadata_column:
        raise ValueError("metadata_column must be specified.")

    # Ensure output directory exists
    visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "composition", "ancom",
        "--i-table", str(table),
        "--m-metadata-file", str(metadata_file),
        "--m-metadata-column", metadata_column,
        "--o-visualization", str(visualization),
        "--p-transform-function", transform_function,
        "--p-difference-function", difference_function,
    ]

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

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
        logging.info("QIIME 2 command executed successfully.")

    except FileNotFoundError:
        logging.error("QIIME 2 is not installed or not in the system's PATH.")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        raise

    # --- Return Structured Output ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "visualization": str(visualization)
        }
    }

if __name__ == '__main__':
    mcp.run()