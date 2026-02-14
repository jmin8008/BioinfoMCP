from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

mcp = FastMCP()

@mcp.tool()
def identify_contaminants(
    i_table: Path,
    i_metadata: Path,
    p_method: str,
    o_feature_scores: Path,
    o_is_contaminant_table: Path,
    p_freq_concentration_column: Optional[str] = None,
    p_prev_control_column: Optional[str] = None,
    p_prev_control_indicator: Optional[str] = None,
    p_threshold: float = 0.1,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """
    Identifies contaminant features using the decontam R package within QIIME 2.

    This method supports two main approaches: 'prevalence' and 'frequency'.
    The 'prevalence' method identifies contaminants based on their prevalence in
    true vs. control samples. The 'frequency' method identifies contaminants
    based on their frequency relative to input DNA concentration.

    Args:
        i_table: Path to the feature table artifact (FeatureTable[Frequency]).
        i_metadata: Path to the sample metadata file.
        p_method: The method for contaminant identification ('prevalence' or 'frequency').
        o_feature_scores: Path to save the output feature scores artifact (DecontamScore).
        o_is_contaminant_table: Path to save the output boolean feature table artifact (FeatureTable[Boolean]).
        p_freq_concentration_column: Metadata column with DNA concentrations (required for 'frequency' method).
        p_prev_control_column: Metadata column indicating control samples.
        p_prev_control_indicator: Value in the control column that identifies control samples (required for 'prevalence' method).
        p_threshold: Probability threshold for classifying features as contaminants.
        verbose: Display verbose output.
        quiet: Suppress standard output.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and output file paths.
    """
    # --- Input Validation ---
    if not i_table.exists():
        raise FileNotFoundError(f"Input table not found at: {i_table}")
    if not i_metadata.exists():
        raise FileNotFoundError(f"Input metadata not found at: {i_metadata}")

    valid_methods = ['prevalence', 'frequency']
    if p_method not in valid_methods:
        raise ValueError(f"p_method must be one of {valid_methods}, but got '{p_method}'.")

    if p_method == 'frequency' and p_freq_concentration_column is None:
        raise ValueError("p_freq_concentration_column is required when p_method is 'frequency'.")

    if p_method == 'prevalence' and p_prev_control_indicator is None:
        raise ValueError("p_prev_control_indicator is required when p_method is 'prevalence'.")

    if not (0.0 <= p_threshold <= 1.0):
        raise ValueError(f"p_threshold must be between 0.0 and 1.0, but got {p_threshold}.")

    if verbose and quiet:
        raise ValueError("Cannot set both 'verbose' and 'quiet' to True.")

    # --- Command Construction ---
    cmd = [
        "qiime", "decontam", "identify-contaminants",
        "--i-table", str(i_table),
        "--i-metadata", str(i_metadata),
        "--p-method", p_method,
        "--p-threshold", str(p_threshold),
        "--o-feature-scores", str(o_feature_scores),
        "--o-is-contaminant-table", str(o_is_contaminant_table),
    ]

    if p_freq_concentration_column:
        cmd.extend(["--p-freq-concentration-column", p_freq_concentration_column])
    if p_prev_control_column:
        cmd.extend(["--p-prev-control-column", p_prev_control_column])
    if p_prev_control_indicator:
        cmd.extend(["--p-prev-control-indicator", p_prev_control_indicator])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "feature_scores": str(o_feature_scores),
                "is_contaminant_table": str(o_is_contaminant_table)
            }
        }
    except FileNotFoundError:
        # This handles the case where 'qiime' is not in the system's PATH
        raise RuntimeError("QIIME 2 command 'qiime' not found. Please ensure QIIME 2 is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        # This handles errors from the QIIME 2 tool itself
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 decontam command failed.",
            "return_code": e.returncode
        }

if __name__ == '__main__':
    mcp.run()