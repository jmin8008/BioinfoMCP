from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List, Dict, Union
import logging

# It's a good practice to set up a logger for server-side applications.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def cast_metadata(
    metadata_files: List[Path],
    cast: List[str],
    output_file: Path,
    ignore_missing_samples: bool = False,
) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Casts metadata from one type to another using QIIME 2's 'tools cast-metadata'.

    This tool allows casting columns in metadata files to different types
    (e.g., from categorical to numeric). It is an advanced command that should
    be used with care.

    Args:
        metadata_files: A list of one or more input metadata files (e.g., .tsv) to be cast.
        cast: A list of mappings of a column name to the type it should be cast to.
              The format for each string must be 'COLUMN:TYPE'. This option is required
              and can be repeated.
        output_file: The path to the file where the casted metadata should be written.
        ignore_missing_samples: If True, ignore samples that are present in the
                                metadata but not in other data (e.g., a feature table).
                                Corresponds to the --ignore-missing-samples flag.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary mapping output names to their file paths.
    
    Raises:
        ValueError: If required list arguments `metadata_files` or `cast` are empty.
        FileNotFoundError: If any of the input metadata files do not exist.
        RuntimeError: If the 'qiime' command is not found in the system's PATH.
        subprocess.CalledProcessError: If the QIIME 2 command fails for any reason.
    """
    # 1. Input Validation
    if not metadata_files:
        raise ValueError("At least one metadata file must be provided via the 'metadata_files' parameter.")
    if not cast:
        raise ValueError("At least one cast instruction must be provided via the 'cast' parameter.")

    for f in metadata_files:
        if not f.exists():
            raise FileNotFoundError(f"Input metadata file not found: {f}")
    
    for c in cast:
        if ':' not in c or len(c.split(':')) != 2:
            raise ValueError(f"Invalid format for --cast argument: '{c}'. Expected 'COLUMN:TYPE'.")

    # 2. File Path Handling: Ensure the output directory exists
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory for {output_file}: {e}")
        raise

    # 3. Command Construction
    cmd = ["qiime", "tools", "cast-metadata"]
    
    # Add options
    for c in cast:
        cmd.extend(["--cast", c])
    
    cmd.extend(["--output-file", str(output_file)])
    
    if ignore_missing_samples:
        cmd.append("--ignore-missing-samples")
    
    # Add positional arguments (inputs) at the end
    cmd.extend([str(f) for f in metadata_files])

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # 4. Subprocess Execution and Error Handling
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        # This handles the case where 'qiime' is not in the system's PATH
        error_msg = "QIIME 2 command-line tool ('qiime') not found. Please ensure QIIME 2 is installed and its environment is activated."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except subprocess.CalledProcessError as e:
        # Capture and log detailed error information from the failed process
        error_message = (
            f"QIIME 2 command failed with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr: {e.stderr.strip()}\n"
            f"Stdout: {e.stdout.strip()}"
        )
        logger.error(error_message)
        # Re-raise the exception to let the MCP framework handle the failure response
        raise e

    # 5. Structured Result Return
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "casted_metadata": str(output_file)
        }
    }

if __name__ == '__main__':
    mcp.run()