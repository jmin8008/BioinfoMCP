from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, List
import logging

# Initialize the MCP server
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def mafft(
    sequences: Path,
    alignment: Path,
    n_threads: int = 1,
    parttree: bool = False,
    mafft_args: Optional[List[str]] = None,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Aligns sequences using MAFFT within the QIIME 2 framework.

    This method wraps the 'qiime alignment mafft' command.

    Args:
        sequences: Path to the input sequences artifact (FeatureData[Sequence]).
        alignment: Path for the output aligned sequences artifact (FeatureData[AlignedSequence]).
        n_threads: The number of threads to use. Use 0 to automatically use all available cores.
        parttree: Use the --parttree option of MAFFT, recommended for datasets with a few hundred sequences.
        mafft_args: Additional arguments to pass directly to the mafft command.
        verbose: Display verbose output during execution.
        quiet: Silence output if execution is successful.

    Returns:
        A dictionary containing the execution command, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequences file not found at: {sequences}")
    if not alignment.parent.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {alignment.parent}")
    if n_threads < 0:
        raise ValueError("n_threads must be a non-negative integer (0 for auto).")

    # --- Command Construction ---
    cmd = [
        "qiime", "alignment", "mafft",
        "--i-sequences", str(sequences),
        "--o-alignment", str(alignment),
        "--p-n-threads", str(n_threads),
    ]

    if parttree:
        cmd.append("--p-parttree")

    if mafft_args:
        # QIIME 2 expects multiple arguments for --p-mafft-args to be passed one by one
        cmd.append("--p-mafft-args")
        cmd.extend(mafft_args)

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(alignment)],
        }
    except FileNotFoundError:
        err_msg = "Error: 'qiime' command not found. Is QIIME 2 installed and in your PATH?"
        logging.error(err_msg)
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 mafft command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
            "error": f"Command failed with exit code {e.returncode}",
        }

@mcp.tool()
def mafft_add(
    alignment: Path,
    sequences: Path,
    output_alignment: Path,
    n_threads: int = 1,
    mafft_args: Optional[List[str]] = None,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Adds new sequences to an existing alignment using MAFFT.

    This method wraps the 'qiime alignment mafft-add' command.

    Args:
        alignment: Path to the existing alignment artifact (FeatureData[AlignedSequence]).
        sequences: Path to the new sequences artifact to be added (FeatureData[Sequence]).
        output_alignment: Path for the output alignment with new sequences (FeatureData[AlignedSequence]).
        n_threads: The number of threads to use. Use 0 to automatically use all available cores.
        mafft_args: Additional arguments to pass directly to the mafft command.
        verbose: Display verbose output during execution.
        quiet: Silence output if execution is successful.

    Returns:
        A dictionary containing the execution command, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequences file not found at: {sequences}")
    if not output_alignment.parent.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {output_alignment.parent}")
    if n_threads < 0:
        raise ValueError("n_threads must be a non-negative integer (0 for auto).")

    # --- Command Construction ---
    cmd = [
        "qiime", "alignment", "mafft-add",
        "--i-alignment", str(alignment),
        "--i-sequences", str(sequences),
        "--o-alignment", str(output_alignment),
        "--p-n-threads", str(n_threads),
    ]

    if mafft_args:
        cmd.append("--p-mafft-args")
        cmd.extend(mafft_args)

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(output_alignment)],
        }
    except FileNotFoundError:
        err_msg = "Error: 'qiime' command not found. Is QIIME 2 installed and in your PATH?"
        logging.error(err_msg)
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 mafft-add command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
            "error": f"Command failed with exit code {e.returncode}",
        }

@mcp.tool()
def mask(
    alignment: Path,
    masked_alignment: Path,
    max_gap_frequency: float = 1.0,
    min_conservation: float = 0.4,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Masks sites in a sequence alignment that are highly variable or contain a high frequency of gaps.

    This method wraps the 'qiime alignment mask' command.

    Args:
        alignment: Path to the alignment artifact to be masked (FeatureData[AlignedSequence]).
        masked_alignment: Path for the output masked alignment artifact (FeatureData[AlignedSequence]).
        max_gap_frequency: The maximum relative frequency of gaps in a column for it to be retained.
        min_conservation: The minimum relative frequency of a non-gap character for a column to be retained.
        verbose: Display verbose output during execution.
        quiet: Silence output if execution is successful.

    Returns:
        A dictionary containing the execution command, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")
    if not masked_alignment.parent.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {masked_alignment.parent}")
    if not (0.0 <= max_gap_frequency <= 1.0):
        raise ValueError("max_gap_frequency must be between 0.0 and 1.0.")
    if not (0.0 <= min_conservation <= 1.0):
        raise ValueError("min_conservation must be between 0.0 and 1.0.")

    # --- Command Construction ---
    cmd = [
        "qiime", "alignment", "mask",
        "--i-alignment", str(alignment),
        "--o-masked-alignment", str(masked_alignment),
        "--p-max-gap-frequency", str(max_gap_frequency),
        "--p-min-conservation", str(min_conservation),
    ]

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(masked_alignment)],
        }
    except FileNotFoundError:
        err_msg = "Error: 'qiime' command not found. Is QIIME 2 installed and in your PATH?"
        logging.error(err_msg)
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 mask command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
            "error": f"Command failed with exit code {e.returncode}",
        }

if __name__ == '__main__':
    mcp.run()