import subprocess
import re
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def qiime_feature_classifier_fit_classifier_naive_bayes(
    reference_reads: Path,
    reference_taxonomy: Path,
    classifier: Path,
    classify_alpha: float = 0.001,
    feat_ext_ngram_range: str = '[7, 7]',
    feat_ext_word_length: int = 84,
    chunk_size: int = 20000,
    verbose: bool = False,
):
    """
    Train a Naive Bayes classifier for feature classification using QIIME 2.

    This tool wraps the 'qiime feature-classifier fit-classifier-naive-bayes'
    command. It trains a Naive Bayes classifier from reference sequences and
    their corresponding taxonomic assignments.

    Args:
        reference_reads: Path to the artifact containing sequences from which to
                         train the classifier. (QIIME 2 type: FeatureData[Sequence])
                         Corresponds to --i-reference-reads.
        reference_taxonomy: Path to the artifact containing taxonomy labels for
                            the training sequences. (QIIME 2 type: FeatureData[Taxonomy])
                            Corresponds to --i-reference-taxonomy.
        classifier: Path to write the resulting classifier artifact.
                    Corresponds to --o-classifier.
        classify_alpha: The lowest possible frequency for any feature; used for
                        smoothing. Corresponds to --p-classify--alpha.
        feat_ext_ngram_range: The range of n-gram lengths to include in the k-mer
                              feature vector. Must be a string representing a list
                              of one or two integers, e.g., '[7, 7]' or '[6, 8]'.
                              Corresponds to --p-feat-ext--ngram-range.
        feat_ext_word_length: The k-mer length to be used for feature extraction.
                              Corresponds to --p-feat-ext--word-length.
        chunk_size: Number of sequences to process at a time. This parameter is
                    used to tune memory usage. Corresponds to --p-chunk-size.
        verbose: Display verbose output during command execution.

    Returns:
        A dictionary containing the execution details, including the command,
        stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not reference_reads.is_file():
        raise FileNotFoundError(f"Input reference reads artifact not found: {reference_reads}")
    if not reference_taxonomy.is_file():
        raise FileNotFoundError(f"Input reference taxonomy artifact not found: {reference_taxonomy}")
    
    output_dir = classifier.parent
    if not output_dir.is_dir():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise NotADirectoryError(f"Output directory could not be created: {output_dir}. Error: {e}")

    if classify_alpha <= 0:
        raise ValueError("--p-classify--alpha must be a positive number.")
    
    # Validate ngram_range format, e.g., '[7, 7]' or '[6, 8]'
    if not re.match(r'^\[\s*\d+\s*(,\s*\d+\s*)?\]$', feat_ext_ngram_range):
        raise ValueError(
            "--p-feat-ext--ngram-range must be a string representing a list of one or two integers, "
            f"e.g., '[7, 7]' or '[6, 8]'. Received: '{feat_ext_ngram_range}'"
        )

    if feat_ext_word_length <= 0:
        raise ValueError("--p-feat-ext--word-length must be a positive integer.")
    
    if chunk_size <= 0:
        raise ValueError("--p-chunk-size must be a positive integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-classifier", "fit-classifier-naive-bayes",
        "--i-reference-reads", str(reference_reads),
        "--i-reference-taxonomy", str(reference_taxonomy),
        "--o-classifier", str(classifier),
        "--p-classify--alpha", str(classify_alpha),
        "--p-feat-ext--ngram-range", feat_ext_ngram_range,
        "--p-feat-ext--word-length", str(feat_ext_word_length),
        "--p-chunk-size", str(chunk_size),
    ]
    if verbose:
        cmd.append("--verbose")

    command_executed = " ".join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(classifier)]
        }
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and accessible in your system's PATH.",
            "error": "Command not found",
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "output_files": []
        }

if __name__ == '__main__':
    mcp.run()