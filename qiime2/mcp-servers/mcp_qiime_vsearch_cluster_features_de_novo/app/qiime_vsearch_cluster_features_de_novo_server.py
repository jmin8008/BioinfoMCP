from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List

mcp = FastMCP()

@mcp.tool()
def qiime_vsearch_cluster_features_de_novo(
    sequences: Path,
    table: Path,
    clustered_table: Path,
    clustered_sequences: Path,
    perc_identity: float,
    threads: int = 1,
    verbose: bool = False,
):
    """
    De-replicate and cluster features that are >= a specified percent identity.

    This tool uses the vsearch command-line tool to perform de novo clustering
    of features (e.g., ASVs) based on sequence similarity. It corresponds to the
    `qiime vsearch cluster-features-de-novo` command.

    Parameters
    ----------
    sequences : Path
        The sequences to be clustered. (QIIME 2 artifact: FeatureData[Sequence])
        Corresponds to the `--i-sequences` parameter.
    table : Path
        The feature table containing the features to be clustered. (QIIME 2 artifact: FeatureTable[Frequency])
        Corresponds to the `--i-table` parameter.
    clustered_table : Path
        The path to write the resulting clustered feature table. (QIIME 2 artifact: FeatureTable[Frequency])
        Corresponds to the `--o-clustered-table` parameter.
    clustered_sequences : Path
        The path to write the resulting clustered sequences. (QIIME 2 artifact: FeatureData[Sequence])
        Corresponds to the `--o-clustered-sequences` parameter.
    perc_identity : float
        The percent identity at which to cluster sequences. Must be between 0.0 and 1.0.
        Corresponds to the `--p-perc-identity` parameter.
    threads : int, optional
        The number of threads to use for multithreaded processing. Default is 1.
        Corresponds to the `--p-threads` parameter.
    verbose : bool, optional
        Display verbose output during command execution. Default is False.
        Corresponds to the `--verbose` flag.

    Returns
    -------
    dict
        A dictionary containing the execution command, stdout, stderr, and a list of output file paths.
    """
    # --- Input Validation ---
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequences file not found at: {sequences}")
    if not table.is_file():
        raise FileNotFoundError(f"Input table file not found at: {table}")

    if not (0.0 <= perc_identity <= 1.0):
        raise ValueError("perc_identity must be between 0.0 and 1.0, inclusive.")
    
    if threads < 1:
        raise ValueError("threads must be a positive integer (>= 1).")

    # Ensure output directories exist to avoid errors from the tool
    clustered_table.parent.mkdir(parents=True, exist_ok=True)
    clustered_sequences.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "vsearch", "cluster-features-de-novo",
        "--i-sequences", str(sequences),
        "--i-table", str(table),
        "--p-perc-identity", str(perc_identity),
        "--o-clustered-table", str(clustered_table),
        "--o-clustered-sequences", str(clustered_sequences),
        "--p-threads", str(threads),
    ]

    if verbose:
        cmd.append("--verbose")

    command_string = " ".join(cmd)

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        output_files = [str(clustered_table), str(clustered_sequences)]

    except FileNotFoundError:
        return {
            "command_executed": command_string,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your system's PATH.",
            "output_files": [],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_string,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_string,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()