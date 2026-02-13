import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Union

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def qiime_deblur_denoise_other(
    demultiplexed_seqs: Path,
    reference_seqs: Path,
    trim_length: int,
    output_table: Path,
    output_representative_sequences: Path,
    output_stats: Path,
    sample_stats: bool = False,
    mean_error: float = 0.005,
    indel_prob: float = 0.01,
    indels: bool = True,
    min_reads: int = 10,
    min_size: int = 2,
    jobs_to_start: int = 1,
    hashed_feature_ids: bool = True,
) -> Dict[str, Union[str, List[str]]]:
    """
    Deblur single-end sequences using a user-specified positive filter.

    This method is suitable for denoising marker genes other than 16S rRNA,
    such as ITS or COI, where a custom positive filter (reference sequences)
    is required. It denoises sequences, creates a feature table, and generates
    representative sequences.

    Args:
        demultiplexed_seqs: Path to the QIIME 2 artifact (.qza) containing demultiplexed single-end sequence data.
        reference_seqs: Path to the QIIME 2 artifact (.qza) of reference sequences to use as a positive filter.
        trim_length: Sequences are trimmed to this length. A value of -1 indicates no trimming.
        output_table: Path to write the output feature table artifact (.qza).
        output_representative_sequences: Path to write the output representative sequences artifact (.qza).
        output_stats: Path to write the output denoising stats artifact (.qza).
        sample_stats: If True, gather statistics per sample.
        mean_error: The mean per-nucleotide error rate.
        indel_prob: The probability of an indel.
        indels: If True, allow indels in sequence alignment.
        min_reads: The minimum number of reads for a sequence to be considered.
        min_size: The minimum number of reads for a feature to be retained.
        jobs_to_start: Number of concurrent jobs to start.
        hashed_feature_ids: If True, hash the feature IDs for consistent naming.

    Returns:
        A dictionary containing the executed command, stdout, stderr, and a list of output file paths.
    """
    # --- Input Validation ---
    if not demultiplexed_seqs.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_seqs}")
    if not reference_seqs.is_file():
        raise FileNotFoundError(f"Reference sequences file not found: {reference_seqs}")

    if trim_length < -1:
        raise ValueError("trim_length must be -1 (no trimming) or a positive integer.")
    if not (0.0 <= mean_error <= 1.0):
        raise ValueError("mean_error must be between 0.0 and 1.0.")
    if not (0.0 <= indel_prob <= 1.0):
        raise ValueError("indel_prob must be between 0.0 and 1.0.")
    if min_reads < 1:
        raise ValueError("min_reads must be a positive integer.")
    if min_size < 1:
        raise ValueError("min_size must be a positive integer.")
    if jobs_to_start < 1:
        raise ValueError("jobs_to_start must be a positive integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "deblur", "denoise-other",
        "--i-demultiplexed-seqs", str(demultiplexed_seqs),
        "--i-reference-seqs", str(reference_seqs),
        "--p-trim-length", str(trim_length),
        "--p-mean-error", str(mean_error),
        "--p-indel-prob", str(indel_prob),
        "--p-min-reads", str(min_reads),
        "--p-min-size", str(min_size),
        "--p-jobs-to-start", str(jobs_to_start),
        "--o-table", str(output_table),
        "--o-representative-sequences", str(output_representative_sequences),
        "--o-stats", str(output_stats),
    ]

    # Handle boolean flags, which use --p-flag/--p-no-flag syntax in QIIME 2
    cmd.append("--p-sample-stats" if sample_stats else "--p-no-sample-stats")
    cmd.append("--p-indels" if indels else "--p-no-indels")
    cmd.append("--p-hashed-feature-ids" if hashed_feature_ids else "--p-no-hashed-feature-ids")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 deblur denoise-other failed with exit code {e.returncode}",
            "output_files": []
        }
    except FileNotFoundError:
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": "QIIME 2 command not found. Is it installed and in your PATH?",
            "error": "QIIME 2 not found.",
            "output_files": []
        }

    # --- Structured Result Return ---
    output_files = [
        str(output_table),
        str(output_representative_sequences),
        str(output_stats)
    ]

    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()