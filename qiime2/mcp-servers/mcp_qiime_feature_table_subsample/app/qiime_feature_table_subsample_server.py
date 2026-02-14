from fastmcp import FastMCP
from pathlib import Path
import subprocess
import logging
from typing import Dict, List

# Initialize MCP and logging
mcp = FastMCP()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@mcp.tool()
def feature_table_subsample(
    i_table: Path,
    p_fraction: float,
    o_subsampled_table: Path,
    p_with_replacement: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict:
    """
    Subsample features from a feature table.

    This QIIME 2 tool subsamples features from a feature table, either with or
    without replacement. It is useful for reducing the complexity of a feature
    table for downstream analyses or for performing rarefaction-like analyses
    at the feature level.

    Args:
        i_table: Path to the input feature table artifact (`.qza`).
        p_fraction: The fraction of features to be retained (value between 0.0 and 1.0).
        o_subsampled_table: Path to the output subsampled feature table artifact (`.qza`).
        p_with_replacement: Subsample with replacement. Defaults to False.
        verbose: Display verbose output during command execution.
        quiet: Silence output if execution is successful.

    Returns:
        A dictionary containing the execution details and output file path.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table not found at: {i_table}")

    if not (0.0 <= p_fraction <= 1.0):
        raise ValueError("p_fraction must be between 0.0 and 1.0, inclusive.")

    if o_subsampled_table.is_dir():
        raise IsADirectoryError(f"Output path {o_subsampled_table} must be a file, not a directory.")
    
    # Ensure the output directory exists
    o_subsampled_table.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "subsample",
        "--i-table", str(i_table),
        "--p-fraction", str(p_fraction),
        "--o-subsampled-table", str(o_subsampled_table),
    ]

    if p_with_replacement:
        cmd.append("--p-with-replacement")
    
    if verbose:
        cmd.append("--verbose")
    
    if quiet:
        cmd.append("--quiet")

    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        
        # Verify that the output file was created
        if not o_subsampled_table.is_file():
             raise FileNotFoundError(
                f"Expected output file was not created: {o_subsampled_table}\n"
                f"QIIME2 stdout:\n{stdout}\n"
                f"QIIME2 stderr:\n{stderr}"
            )

        output_files: List[str] = [str(o_subsampled_table)]

    except FileNotFoundError:
        error_msg = "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your system's PATH."
        logging.error(error_msg)
        # This error is critical and should be raised to the MCP framework
        raise RuntimeError(error_msg) from None
        
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        # Return a structured error dictionary as the process failed
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "output_files": []
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()