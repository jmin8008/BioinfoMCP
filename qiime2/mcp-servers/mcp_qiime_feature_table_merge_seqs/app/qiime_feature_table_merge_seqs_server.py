from fastmcp import FastMCP
from pathlib import Path
import subprocess
from typing import List, Dict, Any

mcp = FastMCP()


@mcp.tool()
def feature_table_merge_seqs(
    data: List[Path],
    merged_data: Path,
    no_overlap_method: str = 'error',
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Combines feature sequence data tables using QIIME 2.

    This tool merges multiple FeatureData[Sequence] artifacts into a single artifact.
    It corresponds to the 'qiime feature-table merge-seqs' command.

    Args:
        data: A list of paths to the feature sequence data tables (QIIME 2 artifacts) to be merged.
        merged_data: The path for the output merged feature sequence data artifact.
        no_overlap_method: Method for handling features that are not found in all tables.
                           Choices are 'error' or 'sum'.
        verbose: Display verbose output when running the command.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output file paths.
    """
    # --- Input Validation ---
    if not data:
        raise ValueError("The --i-data parameter requires at least one input file.")

    for input_path in data:
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

    valid_methods = ['error', 'sum']
    if no_overlap_method not in valid_methods:
        raise ValueError(
            f"Invalid value for no_overlap_method: '{no_overlap_method}'. "
            f"Must be one of {valid_methods}."
        )

    # Ensure the output directory exists
    try:
        merged_data.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise IOError(f"Failed to create output directory {merged_data.parent}: {e}")

    # --- Command Construction ---
    cmd = ["qiime", "feature-table", "merge-seqs"]

    for path in data:
        cmd.extend(["--i-data", str(path)])

    cmd.extend(["--o-merged-data", str(merged_data)])
    cmd.extend(["--p-no-overlap-method", no_overlap_method])

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        # QIIME 2 command failed, return structured error info
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}.",
            "output_files": {}
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "merged_data": str(merged_data)
        }
    }


if __name__ == '__main__':
    mcp.run()