from fastmcp import FastMCP
import subprocess
import logging
from pathlib import Path
from typing import Literal, Dict, Union

# Initialize the MCP application
mcp = FastMCP()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def qiime_dada2_denoise_single(
    demultiplexed_seqs: Path,
    table: Path,
    representative_sequences: Path,
    denoising_stats: Path,
    trunc_len: int = 0,
    trim_left: int = 0,
    max_ee_f: float = 2.0,
    trunc_q: int = 2,
    pooling_method: Literal['independent', 'pseudo'] = 'independent',
    chimera_method: Literal['none', 'pooled', 'consensus'] = 'consensus',
    min_fold_parent_over_abundance: float = 1.0,
    n_threads: int = 1,
    n_reads_learn: int = 1000000,
    hashed_feature_ids: bool = True,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Union[str, int, Dict[str, str]]]:
    """
    Denoises single-end sequences, resolves sequence variants (SVs), and removes chimeras using DADA2.

    This method is part of the QIIME 2 DADA2 plugin and serves as a quality control
    and feature table generation step for single-end amplicon sequencing data.

    Args:
        demultiplexed_seqs: The single-end sequences to be denoised (QIIME 2 artifact).
        table: The path for the output feature table (QIIME 2 artifact).
        representative_sequences: The path for the output feature sequences (QIIME 2 artifact).
        denoising_stats: The path for the output denoising stats (QIIME 2 artifact).
        trunc_len: Position at which sequences should be truncated. Reads shorter will be discarded. 0 means no truncation.
        trim_left: Position at which sequences should be trimmed from the 5' end.
        max_ee_f: Reads with expected errors higher than this value will be discarded.
        trunc_q: Reads are truncated at the first instance of a quality score <= this value.
        pooling_method: Method to pool samples for denoising ('independent' or 'pseudo').
        chimera_method: Method to remove chimeras ('none', 'pooled', or 'consensus').
        min_fold_parent_over_abundance: Minimum fold increase for a sequence to be considered a chimera.
        n_threads: Number of threads for multithreaded processing. 0 uses all available cores.
        n_reads_learn: Number of reads to use when training the error model.
        hashed_feature_ids: If true, feature IDs will be MD5 hashes of the sequences.
        verbose: Display verbose output.
        quiet: Suppress standard output.

    Returns:
        A dictionary containing the execution command, stdout, stderr, and a map of output file paths.
    """
    # --- Input Validation ---
    if not demultiplexed_seqs.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_seqs}")

    if trunc_len < 0:
        raise ValueError("--p-trunc-len must be a non-negative integer.")
    if trim_left < 0:
        raise ValueError("--p-trim-left must be a non-negative integer.")
    if max_ee_f < 0.0:
        raise ValueError("--p-max-ee-f must be a non-negative float.")
    if trunc_q < 0:
        raise ValueError("--p-trunc-q must be a non-negative integer.")
    if n_threads < 0:
        raise ValueError("--p-n-threads must be a non-negative integer.")
    if n_reads_learn <= 0:
        raise ValueError("--p-n-reads-learn must be a positive integer.")
    if min_fold_parent_over_abundance < 0.0:
        raise ValueError("--p-min-fold-parent-over-abundance must be a non-negative float.")
    if verbose and quiet:
        raise ValueError("Cannot set both --verbose and --quiet flags simultaneously.")

    # --- File Path Handling ---
    # Ensure output directories exist to prevent command failure
    for output_path in [table, representative_sequences, denoising_stats]:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "dada2", "denoise-single",
        "--i-demultiplexed-seqs", str(demultiplexed_seqs),
        "--o-table", str(table),
        "--o-representative-sequences", str(representative_sequences),
        "--o-denoising-stats", str(denoising_stats),
        "--p-trunc-len", str(trunc_len),
        "--p-trim-left", str(trim_left),
        "--p-max-ee-f", str(max_ee_f),
        "--p-trunc-q", str(trunc_q),
        "--p-pooling-method", pooling_method,
        "--p-chimera-method", chimera_method,
        "--p-min-fold-parent-over-abundance", str(min_fold_parent_over_abundance),
        "--p-n-threads", str(n_threads),
        "--p-n-reads-learn", str(n_reads_learn),
    ]

    if hashed_feature_ids:
        cmd.append("--p-hashed-feature-ids")
    else:
        # QIIME 2 uses --p-no-<flag> for disabling boolean flags that default to True
        cmd.append("--p-no-hashed-feature-ids")

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
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        # This handles the case where 'qiime' is not in the system's PATH
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and activated in your environment.",
            "error": "Command not found",
            "return_code": 127,
            "output_files": {}
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 dada2 denoise-single failed.",
            "return_code": e.returncode,
            "output_files": {}
        }

    # --- Structured Result Return ---
    output_files = {
        "table": str(table),
        "representative_sequences": str(representative_sequences),
        "denoising_stats": str(denoising_stats),
    }

    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()