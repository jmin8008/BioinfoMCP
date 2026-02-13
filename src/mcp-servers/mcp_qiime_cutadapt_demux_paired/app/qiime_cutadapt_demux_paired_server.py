from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional

mcp = FastMCP()

@mcp.tool()
def qiime_cutadapt_demux_paired(
    i_seqs: Path,
    m_forward_barcodes_file: Path,
    m_forward_barcodes_column: str,
    o_per_sample_sequences: Path,
    o_untrimmed_sequences: Path,
    m_reverse_barcodes_file: Optional[Path] = None,
    m_reverse_barcodes_column: Optional[str] = None,
    error_rate: float = 0.1,
    batch_size: int = 0,
    minimum_length: int = 1,
    mixed_orientation: bool = False,
    cores: int = 1,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Demultiplex paired-end sequence data using QIIME 2's cutadapt plugin.

    This method supports demultiplexing paired-end sequence data that contain
    in-line barcodes. Barcodes can be at the 5' or 3' end of either the
    forward or reverse reads. All barcodes will be removed from the reads.

    Args:
        i_seqs: The paired-end sequences to be demultiplexed (QIIME 2 artifact).
        m_forward_barcodes_file: The file containing the forward barcodes.
        m_forward_barcodes_column: The column name in the barcode file that contains the forward barcodes.
        o_per_sample_sequences: The output path for the resulting demultiplexed sequences artifact.
        o_untrimmed_sequences: The output path for the sequences that were not demultiplexed artifact.
        m_reverse_barcodes_file: The file containing the reverse barcodes.
        m_reverse_barcodes_column: The column name in the barcode file that contains the reverse barcodes.
        error_rate: The level of error tolerance for barcode matching.
        batch_size: The number of samples to be processed in a batch (0 for auto-detect).
        minimum_length: Discard reads shorter than this length.
        mixed_orientation: Allow reads to be in mixed orientation (barcodes at 5' or 3' end).
        cores: Number of cores to use for multiprocessing.
        verbose: Display verbose output to stdout.
        quiet: Silence output if execution is successful.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and output file paths.
    """
    # --- Input Validation ---
    if not i_seqs.is_file():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_seqs}")
    if not m_forward_barcodes_file.is_file():
        raise FileNotFoundError(f"Forward barcodes metadata file not found: {m_forward_barcodes_file}")

    if (m_reverse_barcodes_file is not None and m_reverse_barcodes_column is None) or \
       (m_reverse_barcodes_file is None and m_reverse_barcodes_column is not None):
        raise ValueError("Both --m-reverse-barcodes-file and --m-reverse-barcodes-column must be provided together.")

    if m_reverse_barcodes_file and not m_reverse_barcodes_file.is_file():
        raise FileNotFoundError(f"Reverse barcodes metadata file not found: {m_reverse_barcodes_file}")

    if not (0.0 <= error_rate <= 1.0):
        raise ValueError(f"Error rate must be between 0.0 and 1.0, but got {error_rate}")

    if batch_size < 0:
        raise ValueError(f"Batch size must be a non-negative integer, but got {batch_size}")

    if minimum_length < 1:
        raise ValueError(f"Minimum length must be at least 1, but got {minimum_length}")

    if cores < 1:
        raise ValueError(f"Number of cores must be at least 1, but got {cores}")

    if verbose and quiet:
        raise ValueError("Cannot use --verbose and --quiet flags simultaneously.")

    # --- Command Construction ---
    cmd = [
        "qiime", "cutadapt", "demux-paired",
        "--i-seqs", str(i_seqs),
        "--m-forward-barcodes-file", str(m_forward_barcodes_file),
        "--m-forward-barcodes-column", m_forward_barcodes_column,
        "--o-per-sample-sequences", str(o_per_sample_sequences),
        "--o-untrimmed-sequences", str(o_untrimmed_sequences),
        "--p-error-rate", str(error_rate),
        "--p-batch-size", str(batch_size),
        "--p-minimum-length", str(minimum_length),
        "--p-cores", str(cores)
    ]

    if m_reverse_barcodes_file and m_reverse_barcodes_column:
        cmd.extend(["--m-reverse-barcodes-file", str(m_reverse_barcodes_file)])
        cmd.extend(["--m-reverse-barcodes-column", m_reverse_barcodes_column])

    if mixed_orientation:
        cmd.append("--p-mixed-orientation")
    # The default is --p-no-mixed-orientation, which is applied if --p-mixed-orientation is absent.

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        # --- Structured Result Return ---
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "per_sample_sequences": str(o_per_sample_sequences),
                "untrimmed_sequences": str(o_untrimmed_sequences)
            }
        }
    except FileNotFoundError:
        raise RuntimeError("qiime command not found. Please ensure QIIME 2 is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        # Capture and return structured error info
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 cutadapt demux-paired command failed.",
            "return_code": e.returncode
        }

if __name__ == '__main__':
    mcp.run()