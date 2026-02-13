from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Dict
import logging

# Initialize the MCP server
mcp = FastMCP()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@mcp.tool()
def qiime_cutadapt_demux_single(
    i_seqs: Path,
    m_barcodes_file: Path,
    m_barcodes_column: str,
    o_per_sample_sequences: Path,
    o_untrimmed_sequences: Path,
    p_error_rate: float = 0.1,
    p_batch_size: int = 0,
    p_minimum_length: int = 1,
    p_mixed_orientation: bool = False,
    p_cores: int = 1,
    verbose: bool = False,
) -> Dict:
    """
    Demultiplex single-end sequence data with barcodes in-sequence using QIIME 2's cutadapt plugin.

    This tool uses barcode sequences in a metadata file to assign reads from a
    multiplexed sequencing run to their respective samples. Reads that are not
    successfully assigned to a sample are written to a separate output file.

    Args:
        i_seqs (Path): The single-end sequences to be demultiplexed (QIIME 2 artifact: .qza).
        m_barcodes_file (Path): The sample metadata file containing the per-sample barcodes.
        m_barcodes_column (str): The column in the sample metadata file containing the barcodes.
        o_per_sample_sequences (Path): The path to write the resulting demultiplexed sequences artifact.
        o_untrimmed_sequences (Path): The path to write the sequences that were not demultiplexed.
        p_error_rate (float, optional): The maximum allowable error rate for barcode matching. Defaults to 0.1.
        p_batch_size (int, optional): The number of samples to be processed in a batch. Use 0 for automatic batch size. Defaults to 0.
        p_minimum_length (int, optional): The minimum length of a read to be retained after demultiplexing. Defaults to 1.
        p_mixed_orientation (bool, optional): Allow barcodes to be in forward or reverse-complement orientation. Defaults to False.
        p_cores (int, optional): The number of cores to use. Use 0 to use all available cores. Defaults to 1.
        verbose (bool, optional): Display verbose output during command execution. Defaults to False.

    Returns:
        Dict: A dictionary containing the execution details, including the command, stdout, stderr, and output file paths.
    """
    # --- Input Validation ---
    if not i_seqs.is_file():
        raise FileNotFoundError(f"Input sequences artifact not found at: {i_seqs}")
    if not m_barcodes_file.is_file():
        raise FileNotFoundError(f"Barcodes metadata file not found at: {m_barcodes_file}")
    if not m_barcodes_column.strip():
        raise ValueError("Barcode column name (--m-barcodes-column) cannot be empty.")

    if not (0.0 <= p_error_rate <= 1.0):
        raise ValueError(f"Error rate (--p-error-rate) must be between 0.0 and 1.0, but got {p_error_rate}.")
    if p_batch_size < 0:
        raise ValueError(f"Batch size (--p-batch-size) must be a non-negative integer, but got {p_batch_size}.")
    if p_minimum_length < 1:
        raise ValueError(f"Minimum length (--p-minimum-length) must be at least 1, but got {p_minimum_length}.")
    if p_cores < 0:
        raise ValueError(f"Number of cores (--p-cores) must be a non-negative integer, but got {p_cores}.")

    # --- Output Path Handling ---
    # Create parent directories for output files if they don't exist
    o_per_sample_sequences.parent.mkdir(parents=True, exist_ok=True)
    o_untrimmed_sequences.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "cutadapt", "demux-single",
        "--i-seqs", str(i_seqs),
        "--m-barcodes-file", str(m_barcodes_file),
        "--m-barcodes-column", m_barcodes_column,
        "--o-per-sample-sequences", str(o_per_sample_sequences),
        "--o-untrimmed-sequences", str(o_untrimmed_sequences),
        "--p-error-rate", str(p_error_rate),
        "--p-batch-size", str(p_batch_size),
        "--p-minimum-length", str(p_minimum_length),
        "--p-cores", str(p_cores),
    ]

    if p_mixed_orientation:
        cmd.append("--p-mixed-orientation")
    
    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        # This error is caught if the 'qiime' command itself is not found.
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in your system's PATH.")
    except subprocess.CalledProcessError as e:
        # This error is caught for non-zero exit codes from the tool.
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        logging.error(f"Stdout: {e.stdout}")
        # Return a structured error for the client
        return {
            "error": "Command execution failed.",
            "command_executed": command_executed,
            "exit_code": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
        }

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

if __name__ == '__main__':
    mcp.run()