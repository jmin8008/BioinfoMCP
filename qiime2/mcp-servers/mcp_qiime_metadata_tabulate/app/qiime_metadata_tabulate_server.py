from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List
import logging

mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def metadata_tabulate(
    m_input_file: List[Path],
    o_visualization: Path,
):
    """
    Generate a simple tabular view of metadata files or artifacts.

    This tool creates a QIIME 2 visualization (.qzv) that provides a searchable
    and sortable table from one or more metadata files (.tsv) or artifacts (.qza).
    The output visualization supports sorting and searching.
    """
    # --- Input Validation ---
    if not m_input_file:
        raise ValueError("Parameter 'm_input_file' cannot be empty. Please provide at least one input file.")

    for file_path in m_input_file:
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    # --- File Path Handling ---
    if o_visualization.suffix != ".qzv":
        logging.warning(f"Output file '{o_visualization}' does not end with .qzv. QIIME 2 visualizations typically use this extension.")
    
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "metadata", "tabulate",
        "--o-visualization", str(o_visualization)
    ]
    
    # Add all input files. The flag --m-input-file must be repeated for each file.
    for file_path in m_input_file:
        cmd.extend(["--m-input-file", str(file_path)])

    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing qiime metadata tabulate: {e.stderr}")
        # Return structured error info
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed."
        }
    except FileNotFoundError:
        error_msg = "The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        logging.error(error_msg)
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": error_msg,
            "return_code": 127,
            "error": "Command not found."
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": [str(o_visualization)]
    }

if __name__ == '__main__':
    mcp.run()