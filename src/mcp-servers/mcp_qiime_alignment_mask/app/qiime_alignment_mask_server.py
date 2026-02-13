from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Dict
import logging

# Initialize MCP and logger
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def mask(
    alignment: Path,
    masked_alignment: Path,
    max_gap_frequency: float = 1.0,
    min_conservation: float = 0.0,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict:
    """
    Masks phylogenetically uninformative or ambiguously aligned sites in a sequence alignment using QIIME 2.

    This method masks sites in a sequence alignment that are phylogenetically
    uninformative or ambiguously aligned. The masked alignment can be used in
    downstream analyses (e.g., phylogenetic reconstruction).

    Args:
        alignment: The input alignment artifact file to be masked. (QIIME 2 format: .qza)
        masked_alignment: The path for the output masked alignment artifact. (QIIME 2 format: .qza)
        max_gap_frequency: The maximum relative frequency of gap characters for a
                           column to be retained. Columns with more than this
                           proportion of gaps will be removed. Set to 1.0 to disable.
        min_conservation: The minimum relative frequency of a dominant character
                          for a column to be retained. A column will be retained
                          if its most-frequent character is present in at least
                          this proportion of the sequences. Set to 0.0 to disable.
        verbose: Display verbose output to stdout.
        quiet: Display quiet output to stdout. Cannot be used with --verbose.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output files.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")

    if not masked_alignment.parent.exists():
        try:
            masked_alignment.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {masked_alignment.parent}")
        except OSError as e:
            raise OSError(f"Could not create output directory: {masked_alignment.parent}. Error: {e}")

    if not (0.0 <= max_gap_frequency <= 1.0):
        raise ValueError("max_gap_frequency must be between 0.0 and 1.0.")

    if not (0.0 <= min_conservation <= 1.0):
        raise ValueError("min_conservation must be between 0.0 and 1.0.")

    if verbose and quiet:
        raise ValueError("The --verbose and --quiet flags are mutually exclusive.")

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
    logger.info(f"Executing command: {command_str}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        logger.info("QIIME alignment mask completed successfully.")

    except FileNotFoundError:
        raise RuntimeError(
            "`qiime` command not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME alignment mask failed with exit code {e.returncode}")
        raise RuntimeError(
            f"QIIME alignment mask failed.\n"
            f"Exit Code: {e.returncode}\n"
            f"Command: {command_str}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "masked_alignment": str(masked_alignment)
        }
    }

if __name__ == '__main__':
    mcp.run()