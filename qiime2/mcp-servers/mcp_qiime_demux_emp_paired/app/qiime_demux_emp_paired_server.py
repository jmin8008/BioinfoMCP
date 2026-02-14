from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def demux_emp_paired(
    i_seqs: Path,
    m_barcodes_file: Path,
    m_barcodes_column: str,
    o_per_sample_sequences: Path,
    o_error_correction_details: Optional[Path] = None,
    rev_comp_mapping_barcodes: bool = False,
    rev_comp_barcodes: bool = False,
    golay_error_correction: bool = True,
    n_jobs: int = 1,
    verbose: bool = False,
) -> dict:
    """
    Demultiplex paired-end EMP protocol sequencing reads.

    This tool demultiplexes paired-end sequences that follow the Earth Microbiome
    Project (EMP) protocol, where forward, reverse, and barcode reads are in
    separate files within a QIIME 2 artifact.

    Args:
        i_seqs (Path): The QIIME 2 artifact (.qza) containing the paired-end
                       sequences to be demultiplexed (type: EMPPairedEndSequences).
        m_barcodes_file (Path): The sample metadata file (.tsv) containing barcode
                                information.
        m_barcodes_column (str): The column name in the metadata file that contains
                                 the per-sample barcodes.
        o_per_sample_sequences (Path): The path for the output QIIME 2 artifact (.qza)
                                       containing the demultiplexed sequences.
        o_error_correction_details (Optional[Path]): The path for the optional output
                                                     artifact (.qza) with details about
                                                     barcode error correction. Defaults to None.
        rev_comp_mapping_barcodes (bool): If True, reverse complement the barcode sequence
                                          reads before matching. Useful if barcode reads
                                          are in a different orientation than metadata
                                          barcodes. Defaults to False.
        rev_comp_barcodes (bool): If True, reverse complement the barcode sequences in the
                                  metadata file. Defaults to False.
        golay_error_correction (bool): If True, apply Golay error correction to barcode
                                       reads. Recommended only for Golay barcodes.
                                       Defaults to True.
        n_jobs (int): The number of parallel jobs to use for demultiplexing. Set to -1
                      to use all available CPUs. Defaults to 1.
        verbose (bool): If True, display verbose command-line output. Defaults to False.

    Returns:
        dict: A dictionary containing the executed command, stdout, stderr, and a
              dictionary of output file paths.
    """
    # --- Input Validation ---
    if not i_seqs.is_file():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_seqs}")
    if not m_barcodes_file.is_file():
        raise FileNotFoundError(f"Metadata barcodes file not found: {m_barcodes_file}")

    # --- File Path Handling ---
    # Ensure output directories exist
    o_per_sample_sequences.parent.mkdir(parents=True, exist_ok=True)
    if o_error_correction_details:
        o_error_correction_details.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = ["qiime", "demux", "emp-paired"]
    cmd.extend(["--i-seqs", str(i_seqs)])
    cmd.extend(["--m-barcodes-file", str(m_barcodes_file)])
    cmd.extend(["--m-barcodes-column", m_barcodes_column])
    cmd.extend(["--o-per-sample-sequences", str(o_per_sample_sequences)])

    if o_error_correction_details:
        cmd.extend(["--o-error-correction-details", str(o_error_correction_details)])

    # Handle boolean flags explicitly as QIIME 2 uses --p-flag/--p-no-flag pairs
    cmd.append("--p-rev-comp-mapping-barcodes" if rev_comp_mapping_barcodes else "--p-no-rev-comp-mapping-barcodes")
    cmd.append("--p-rev-comp-barcodes" if rev_comp_barcodes else "--p-no-rev-comp-barcodes")
    cmd.append("--p-golay-error-correction" if golay_error_correction else "--p-no-golay-error-correction")

    # Handle n_jobs: -1 means use all available CPUs
    n_jobs_val = n_jobs
    if n_jobs == -1:
        n_jobs_val = os.cpu_count() or 1
    cmd.extend(["--p-n-jobs", str(n_jobs_val)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        return {
            "error": "QIIME 2 is not installed or not in the system's PATH.",
            "command_executed": command_str,
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    output_files = {"per_sample_sequences": str(o_per_sample_sequences)}
    if o_error_correction_details:
        output_files["error_correction_details"] = str(o_error_correction_details)

    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()