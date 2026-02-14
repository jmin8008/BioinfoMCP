from fastmcp import FastMCP
from pathlib import Path
import subprocess
from typing import List

mcp = FastMCP()

@mcp.tool()
def feature_table_merge(
    tables: List[Path],
    merged_table: Path,
    overlap_method: str = 'error_on_overlapping_sample',
    verbose: bool = False
):
    """
    Merges multiple QIIME 2 feature tables into a single feature table.

    This tool combines multiple feature tables. All feature tables must have the
    same features and samples unless the 'sum' overlap method is used.
    """
    # --- Input Validation ---
    if not tables:
        raise ValueError("At least one input table must be provided for the 'tables' parameter.")

    for table_path in tables:
        if not table_path.is_file():
            raise FileNotFoundError(f"Input table file not found: {table_path}")

    allowed_methods = ['error_on_overlapping_sample', 'sum', 'error_on_overlapping_feature']
    if overlap_method not in allowed_methods:
        raise ValueError(f"Invalid overlap_method '{overlap_method}'. Must be one of {allowed_methods}.")

    # Ensure output directory exists
    try:
        merged_table.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Failed to create output directory for {merged_table}: {e}")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "merge",
        "--o-merged-table", str(merged_table),
        "--p-overlap-method", overlap_method,
    ]

    # Add all input tables by repeating the --i-tables flag
    for table_path in tables:
        cmd.extend(["--i-tables", str(table_path)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_executed = " ".join(map(str, cmd))
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in the system's PATH.")
    except subprocess.CalledProcessError as e:
        # The MCP framework will catch this and return a structured error response.
        # We re-raise the exception to allow the framework to handle it.
        # The error message will include stdout and stderr from the failed process.
        raise e

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": [str(merged_table)]
    }

if __name__ == '__main__':
    mcp.run()