import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def pairwise_distances(
    distance_matrix: Path,
    metadata_file: List[Path],
    state_column: str,
    individual_id_column: str,
    pairwise_distances: Path,
    group_column: Optional[str] = None,
    replicate_handling: str = 'random',
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Calculate pairwise distances between states using QIIME 2's longitudinal plugin.

    This tool calculates pairwise distances between states for each individual
    and generates a boxplot of these distances. It requires a distance matrix
    and metadata describing the samples.
    """
    # --- Input Validation ---
    if not distance_matrix.exists():
        raise FileNotFoundError(f"Input distance matrix not found: {distance_matrix}")

    for meta_path in metadata_file:
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")

    valid_replicate_handling = {'random', 'drop'}
    if replicate_handling not in valid_replicate_handling:
        raise ValueError(f"Invalid value for replicate_handling: '{replicate_handling}'. "
                         f"Must be one of {valid_replicate_handling}.")

    # Ensure output directory exists
    pairwise_distances.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "longitudinal", "pairwise-distances",
        "--i-distance-matrix", str(distance_matrix),
        "--p-state-column", state_column,
        "--p-individual-id-column", individual_id_column,
        "--p-replicate-handling", replicate_handling,
        "--o-pairwise-distances", str(pairwise_distances),
    ]

    for meta_path in metadata_file:
        cmd.extend(["--m-metadata-file", str(meta_path)])

    if group_column:
        cmd.extend(["--p-group-column", group_column])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        return {
            "error": "QIIME 2 command not found. Please ensure 'qiime' is in your system's PATH."
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "pairwise_distances": str(pairwise_distances)
        }
    }

if __name__ == '__main__':
    mcp.run()