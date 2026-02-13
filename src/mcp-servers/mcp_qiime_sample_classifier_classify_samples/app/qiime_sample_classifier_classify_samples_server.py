import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def qiime_sample_classifier_classify_samples(
    i_table: Path,
    i_sample_estimator: Path,
    o_prediction: Path,
    o_feature_importance: Optional[Path] = None,
    o_predictions: Optional[Path] = None,
    p_chunk_size: int = 2000,
    p_n_jobs: int = 1,
    p_random_state: Optional[int] = None,
    p_predict_direction: str = 'forward',
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Predicts target values for new samples using a trained QIIME 2 sample classifier.

    This tool uses a trained classifier to predict the values of a target metadata
    column for new samples based on their feature data.

    Args:
        i_table: Path to the feature table artifact containing features for prediction.
        i_sample_estimator: Path to the sample classifier artifact trained with fit-classifier or fit-regressor.
        o_prediction: Path to the output artifact for predicted target values.
        o_feature_importance: Optional path to the output artifact for feature importances.
        o_predictions: Optional path to the output artifact for predicted class probabilities (classifiers only).
        p_chunk_size: The number of samples to predict on at a time.
        p_n_jobs: Number of jobs to run in parallel.
        p_random_state: Seed used by the random number generator.
        p_predict_direction: Direction of feature importances ('forward' or 'reverse').
        verbose: Display verbose output to stdout.
        quiet: Display quiet output to stdout.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a list of output file paths.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table artifact not found at: {i_table}")
    if not i_sample_estimator.is_file():
        raise FileNotFoundError(f"Input sample estimator artifact not found at: {i_sample_estimator}")

    if p_predict_direction not in ['forward', 'reverse']:
        raise ValueError("p_predict_direction must be either 'forward' or 'reverse'.")

    if p_chunk_size <= 0:
        raise ValueError("p_chunk_size must be a positive integer.")
    
    if p_n_jobs <= 0:
        raise ValueError("p_n_jobs must be a positive integer.")

    if verbose and quiet:
        raise ValueError("Cannot enable both --verbose and --quiet flags simultaneously.")

    # --- Command Construction ---
    cmd = [
        "qiime", "sample-classifier", "classify-samples",
        "--i-table", str(i_table),
        "--i-sample-estimator", str(i_sample_estimator),
        "--o-prediction", str(o_prediction),
        "--p-chunk-size", str(p_chunk_size),
        "--p-n-jobs", str(p_n_jobs),
        "--p-predict-direction", p_predict_direction,
    ]

    output_files = [str(o_prediction)]

    if o_feature_importance:
        cmd.extend(["--o-feature-importance", str(o_feature_importance)])
        output_files.append(str(o_feature_importance))
    
    if o_predictions:
        cmd.extend(["--o-predictions", str(o_predictions)])
        output_files.append(str(o_predictions))

    if p_random_state is not None:
        cmd.extend(["--p-random-state", str(p_random_state)])

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
            check=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files
        }
    except FileNotFoundError:
        return {
            "command_executed": " ".join(cmd),
            "stdout": "",
            "stderr": "QIIME 2 command not found. Please ensure 'qiime' is installed and in your system's PATH.",
            "error": "Command not found",
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"Command failed with exit code {e.returncode}",
            "output_files": []
        }

if __name__ == '__main__':
    mcp.run()