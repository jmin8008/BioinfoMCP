import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def qiime_cutadapt_trim_paired(
    demultiplexed_sequences: Path,
    trimmed_sequences: Path,
    cores: int = 1,
    adapter_f: Optional[List[str]] = None,
    front_f: Optional[List[str]] = None,
    anywhere_f: Optional[List[str]] = None,
    adapter_r: Optional[List[str]] = None,
    front_r: Optional[List[str]] = None,
    anywhere_r: Optional[List[str]] = None,
    error_rate: float = 0.1,
    indels: bool = True,
    times: int = 1,
    overlap: int = 3,
    match_read_wildcards: bool = False,
    match_adapter_wildcards: bool = True,
    minimum_length: int = 1,
    discard_untrimmed: bool = False,
    max_n: Optional[float] = None,
    verbose: bool = False,
):
    """
    Search for and remove adapters from paired-end sequence data using cutadapt.

    This tool wraps the 'qiime cutadapt trim-paired' command. For an overview of
    available adapter types and calling conventions, see the cutadapt documentation.
    """
    # --- Input Validation ---
    if not demultiplexed_sequences.is_file():
        raise ValueError(
            f"Input file not found: {demultiplexed_sequences}"
        )

    if not trimmed_sequences.parent.is_dir():
        raise ValueError(
            f"Output directory does not exist: {trimmed_sequences.parent}"
        )

    if cores < 1:
        raise ValueError("--p-cores must be at least 1.")
    if not (0.0 <= error_rate <= 1.0):
        raise ValueError("--p-error-rate must be between 0.0 and 1.0.")
    if times < 1:
        raise ValueError("--p-times must be at least 1.")
    if overlap < 1:
        raise ValueError("--p-overlap must be at least 1.")
    if minimum_length < 1:
        raise ValueError("--p-minimum-length must be at least 1.")
    if max_n is not None and not (0.0 <= max_n <= 1.0):
        raise ValueError("--p-max-n must be between 0.0 and 1.0 if provided.")

    # --- Command Construction ---
    cmd = [
        "qiime",
        "cutadapt",
        "trim-paired",
        "--i-demultiplexed-sequences",
        str(demultiplexed_sequences),
        "--o-trimmed-sequences",
        str(trimmed_sequences),
        "--p-cores",
        str(cores),
        "--p-error-rate",
        str(error_rate),
        "--p-times",
        str(times),
        "--p-overlap",
        str(overlap),
        "--p-minimum-length",
        str(minimum_length),
    ]

    # Add list-based adapter parameters
    adapter_params = {
        "--p-adapter-f": adapter_f,
        "--p-front-f": front_f,
        "--p-anywhere-f": anywhere_f,
        "--p-adapter-r": adapter_r,
        "--p-front-r": front_r,
        "--p-anywhere-r": anywhere_r,
    }
    for flag, values in adapter_params.items():
        if values:
            for value in values:
                cmd.extend([flag, value])

    # Add boolean flag pairs
    cmd.append("--p-indels" if indels else "--p-no-indels")
    cmd.append(
        "--p-match-read-wildcards"
        if match_read_wildcards
        else "--p-no-match-read-wildcards"
    )
    cmd.append(
        "--p-match-adapter-wildcards"
        if match_adapter_wildcards
        else "--p-no-match-adapter-wildcards"
    )
    cmd.append(
        "--p-discard-untrimmed"
        if discard_untrimmed
        else "--p-no-discard-untrimmed"
    )

    # Add optional parameters
    if max_n is not None:
        cmd.extend(["--p-max-n", str(max_n)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(trimmed_sequences)],
        }
    except subprocess.CalledProcessError as e:
        # In case of an error, return a structured error message
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "output_files": [],
        }
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and in your PATH.",
            "error": "Command not found",
            "output_files": [],
        }


if __name__ == "__main__":
    mcp.run()