from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Literal, Dict
import logging

# Initialize MCP and logger
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def denoise_pyro(
    demultiplexed_seqs: Path,
    table: Path,
    representative_sequences: Path,
    denoising_stats: Path,
    trunc_len: int,
    trim_left: int = 0,
    max_ee: float = 2.0,
    trunc_q: int = 2,
    max_len: int = 0,
    chimera_method: Literal["none", "pooled", "consensus"] = "consensus",
    min_fold_parent_over_abundance: float = 1.0,
    n_threads: int = 1,
    n_reads_learn: int = 1000000,
    hashed_feature_ids: bool = True,
    verbose: bool = False,
) -> Dict:
    """
    Denoises pyrosequenced reads using DADA2.

    This method denoises pyrosequenced reads, resolves them into exact amplicon
    sequence variants (ASVs), and counts their abundances. It is a wrapper for
    the 'qiime dada2 denoise-pyro' command.
    """
    # --- Input Validation ---
    if not demultiplexed_seqs.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_seqs}")

    if trunc_len <= 0:
        raise ValueError("--p-trunc-len must be a positive integer.")
    if trim_left < 0:
        raise ValueError("--p-trim-left must be a non-negative integer.")
    if trim_left >= trunc_len:
        raise ValueError("--p-trim-left must be less than --p-trunc-len.")
    if max_ee < 0:
        raise ValueError("--p-max-ee must be a non-negative float.")
    if trunc_q < 0:
        raise ValueError("--p-trunc-q must be a non-negative integer.")
    if max_len < 0:
        raise ValueError("--p-max-len must be a non-negative integer.")
    if min_fold_parent_over_abundance < 0:
        raise ValueError("--p-min-fold-parent-over-abundance must be a non-negative float.")
    if n_threads < 0:
        raise ValueError("--p-n-threads must be a non-negative integer (0 for all cores).")
    if n_reads_learn <= 0:
        raise ValueError("--p-n-reads-learn must be a positive integer.")

    # --- File Path Handling ---
    # Ensure output directories exist to prevent QIIME 2 errors
    for output_path in [table, representative_sequences, denoising_stats]:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "dada2", "denoise-pyro",
        "--i-demultiplexed-seqs", str(demultiplexed_seqs),
        "--o-table", str(table),
        "--o-representative-sequences", str(representative_sequences),
        "--o-denoising-stats", str(denoising_stats),
        "--p-trunc-len", str(trunc_len),
        "--p-trim-left", str(trim_left),
        "--p-max-ee", str(max_ee),
        "--p-trunc-q", str(trunc_q),
        "--p-max-len", str(max_len),
        "--p-chimera-method", chimera_method,
        "--p-min-fold-parent-over-abundance", str(min_fold_parent_over_abundance),
        "--p-n-threads", str(n_threads),
        "--p-n-reads-learn", str(n_reads_learn),
    ]

    if hashed_feature_ids:
        cmd.append("--p-hashed-feature-ids")
    else:
        cmd.append("--p-no-hashed-feature-ids")

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
        
        # --- Structured Result Return (Success) ---
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

    except FileNotFoundError:
        error_message = "QIIME 2 command not found. Please ensure 'qiime' is installed and in your system's PATH."
        logger.error(error_message)
        raise RuntimeError(error_message) from None

    except subprocess.CalledProcessError as e:
        # --- Error Handling and Structured Return (Failure) ---
        logger.error(f"QIIME DADA2 denoise-pyro failed with return code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME DADA2 denoise-pyro failed. Check stderr for details.",
            "return_code": e.returncode,
        }

if __name__ == '__main__':
    mcp.run()