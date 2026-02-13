from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import shlex

mcp = FastMCP()

@mcp.tool()
def quality_filter_q_score(
    demux: Path,
    filtered_sequences: Path,
    filter_stats: Path,
    min_quality: int = 4,
    quality_window: int = 3,
    min_length_fraction: float = 0.75,
    max_ambiguous: int = 0,
    mode: str = "sliding-window",
    window_size: int = 50,
    threads: int = 1,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """
    Filter reads from a demultiplexed QIIME 2 artifact based on quality scores.

    This tool filters reads based on a variety of quality metrics, including
    minimum quality score, number of low-quality positions, read length, and
    ambiguous bases. It supports both 'exact' and 'sliding-window' filtering modes.
    """
    # --- Input Validation ---
    if not demux.is_file():
        raise FileNotFoundError(f"Input demultiplexed sequences artifact not found at: {demux}")

    # Ensure output directories exist
    try:
        filtered_sequences.parent.mkdir(parents=True, exist_ok=True)
        filter_stats.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create output directories: {e}")

    if min_quality < 0:
        raise ValueError("min_quality must be a non-negative integer.")
    if quality_window < 0:
        raise ValueError("quality_window must be a non-negative integer.")
    if not (0.0 <= min_length_fraction <= 1.0):
        raise ValueError("min_length_fraction must be a float between 0.0 and 1.0.")
    if max_ambiguous < 0:
        raise ValueError("max_ambiguous must be a non-negative integer.")
    if mode not in ["exact", "sliding-window"]:
        raise ValueError("mode must be either 'exact' or 'sliding-window'.")
    if window_size <= 0:
        raise ValueError("window_size must be a positive integer.")
    if threads <= 0:
        raise ValueError("threads must be a positive integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "quality-filter", "q-score",
        "--i-demux", str(demux),
        "--o-filtered-sequences", str(filtered_sequences),
        "--o-filter-stats", str(filter_stats),
        "--p-min-quality", str(min_quality),
        "--p-quality-window", str(quality_window),
        "--p-min-length-fraction", str(min_length_fraction),
        "--p-max-ambiguous", str(max_ambiguous),
        "--p-mode", mode,
        "--p-window-size", str(window_size),
        "--p-threads", str(threads),
    ]

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = shlex.join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        
        output_files = [str(filtered_sequences), str(filter_stats)]

        # --- Structured Result Return ---
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files
        }
    except FileNotFoundError:
        error_message = "QIIME 2 is not installed or not in the system's PATH. Please ensure the 'qiime' command is accessible."
        return {
            "error": error_message,
            "command_executed": command_str,
            "stdout": "",
            "stderr": "",
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

if __name__ == '__main__':
    mcp.run()