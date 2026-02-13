import subprocess
import logging
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

# Initialize FastMCP and logging
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def qiime_composition_add_pseudocount(
    i_table: Path,
    o_composition_table: Path,
    pseudocount: float = 1.0,
    verbose: bool = False,
):
    """
    Increment all values in a feature table by a pseudocount.

    This tool is a wrapper for the 'qiime composition add-pseudocount' command.
    It adds a specified pseudocount to all feature counts in a table, which is
    a common step before log-ratio transformations to handle zeros.

    Parameters
    ----------
    i_table : Path
        The input feature table artifact (FeatureTable[Frequency]). This is a required parameter.
    o_composition_table : Path
        The path for the output composition table artifact (FeatureTable[Composition]). This is a required parameter.
    pseudocount : float, optional
        The value to add to all counts in the table. Defaults to 1.0.
    verbose : bool, optional
        Display verbose output during command execution. Defaults to False.

    Returns
    -------
    dict
        A dictionary containing the execution details and output file paths.
        Keys include 'command_executed', 'stdout', 'stderr', and 'output_files'.
    
    Raises
    ------
    FileNotFoundError
        If the input table does not exist.
    ValueError
        If the input path is not a file or if the pseudocount is not a positive number.
    """
    # 1. Input Validation
    if not i_table.exists():
        raise FileNotFoundError(f"Input table not found at: {i_table}")
    if not i_table.is_file():
        raise ValueError(f"Input path must be a file, but got a directory: {i_table}")

    if pseudocount <= 0:
        # While QIIME2 might allow non-positive values, it's standard practice
        # for pseudocounts to be positive. This is a sensible validation.
        raise ValueError("The pseudocount must be a positive number.")

    # Ensure the output directory exists
    output_dir = o_composition_table.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Command Construction
    cmd = [
        "qiime", "composition", "add-pseudocount",
        "--i-table", str(i_table),
        "--o-composition-table", str(o_composition_table),
        "--p-pseudocount", str(pseudocount),
    ]

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # 3. Subprocess Execution & 4. Error Handling
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        # This catches the case where 'qiime' is not in the system's PATH
        error_message = "Error: 'qiime' command not found. Make sure QIIME 2 is installed and activated in your environment."
        logging.error(error_message)
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": error_message,
            "output_files": {},
            "error": "QIIME 2 not found"
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": {},
            "error": f"Command failed with exit code {e.returncode}"
        }

    # 5. Structured Result Return
    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "composition_table": str(o_composition_table)
        }
    }

if __name__ == '__main__':
    mcp.run()