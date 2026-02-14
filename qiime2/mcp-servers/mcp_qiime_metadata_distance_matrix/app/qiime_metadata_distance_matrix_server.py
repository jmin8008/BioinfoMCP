import subprocess
import logging
from pathlib import Path
from typing import List
import tempfile
from fastmcp import FastMCP

# Initialize MCP and logging
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def metadata_distance_matrix(
    m_metadata_file: Path,
    m_metadata_column: List[str],
    o_distance_matrix: Path,
):
    """
    Compute a distance matrix from a metadata file.

    This action supports calculating distances between samples using metadata
    columns of various types. This is a useful way to explore the metadata in
    an analysis. For example, a distance matrix based on geographic location
    could be compared to a beta diversity distance matrix to see if samples
    that are closer to one another in space are also more similar to one
    another in composition.
    """
    # --- Input Validation ---
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Input metadata file not found: {m_metadata_file}")

    if not m_metadata_column:
        raise ValueError("--m-metadata-column cannot be empty. Please provide at least one column name.")

    # Ensure output directory exists
    o_distance_matrix.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "metadata", "distance-matrix",
        "--m-metadata-file", str(m_metadata_file),
        "--o-distance-matrix", str(o_distance_matrix),
    ]
    # Add each metadata column to the command
    for column in m_metadata_column:
        cmd.extend(["--m-metadata-column", column])

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        stdout = result.stdout
        stderr = result.stderr
        logging.info("QIIME 2 command executed successfully.")

    except FileNotFoundError:
        # This handles the case where 'qiime' is not in the system's PATH
        error_message = "Error: 'qiime' command not found. Make sure QIIME 2 is installed and accessible in your system's PATH."
        logging.error(error_message)
        # In a real server, you might raise a specific exception here
        # For this structure, we return a detailed error dictionary
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": error_message,
            "return_code": 1,
            "error": "QIIME 2 executable not found."
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command execution failed."
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "distance_matrix": str(o_distance_matrix)
        }
    }

if __name__ == '__main__':
    mcp.run()