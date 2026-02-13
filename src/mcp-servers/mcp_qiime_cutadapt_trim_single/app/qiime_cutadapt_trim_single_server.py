from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

mcp = FastMCP()

@mcp.tool()
def qiime_cutadapt_trim_single(
    demultiplexed_sequences: Path,
    trimmed_sequences: Path,
    cores: int = 1,
    adapter: Optional[List[str]] = None,
    front: Optional[List[str]] = None,
    anywhere: Optional[List[str]] = None,
    error_rate: float = 0.1,
    indels: bool = True,
    times: int = 1,
    overlap: int = 3,
    match_read_wildcards: bool = False,
    match_adapter_wildcards: bool = True,
    minimum_length: int = 0,
    discard_untrimmed: bool = False,
    max_n: Optional[float] = None,
    verbose: bool = False,
) -> Dict:
    """
    Finds and removes adapters in single-end reads using QIIME 2's cutadapt plugin.

    This tool wraps the 'qiime cutadapt trim-single' command. For more details,
    refer to the official QIIME 2 and cutadapt documentation.

    Args:
        demultiplexed_sequences: Path to the demultiplexed single-end sequences artifact (.qza).
        trimmed_sequences: Path to the output trimmed sequences artifact (.qza).
        cores: Number of CPU cores to use.
        adapter: Sequence of an adapter ligated to the 3' end.
        front: Sequence of an adapter ligated to the 5' end.
        anywhere: Sequence of an adapter that may be ligated to the 5' or 3' end.
        error_rate: Maximum allowed error rate for adapter matching.
        indels: Allow insertions or deletions of bases when matching adapters.
        times: Remove multiple occurrences of an adapter if it is present more than once.
        overlap: Minimum overlap between read and adapter for a match.
        match_read_wildcards: Interpret IUPAC wildcards in reads.
        match_adapter_wildcards: Interpret IUPAC wildcards in adapters.
        minimum_length: Discard reads shorter than this length.
        discard_untrimmed: Discard reads in which no adapter was found.
        max_n: Discard reads with more than N bases. If the value is between 0 and 1,
               it is interpreted as a rate.
        verbose: Display verbose output during command execution.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output files.
    """
    # Input validation
    if not demultiplexed_sequences.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_sequences}")
    if not trimmed_sequences.parent.exists():
        trimmed_sequences.parent.mkdir(parents=True, exist_ok=True)

    if cores < 1:
        raise ValueError("Parameter 'cores' must be a positive integer.")
    if not (0.0 <= error_rate <= 1.0):
        raise ValueError("Parameter 'error_rate' must be between 0.0 and 1.0.")
    if times < 1:
        raise ValueError("Parameter 'times' must be a positive integer.")
    if overlap < 1:
        raise ValueError("Parameter 'overlap' must be a positive integer.")
    if minimum_length < 0:
        raise ValueError("Parameter 'minimum_length' must be a non-negative integer.")
    if max_n is not None and max_n < 0:
        raise ValueError("Parameter 'max_n' must be a non-negative value.")

    # Command construction
    cmd = [
        "qiime", "cutadapt", "trim-single",
        "--i-demultiplexed-sequences", str(demultiplexed_sequences),
        "--o-trimmed-sequences", str(trimmed_sequences),
        "--p-cores", str(cores),
        "--p-error-rate", str(error_rate),
        "--p-times", str(times),
        "--p-overlap", str(overlap),
        "--p-minimum-length", str(minimum_length),
    ]

    if adapter:
        for seq in adapter:
            cmd.extend(["--p-adapter", seq])
    if front:
        for seq in front:
            cmd.extend(["--p-front", seq])
    if anywhere:
        for seq in anywhere:
            cmd.extend(["--p-anywhere", seq])

    cmd.append("--p-indels" if indels else "--p-no-indels")
    cmd.append("--p-match-read-wildcards" if match_read_wildcards else "--p-no-match-read-wildcards")
    cmd.append("--p-match-adapter-wildcards" if match_adapter_wildcards else "--p-no-match-adapter-wildcards")
    cmd.append("--p-discard-untrimmed" if discard_untrimmed else "--p-no-discard-untrimmed")

    if max_n is not None:
        cmd.extend(["--p-max-n", str(max_n)])

    if verbose:
        cmd.append("--verbose")

    # Subprocess execution
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "trimmed_sequences": str(trimmed_sequences)
            }
        }
    except FileNotFoundError:
        raise RuntimeError("qiime command not found. Please ensure QIIME 2 is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        # Return structured error information
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "output_files": {}
        }

if __name__ == '__main__':
    mcp.run()