import subprocess
from pathlib import Path
from typing import Optional, Literal
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def qiime_sample_classifier_regress_samples(
    table: Path,
    metadata_file: Path,
    metadata_column: str,
    sample_estimator: Path,
    feature_importance: Path,
    predictions: Path,
    test_size: float = 0.2,
    step: float = 0.05,
    cv: int = 5,
    random_state: Optional[int] = None,
    n_jobs: int = 1,
    n_estimators: int = 100,
    estimator: Literal[
        'RandomForestRegressor', 'ExtraTreesRegressor', 'GradientBoostingRegressor',
        'AdaBoostRegressor', 'KNeighborsRegressor', 'SVR', 'Ridge', 'Lasso', 'ElasticNet'
    ] = 'RandomForestRegressor',
    optimize_feature_selection: bool = False,
    parameter_tuning: bool = False,
    missing_samples: Literal['error', 'ignore'] = 'error',
    model_summary: Optional[Path] = None,
    accuracy_results: Optional[Path] = None,
    verbose: bool = False,
) -> dict:
    """
    Supervised regression analysis of samples using QIIME 2's sample-classifier.

    This tool trains and tests a regression model to predict a continuous metadata
    column from a feature table. It supports various estimators, cross-validation,
    and optional feature selection and hyperparameter tuning.
    """
    # --- Input Validation ---
    if not table.is_file():
        raise FileNotFoundError(f"Input table artifact not found at: {table}")
    if not metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata_file}")

    if not (0.0 < test_size < 1.0):
        raise ValueError("test_size must be between 0.0 and 1.0 (exclusive).")
    if not (0.0 < step < 1.0):
        raise ValueError("step must be between 0.0 and 1.0 (exclusive).")
    if cv < 1:
        raise ValueError("cv (cross-validation folds) must be at least 1.")
    if n_estimators < 1:
        raise ValueError("n_estimators must be at least 1.")

    # --- Command Construction ---
    cmd = [
        "qiime", "sample-classifier", "regress-samples",
        "--i-table", str(table),
        "--m-metadata-file", str(metadata_file),
        "--m-metadata-column", metadata_column,
        "--p-test-size", str(test_size),
        "--p-step", str(step),
        "--p-cv", str(cv),
        "--p-n-jobs", str(n_jobs),
        "--p-n-estimators", str(n_estimators),
        "--p-estimator", estimator,
        "--p-missing-samples", missing_samples,
        "--o-sample-estimator", str(sample_estimator),
        "--o-feature-importance", str(feature_importance),
        "--o-predictions", str(predictions),
    ]

    if random_state is not None:
        cmd.extend(["--p-random-state", str(random_state)])
    if optimize_feature_selection:
        cmd.append("--p-optimize-feature-selection")
    if parameter_tuning:
        cmd.append("--p-parameter-tuning")
    if model_summary:
        cmd.extend(["--o-model-summary", str(model_summary)])
    if accuracy_results:
        cmd.extend(["--o-accuracy-results", str(accuracy_results)])
    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        return {
            "command_executed": " ".join(cmd),
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and activated in your environment.",
            "output_files": {},
            "error": "QIIME 2 not found."
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": {},
            "error": f"QIIME 2 command failed with exit code {e.returncode}.",
            "return_code": e.returncode
        }

    # --- Output Handling ---
    output_files = {
        "sample_estimator": sample_estimator,
        "feature_importance": feature_importance,
        "predictions": predictions,
    }
    if model_summary:
        output_files["model_summary"] = model_summary
    if accuracy_results:
        output_files["accuracy_results"] = accuracy_results

    # Verify that output files were created
    for key, path in output_files.items():
        if not path.exists():
            return {
                "command_executed": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr + f"\nError: Expected output file '{key}' was not created at {path}.",
                "output_files": {},
                "error": "Output file generation failed."
            }

    # --- Structured Result Return ---
    return {
        "command_executed": " ".join(cmd),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {k: str(v) for k, v in output_files.items()}
    }

if __name__ == '__main__':
    mcp.run()