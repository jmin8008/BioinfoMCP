import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def vsearch_cluster_features_open_reference(
    i_sequences: Path,
    i_table: Path,
    i_reference_sequences: Path,
    p_perc_identity: float,
    o_clustered_table: Path,
    o_clustered_sequences: Path,
    p_strand: str = "plus",
    p_threads: int = 1,
    o_new_reference_sequences: Optional[Path] = None,
    o_unmatched_sequences: Optional[Path] = None,
):
    """
    QIIME2 vsearch: Open-reference clustering of features.

    This method performs open-reference clustering. First, features are clustered against a reference
    database (closed-reference clustering). Any features that don't hit the reference are then
    clustered de novo.
    """
    # --- Input Validation ---
    if not i_sequences.is_file():
        raise FileNotFoundError(f"Input sequences file not found: {i_sequences}")
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table file not found: {i_table}")
    if not i_reference_sequences.is_file():
        raise FileNotFoundError(
            f"Input reference sequences file not found: {i_reference_sequences}"
        )

    if not (0.0 <= p_perc_identity <= 1.0):
        raise ValueError("p_perc_identity must be between 0.0 and 1.0.")

    if p_strand not in ["plus", "both"]:
        raise ValueError("p_strand must be either 'plus' or 'both'.")

    if p_threads < 0:
        raise ValueError("p_threads must be a non-negative integer.")

    # --- Output Path Handling ---
    output_files = [o_clustered_table, o_clustered_sequences]
    for path in output_files:
        path.parent.mkdir(parents=True, exist_ok=True)
    if o_new_reference_sequences:
        o_new_reference_sequences.parent.mkdir(parents=True, exist_ok=True)
        output_files.append(o_new_reference_sequences)
    if o_unmatched_sequences:
        o_unmatched_sequences.parent.mkdir(parents=True, exist_ok=True)
        output_files.append(o_unmatched_sequences)

    # --- Command Construction ---
    cmd = [
        "qiime",
        "vsearch",
        "cluster-features-open-reference",
        "--i-sequences",
        str(i_sequences),
        "--i-table",
        str(i_table),
        "--i-reference-sequences",
        str(i_reference_sequences),
        "--p-perc-identity",
        str(p_perc_identity),
        "--p-strand",
        p_strand,
        "--p-threads",
        str(p_threads),
        "--o-clustered-table",
        str(o_clustered_table),
        "--o-clustered-sequences",
        str(o_clustered_sequences),
    ]

    if o_new_reference_sequences:
        cmd.extend(["--o-new-reference-sequences", str(o_new_reference_sequences)])
    if o_unmatched_sequences:
        cmd.extend(["--o-unmatched-sequences", str(o_unmatched_sequences)])

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(p) for p in output_files],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME2 vsearch failed with exit code {e.returncode}",
            "output_files": [],
        }


if __name__ == "__main__":
    mcp.run()