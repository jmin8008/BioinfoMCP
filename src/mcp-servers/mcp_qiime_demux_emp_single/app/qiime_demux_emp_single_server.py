import subprocess
from pathlib import Path
from typing import Optional
import logging

from fastmcp import FastMCP

mcp = FastMCP()

logging.basicConfig(level=logging.INFO)

@mcp.tool()
def demux_emp_single(
    seqs: Path,
    barcodes_file: Path,
    barcodes_column: str,
    per_sample_sequences: Path,
    error_correction_details: Optional[Path] = None,
    rev_comp_barcodes: bool = False,
    rev_comp_mapping_barcodes: bool = False,
    golay_error_correction: bool = True,
    n_jobs: int = 1,
    verbose: bool = False,
) -> dict:
    """
    Demultiplex single-end EMP-protocol sequence data.

    This tool demultiplexes single-end sequence data that was generated using the
    Earth Microbiome Project (EMP) protocol. It uses a metadata file containing
    barcodes to assign sequences to their respective samples.

    Args:
        seqs: The single-end sequences to be demultiplexed (QIIME2 artifact, .qza).
        barcodes_file: The sample metadata file containing the per-sample barcodes (.tsv).
        barcodes_column: The column in the sample metadata file containing the barcodes.
        per_sample_sequences: The path for the resulting demultiplexed sequences artifact (.qza).
        error_correction_details: Optional path to save details about the error correction process (.qza).
        rev_comp_barcodes: Reverse-complement the barcodes before searching for them in the sequence data.
                           If your barcodes are in the standard 5'->3' orientation, you should not enable this.
        rev_comp_mapping_barcodes: Reverse-complement the barcodes in the mapping file before searching.
        golay_error_correction: Perform 12nt Golay error correction on the barcode reads.
        n_jobs: The number of parallel jobs to use.
        verbose: Display verbose output when running the command.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not seqs.is_file():
        raise FileNotFoundError(f"Input sequence artifact not found at: {seqs}")
    if not barcodes_file.is_file():
        raise FileNotFoundError(f"Barcodes metadata file not found at: {barcodes_file}")
    if n_jobs <= 0:
        raise ValueError("n_jobs must be a positive integer.")

    # Ensure output directories exist
    per_sample_sequences.parent.mkdir(parents=True, exist_ok=True)
    if error_correction_details:
        error_correction_details.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "demux", "emp-single",
        "--i-seqs", str(seqs),
        "--m-barcodes-file", str(barcodes_file),
        "--m-barcodes-column", barcodes_column,
        "--o-per-sample-sequences", str(per_sample_sequences),
    ]

    if error_correction_details:
        cmd.extend(["--o-error-correction-details", str(error_correction_details)])

    # Handle boolean flags based on QIIME2's convention
    cmd.append("--p-rev-comp-barcodes" if rev_comp_barcodes else "--p-no-rev-comp-barcodes")
    cmd.append("--p-rev-comp-mapping-barcodes" if rev_comp_mapping_barcodes else "--p-no-rev-comp-mapping-barcodes")
    cmd.append("--p-golay-error-correction" if golay_error_correction else "--p-no-golay-error-correction")

    cmd.extend(["--p-n-jobs", str(n_jobs)])

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
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME2 command failed.",
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    output_files = [str(per_sample_sequences)]
    if error_correction_details:
        output_files.append(str(error_correction_details))

    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()