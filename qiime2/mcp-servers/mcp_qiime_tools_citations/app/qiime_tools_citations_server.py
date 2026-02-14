from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List
import logging

# Initialize the MCP application
mcp = FastMCP()

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def tools_citations(
    qza_files: List[Path],
    citations_format: str = "bibtex",
):
    """
    Display citations for one or more QIIME 2 results (.qza files).

    This tool extracts and displays citation information embedded within QIIME 2
    artifact files, which is crucial for ensuring reproducible science and giving
    credit to the developers of the methods used.

    Args:
        qza_files: A list of paths to one or more QIIME 2 artifact (.qza) files.
        citations_format: The desired citation format for the output.
                          Defaults to 'bibtex'.
    
    Returns:
        A dictionary containing the executed command, stdout (with citations),
        stderr, and a list of output files (which is always empty for this tool).
    """
    # --- Input Validation ---
    if not qza_files:
        raise ValueError("At least one input .qza file must be provided in the 'qza_files' list.")

    for qza_file in qza_files:
        if not qza_file.exists():
            raise FileNotFoundError(f"Input file not found: {qza_file}")
        if not qza_file.is_file():
            raise TypeError(f"Input path must be a file, but it is not: {qza_file}")
        if qza_file.suffix != ".qza":
            logging.warning(f"Input file '{qza_file}' does not have a .qza extension. QIIME 2 may not recognize it.")

    # --- Command Construction ---
    cmd = [
        "qiime",
        "tools",
        "citations",
        "--citations-format",
        citations_format,
    ]
    # Add all input file paths to the command
    cmd.extend([str(p) for p in qza_files])
    
    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        # This error occurs if the 'qiime' command is not found in the system's PATH
        return {
            "error": "QIIME 2 is not installed or not in the system's PATH.",
            "command_executed": command_executed,
        }
    except subprocess.CalledProcessError as e:
        # This error occurs if the command returns a non-zero exit code
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        return {
            "error": "QIIME 2 command failed.",
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    # This tool prints citation information to stdout and does not create output files.
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": []
    }

if __name__ == '__main__':
    mcp.run()