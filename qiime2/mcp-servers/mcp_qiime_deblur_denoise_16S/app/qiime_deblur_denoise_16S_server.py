import subprocess
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def qiime_deblur_denoise_16s(
    demultiplexed_seqs: Path,
    table: Path,
    representative_sequences: Path,
    stats: Path,
    trim_length: int,
    sample_stats: bool = False,
    mean_error_rate: float = 0.005,
    indel_prob: float = 0.01,
    indels: bool = True,
    min_reads: int = 10,
    min_size: int = 2,
    jobs_to_start: int = 1,
    hashed_feature_ids: bool = True,
    reference_seqs: Optional[Path] = None,
    left_trim_len: int = 0,
    verbose: bool = False,
):
    """
    Denoise 16S sequences using the QIIME 2 Deblur plugin.

    This method is intended for use with 16S studies that are generated on the
    Illumina platform. It denoises sequences, creates a feature table, and
    generates representative sequences.

    Parameters
    ----------
    demultiplexed_seqs : Path
        The demultiplexed sequences to be denoised (QIIME 2 artifact: SampleData[SequencesWithQuality]).
    table : Path
        The path to write the resulting feature table (QIIME 2 artifact: FeatureTable[Frequency]).
    representative_sequences : Path
        The path to write the resulting representative sequences (QIIME 2 artifact: FeatureData[Sequence]).
    stats : Path
        The path to write the deblurring statistics (QIIME 2 artifact: DeblurStats).
    trim_length : int
        Sequence trim length. Specify -1 to disable trimming.
    sample_stats : bool, optional
        Collect per-sample stats. This can be expensive for studies with many samples. Default is False.
    mean_error_rate : float, optional
        The mean per nucleotide error rate for depletion of singletons. Default is 0.005.
    indel_prob : float, optional
        The indel probability. Default is 0.01.
    indels : bool, optional
        Allow indels. Default is True.
    min_reads : int, optional
        Retain features that are present in at least this many samples. Default is 10.
    min_size : int, optional
        Retain features that have at least this many sequences. Default is 2.
    jobs_to_start : int, optional
        Number of jobs to start for parallel processing. Default is 1.
    hashed_feature_ids : bool, optional
        If true, hash the feature IDs for brevity. Default is True.
    reference_seqs : Optional[Path], optional
        Positive filtering database. Only features matching these sequences will be retained.
    left_trim_len : int, optional
        Sequence left trim length. Default is 0.
    verbose : bool, optional
        Display verbose output during command execution. Default is False.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output file paths.
    """
    # --- Input Validation ---
    if not demultiplexed_seqs.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_seqs}")
    if reference_seqs and not reference_seqs.is_file():
        raise FileNotFoundError(f"Reference sequences file not found: {reference_seqs}")

    if min_reads < 0:
        raise ValueError("min_reads must be a non-negative integer.")
    if min_size < 1:
        raise ValueError("min_size must be an integer greater than or equal to 1.")
    if jobs_to_start < 1:
        raise ValueError("jobs_to_start must be an integer greater than or equal to 1.")
    if left_trim_len < 0:
        raise ValueError("left_trim_len must be a non-negative integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "deblur", "denoise-16S",
        "--i-demultiplexed-seqs", str(demultiplexed_seqs),
        "--o-table", str(table),
        "--o-representative-sequences", str(representative_sequences),
        "--o-stats", str(stats),
        "--p-trim-length", str(trim_length),
        "--p-mean-error-rate", str(mean_error_rate),
        "--p-indel-prob", str(indel_prob),
        "--p-min-reads", str(min_reads),
        "--p-min-size", str(min_size),
        "--p-jobs-to-start", str(jobs_to_start),
        "--p-left-trim-len", str(left_trim_len),
    ]

    # Handle boolean flags which have a --p-no-<flag> variant in QIIME 2
    cmd.append("--p-sample-stats" if sample_stats else "--p-no-sample-stats")
    cmd.append("--p-indels" if indels else "--p-no-indels")
    cmd.append("--p-hashed-feature-ids" if hashed_feature_ids else "--p-no-hashed-feature-ids")

    # Handle optional file input
    if reference_seqs:
        cmd.extend(["--p-reference-seqs", str(reference_seqs)])

    # Handle verbosity
    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        output_files = {
            "table": str(table),
            "representative_sequences": str(representative_sequences),
            "stats": str(stats)
        }

        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files
        }

    except FileNotFoundError:
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and activated in your environment.",
            "error": "Command not found",
            "return_code": 127
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 deblur denoise-16S failed.",
            "return_code": e.returncode
        }


if __name__ == '__main__':
    mcp.run()