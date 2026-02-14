import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def longitudinal_pairwise_differences(
    i_table: Path,
    m_metadata_file: Path,
    p_group_column: str,
    p_state_column: str,
    p_state_1: str,
    p_state_2: str,
    p_individual_id_column: str,
    o_visualization: Path,
    p_replicate_handling: str = "random",
    p_metric: Optional[str] = None,
    p_parametric: bool = False,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Test for pairwise differences between groups at individual time points.

    This action tests for differences in a feature or alpha diversity metric
    between two states within a group, after controlling for repeated measures
    from individual subjects. This action does not currently support interaction
    effects (e.g., differences in the rate of change between groups).
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {i_table}")
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {m_metadata_file}")

    valid_replicate_handling = ["random", "drop"]
    if p_replicate_handling not in valid_replicate_handling:
        raise ValueError(
            f"Invalid value for p_replicate_handling: '{p_replicate_handling}'. "
            f"Must be one of {valid_replicate_handling}."
        )

    # Ensure output directory exists
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command-Line Construction ---
    cmd = [
        "qiime",
        "longitudinal",
        "pairwise-differences",
        "--i-table",
        str(i_table),
        "--m-metadata-file",
        str(m_metadata_file),
        "--p-group-column",
        p_group_column,
        "--p-state-column",
        p_state_column,
        "--p-state-1",
        p_state_1,
        "--p-state-2",
        p_state_2,
        "--p-individual-id-column",
        p_individual_id_column,
        "--p-replicate-handling",
        p_replicate_handling,
        "--o-visualization",
        str(o_visualization),
    ]

    if p_metric:
        cmd.extend(["--p-metric", p_metric])

    if p_parametric:
        cmd.append("--p-parametric")

    if verbose:
        cmd.append("--verbose")

    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {"visualization": str(o_visualization)},
        }
    except subprocess.CalledProcessError as e:
        # In case of an error, QIIME 2 often prints useful information to stderr
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }
    except FileNotFoundError:
        return {
            "error": "The 'qiime' command was not found. Please ensure QIIME 2 is installed and in your PATH.",
            "command_executed": command_str,
        }


if __name__ == "__main__":
    mcp.run()