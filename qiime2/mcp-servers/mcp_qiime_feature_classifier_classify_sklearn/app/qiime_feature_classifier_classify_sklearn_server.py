import subprocess
from pathlib import Path
from typing import Optional, Union
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def feature_classifier_classify_sklearn(
    i_reads: Path,
    i_classifier: Path,
    o_classification: Path,
    p_reads_per_batch: str = "auto",
    p_n_jobs: int = 1,
    p_pre_dispatch: str = "2*n_jobs",
    p_confidence: float = 0.7,
    p_read_orientation: str = "auto",
    p_chunk_size: int = 262144,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Classify reads by taxon using a fitted scikit-learn classifier.

    This tool uses a pre-trained scikit-learn classifier to assign taxonomy to
    feature sequences (reads). It's a primary step in taxonomic analysis within QIIME 2.

    Args:
        i_reads (Path): The feature data (sequences) to be classified. (QIIME 2 Artifact)
        i_classifier (Path): The taxonomic classifier for classifying the reads. (QIIME 2 Artifact)
        o_classification (Path): The path to write the resulting taxonomic assignments. (QIIME 2 Artifact)
        p_reads_per_batch (str): Number of reads to process in each batch. If "auto", it's autoscaled.
                                 Can be an integer value provided as a string. Defaults to "auto".
        p_n_jobs (int): Number of jobs to run in parallel. Defaults to 1.
        p_pre_dispatch (str): The number of batches of tasks to be pre-dispatched.
                              Can be "all" or an expression like "3*n_jobs". Defaults to "2*n_jobs".
        p_confidence (float): Confidence threshold for limiting taxonomic depth. Set to -1.0 to disable
                              confidence calculation, or 0.0 to calculate but not apply filtering.
                              Must be between 0.0 and 1.0, or -1.0. Defaults to 0.7.
        p_read_orientation (str): Direction of reads with respect to reference sequences.
                                  Choices are 'same', 'reverse-complement', 'auto'. Defaults to 'auto'.
        p_chunk_size (int): Number of samples to process at a time in each batch. Must be >= 1.
                            Defaults to 262144.
        verbose (bool): Display verbose output. Defaults to False.
        quiet (bool): Suppress all output except errors. Defaults to False.

    Returns:
        dict: A dictionary containing the execution command, stdout, stderr, and a
              mapping of output file keys to their paths.
    """
    # --- Input Validation ---
    if not i_reads.is_file():
        raise FileNotFoundError(f"Input reads artifact not found at: {i_reads}")
    if not i_classifier.is_file():
        raise FileNotFoundError(f"Input classifier artifact not found at: {i_classifier}")

    if o_classification.parent and not o_classification.parent.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {o_classification.parent}")

    if p_reads_per_batch != "auto":
        try:
            reads_val = int(p_reads_per_batch)
            if reads_val <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(f"p_reads_per_batch must be 'auto' or a positive integer string, not '{p_reads_per_batch}'.")

    if p_n_jobs < 1:
        raise ValueError(f"p_n_jobs must be a positive integer, not {p_n_jobs}.")

    if not (p_confidence == -1.0 or 0.0 <= p_confidence <= 1.0):
        raise ValueError(f"p_confidence must be -1.0 or between 0.0 and 1.0, not {p_confidence}.")

    allowed_orientations = ['same', 'reverse-complement', 'auto']
    if p_read_orientation not in allowed_orientations:
        raise ValueError(f"p_read_orientation must be one of {allowed_orientations}, not '{p_read_orientation}'.")

    if p_chunk_size < 1:
        raise ValueError(f"p_chunk_size must be a positive integer, not {p_chunk_size}.")

    if verbose and quiet:
        raise ValueError("Cannot set both --verbose and --quiet flags simultaneously.")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-classifier", "classify-sklearn",
        "--i-reads", str(i_reads),
        "--i-classifier", str(i_classifier),
        "--o-classification", str(o_classification),
        "--p-reads-per-batch", str(p_reads_per_batch),
        "--p-n-jobs", str(p_n_jobs),
        "--p-pre-dispatch", p_pre_dispatch,
        "--p-confidence", str(p_confidence),
        "--p-read-orientation", p_read_orientation,
        "--p-chunk-size", str(p_chunk_size),
    ]

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        return {
            "error": "qiime command not found. Please ensure QIIME 2 is installed and in your PATH.",
            "command_executed": " ".join(cmd),
            "stdout": "",
            "stderr": "",
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "classification": str(o_classification)
        }
    }

if __name__ == '__main__':
    mcp.run()