from fastmcp import FastMCP
import subprocess
import logging
from pathlib import Path
from typing import List

# Initialize FastMCP and logger
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def inspect_metadata(
    paths: List[Path]
):
    """
    Inspect QIIME 2 metadata file(s) and report their validity and contents.

    This command is useful for previewing the contents of a metadata file,
    as well as for validating that the file is formatted correctly. If the file is
    not formatted correctly, this command will report the error that was
    encountered.

    Args:
        paths: A list of one or more paths to the metadata files to inspect.
    """
    # --- Input Validation ---
    if not paths:
        raise ValueError("At least one metadata file path must be provided in the 'paths' list.")

    cmd = ["qiime", "tools", "inspect-metadata"]
    
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(f"Input metadata file not found at the specified path: {p}")
        cmd.append(str(p))

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # --- Structured Result Return ---
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": []  # This tool does not generate output files
        }
    except FileNotFoundError:
        error_message = "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your system's PATH."
        logger.error(error_message)
        # Return a structured error if the tool itself is not found
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": error_message,
            "error": "ToolNotFound"
        }
    except subprocess.CalledProcessError as e:
        # Catch errors from the tool itself (e.g., invalid metadata format)
        logger.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}. See stderr for details."
        }

if __name__ == '__main__':
    mcp.run()