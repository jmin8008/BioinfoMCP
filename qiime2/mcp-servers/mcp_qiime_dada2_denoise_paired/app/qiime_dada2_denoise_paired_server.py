from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, List

mcp = FastMCP()

@mcp.tool()
def qiime_dada2_denoise_paired(
    demultiplexed_seqs: Path,
    table: Path,
    representative_sequences: Path,
    denoising_stats: Path,
    trunc_len_f: int = 0,
    trunc_len_r: int = 0,
    trim_left_f: int = 0,
    trim_left_r: int = 0,
    max_ee_f: float = 2.0,
    max_ee_r: float = 2.0,
    trunc_q: int = 2,
    min_overlap: int = 12,
    pooling_method: str = "independent",
    chimera_method: str = "consensus",
    min_fold_parent_over_abundance: float = 1.0,
    allow_one_off: bool = False,
    n_threads: int = 1,
    n_reads_learn: int = 1000000,
    hashed_feature_ids: bool = True,
    read_orientation_map: Optional[Path] = None
):
    """
    Denoises paired-end sequences, dereplicates them, and filters chimeras using DADA2.

    This method is a wrapper for the DADA2 R package's dada function, followed by
    mergePairs, removeBimeraDenovo, and makeSequenceTable. This method is intended
    for use with paired-end sequence data.

    Args:
        demultiplexed_seqs (Path): The paired-end demultiplexed sequences to be denoised. (QIIME 2 Artifact)
        table (Path): The resulting feature table. (QIIME 2 Artifact Path)
        representative_sequences (Path): The resulting representative sequences. (QIIME 2 Artifact Path)
        denoising_stats (Path): The resulting denoising statistics. (QIIME 2 Artifact Path)
        trunc_len_f (int): Position at which forward reads should be truncated. Reads shorter than this are discarded.
        trunc_len_r (int): Position at which reverse reads should be truncated. Reads shorter than this are discarded.
        trim_left_f (int): Number of bases to trim from the beginning of forward reads.
        trim_left_r (int): Number of bases to trim from the beginning of reverse reads.
        max_ee_f (float): Forward reads with number of expected errors higher than this value will be discarded.
        max_ee_r (float): Reverse reads with number of expected errors higher than this value will be discarded.
        trunc_q (int): Reads are truncated at the first instance of a quality score less than or equal to this value.
        min_overlap (int): The minimum number of overlapping bases required to merge the forward and reverse reads.
        pooling_method (str): The method used to pool samples for error rate learning. Choices: 'independent', 'pseudo'.
        chimera_method (str): The method used to remove chimeras. Choices: 'none', 'pooled', 'consensus'.
        min_fold_parent_over_abundance (float): The minimum fold-parent-over-abundance for consensus chimera detection.
        allow_one_off (bool): If True, the DADA2 allowOneOff parameter is enabled.
        n_threads (int): The number of threads to use for processing. 0 uses all available cores.
        n_reads_learn (int): The number of reads to use for learning the error rates.
        hashed_feature_ids (bool): If true, the feature IDs in the resulting table will be MD5 sums of the sequences.
        read_orientation_map (Optional[Path]): Map of samples to forward and reverse read orientations. (QIIME 2 Artifact)

    Returns:
        dict: A dictionary containing the command executed, stdout, stderr, and a list of output file paths.
    """
    # --- Input Validation ---
    if not demultiplexed_seqs.is_file():
        raise FileNotFoundError(f"Input file not found: {demultiplexed_seqs}")

    if read_orientation_map and not read_orientation_map.is_file():
        raise FileNotFoundError(f"Optional input file not found: {read_orientation_map}")

    # Validate choice parameters
    valid_pooling_methods = ["independent", "pseudo"]
    if pooling_method not in valid_pooling_methods:
        raise ValueError(f"Invalid pooling_method '{pooling_method}'. Must be one of {valid_pooling_methods}")

    valid_chimera_methods = ["none", "pooled", "consensus"]
    if chimera_method not in valid_chimera_methods:
        raise ValueError(f"Invalid chimera_method '{chimera_method}'. Must be one of {valid_chimera_methods}")

    # Validate numeric parameters
    if trunc_len_f < 0:
        raise ValueError("trunc_len_f must be a non-negative integer.")
    if trunc_len_r < 0:
        raise ValueError("trunc_len_r must be a non-negative integer.")
    if trim_left_f < 0:
        raise ValueError("trim_left_f must be a non-negative integer.")
    if trim_left_r < 0:
        raise ValueError("trim_left_r must be a non-negative integer.")
    if n_threads < 0:
        raise ValueError("n_threads must be a non-negative integer.")
    if n_reads_learn < 1:
        raise ValueError("n_reads_learn must be a positive integer.")
    if min_overlap < 0:
        raise ValueError("min_overlap must be a non-negative integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "dada2", "denoise-paired",
        "--i-demultiplexed-seqs", str(demultiplexed_seqs),
        "--o-table", str(table),
        "--o-representative-sequences", str(representative_sequences),
        "--o-denoising-stats", str(denoising_stats),
        "--p-trunc-len-f", str(trunc_len_f),
        "--p-trunc-len-r", str(trunc_len_r),
        "--p-trim-left-f", str(trim_left_f),
        "--p-trim-left-r", str(trim_left_r),
        "--p-max-ee-f", str(max_ee_f),
        "--p-max-ee-r", str(max_ee_r),
        "--p-trunc-q", str(trunc_q),
        "--p-min-overlap", str(min_overlap),
        "--p-pooling-method", pooling_method,
        "--p-chimera-method", chimera_method,
        "--p-min-fold-parent-over-abundance", str(min_fold_parent_over_abundance),
        "--p-n-threads", str(n_threads),
        "--p-n-reads-learn", str(n_reads_learn),
    ]

    if allow_one_off:
        cmd.append("--p-allow-one-off")
    
    # The --p-no-hashed-feature-ids flag is used to disable it. The default is True.
    if not hashed_feature_ids:
        cmd.append("--p-no-hashed-feature-ids")

    if read_orientation_map:
        cmd.extend(["--i-read-orientation-map", str(read_orientation_map)])
        
    cmd.append("--verbose")

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.CalledProcessError as e:
        # In case of an error, return the captured output for debugging
        return {
            "command_executed": " ".join(map(str, cmd)),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "output_files": []
        }

    # --- Structured Result Return ---
    output_files = [
        str(table),
        str(representative_sequences),
        str(denoising_stats)
    ]

    return {
        "command_executed": " ".join(map(str, cmd)),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files
    }

if __name__ == '__main__':
    mcp.run()