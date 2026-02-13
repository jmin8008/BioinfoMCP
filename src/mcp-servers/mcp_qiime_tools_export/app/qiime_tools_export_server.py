import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastmcp import FastMCP

# Initialize the MCP application
mcp = FastMCP()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def tools_export(
    input_path: Path,
    output_path: Path,
    output_format: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export a QIIME 2 Artifact (.qza) or Visualization (.qzv) to a directory.

    This tool extracts the data from a QIIME 2 Artifact or Visualization file
    and places it into a specified output directory.

    Args:
        input_path: Path to the QIIME 2 Artifact (.qza) or Visualization (.qzv)
                    to be exported.
        output_path: Path to the directory where the contents should be exported.
                     The directory will be created if it does not exist.
        output_format: The specific format to export the data to. This is only
                       necessary if the artifact supports multiple export formats.

    Returns:
        A dictionary containing the execution details, including the command,
        stdout, stderr, and the path to the output directory.
    """
    # --- Input Validation ---
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path must be a file, not a directory: {input_path}")

    # Ensure the parent directory for the output exists, as QIIME 2 will create the final directory.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime",
        "tools",
        "export",
        "--input-path",
        str(input_path),
        "--output-path",
        str(output_path),
    ]

    if output_format:
        if not output_format.strip():
            raise ValueError("output_format cannot be an empty string.")
        cmd.extend(["--output-format", output_format])

    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # --- Structured Result Return (Success) ---
        # The primary output is the directory itself. We can list the files within it.
        exported_files = [str(p) for p in output_path.rglob('*') if p.is_file()]

        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_directory": str(output_path),
            "exported_files": exported_files,
        }

    except FileNotFoundError:
        error_msg = "The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        logger.error(error_msg)
        # Re-raising is appropriate here as it's a system configuration issue.
        raise RuntimeError(error_msg) from None

    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        # Return a structured error dictionary for failed tool execution
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"Command failed with exit code {e.returncode}. See stderr for details.",
            "output_directory": None,
            "exported_files": [],
        }

if __name__ == '__main__':
    mcp.run()