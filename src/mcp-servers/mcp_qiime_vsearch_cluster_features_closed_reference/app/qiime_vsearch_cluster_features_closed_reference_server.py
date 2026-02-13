import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def vsearch_cluster_features_closed_reference(
    sequences: Path,
    table: Path,
    reference_sequences: Path,
    perc_identity: float,
    strand: Literal["both", "plus"] = "plus",
    threads: int = 1,
    verbose: bool = False,
):
    """
    Performs closed-reference OTU clustering using the vsearch algorithm.

    This method clusters sequences against a reference database. Any sequences that
    do not match a reference sequence at the specified percent identity are discarded.
    The feature table is updated to reflect the new clustered features.

    Parameters
    ----------
    sequences : Path
        The sequences to be clustered (QIIME 2 artifact, FeatureData[Sequence]).
    table : Path
        The feature table to be clustered (QIIME 2 artifact, FeatureTable[Frequency]).
    reference_sequences : Path
        The reference sequences to cluster against (QIIME 2 artifact, FeatureData[Sequence]).
    perc_identity : float
        The percent identity at which to cluster. Must be between 0.0 and 1.0.
    strand : Literal["both", "plus"]
        Search plus (i.e., forward) or both strands. Defaults to 'plus'.
    threads : int
        The number of threads to use for computation. Defaults to 1.
    verbose : bool
        Display verbose output during command execution. Defaults to False.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and paths to
        the output QIIME 2 artifacts.
        - 'clustered_table': The resulting feature table.
        - 'clustered_sequences': The resulting feature sequences.
        - 'unmatched_sequences': The sequences that failed to match the reference.
    """
    # --- Input Validation ---
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequences file not found: {sequences}")
    if not table.is_file():
        raise FileNotFoundError(f"Input table file not found: {table}")
    if not reference_sequences.is_file():
        raise FileNotFoundError(
            f"Input reference sequences file not found: {reference_sequences}"
        )

    if not (0.0 <= perc_identity <= 1.0):
        raise ValueError("perc_identity must be between 0.0 and 1.0.")
    if threads <= 0:
        raise ValueError("threads must be a positive integer.")

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir)
        clustered_table = output_path / "clustered-table.qza"
        clustered_sequences = output_path / "clustered-sequences.qza"
        unmatched_sequences = output_path / "unmatched-sequences.qza"

        # --- Command Construction ---
        cmd = [
            "qiime",
            "vsearch",
            "cluster-features-closed-reference",
            "--i-sequences",
            str(sequences),
            "--i-table",
            str(table),
            "--i-reference-sequences",
            str(reference_sequences),
            "--p-perc-identity",
            str(perc_identity),
            "--p-strand",
            strand,
            "--p-threads",
            str(threads),
            "--o-clustered-table",
            str(clustered_table),
            "--o-clustered-sequences",
            str(clustered_sequences),
            "--o-unmatched-sequences",
            str(unmatched_sequences),
        ]

        if verbose:
            cmd.append("--verbose")

        # --- Subprocess Execution ---
        try:
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            stdout = process.stdout
            stderr = process.stderr
        except subprocess.CalledProcessError as e:
            return {
                "command_executed": " ".join(cmd),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode,
                "error": "QIIME 2 command failed.",
            }

        # --- Return Structured Output ---
        return {
            "command_executed": " ".join(cmd),
            "stdout": stdout,
            "stderr": stderr,
            "output_files": {
                "clustered_table": str(clustered_table),
                "clustered_sequences": str(clustered_sequences),
                "unmatched_sequences": str(unmatched_sequences),
            },
        }


if __name__ == "__main__":
    mcp.run()