import subprocess
import logging
from pathlib import Path
from typing import Optional, List

from fastmcp import FastMCP

# Initialize the MCP application
mcp = FastMCP()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def demux_summarize(
    i_data: Path,
    o_visualization: Path,
    p_n: int = 10000,
    m_metadata_file: Optional[List[Path]] = None,
    m_metadata_column: Optional[str] = None,
    p_where: Optional[str] = None,
    p_no_where: bool = False,
    verbose: bool = False,
):
    """
    Summarize counts per sample and generate interactive positional quality plots.

    This tool provides a summary of demultiplexed sequence data, including
    interactive quality plots for a subset of samples. It wraps the
    'qiime demux summarize' command.

    Args:
        i_data (Path): The demultiplexed sequences to be summarized (QIIME 2 Artifact).
        o_visualization (Path): The path to write the output visualization file (QIIME 2 Visualization).
        p_n (int): The number of samples to randomly select for quality score plots.
                   If n is larger than the number of samples, all samples will be used.
                   Defaults to 10000.
        m_metadata_file (Optional[List[Path]]): A list of sample metadata files to use in the visualization.
        m_metadata_column (Optional[str]): A column from the metadata file to use for sample ordering.
                                           Requires m_metadata_file to be provided.
        p_where (Optional[str]): A QIIME 2 metadata query to subset the data.
                                 Cannot be used with p_no_where.
        p_no_where (bool): If True, do not subset the data. Cannot be used with p_where.
                           Defaults to False.
        verbose (bool): If True, display verbose command-line output. Defaults to False.

    Returns:
        dict: A dictionary containing the command executed, stdout, stderr,
              and a dictionary of output file paths.
    """
    # --- Input Validation ---
    if not i_data.is_file():
        raise FileNotFoundError(f"Input data file does not exist: {i_data}")

    if o_visualization.exists():
        logger.warning(f"Output file {o_visualization} already exists and will be overwritten.")
    
    # Ensure the parent directory for the output file exists
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    if p_n <= 0:
        raise ValueError("--p-n must be a positive integer.")

    if m_metadata_file:
        for mf in m_metadata_file:
            if not mf.is_file():
                raise FileNotFoundError(f"Metadata file does not exist: {mf}")

    if m_metadata_column and not m_metadata_file:
        raise ValueError("--m-metadata-column requires --m-metadata-file to be provided.")

    if p_where and p_no_where:
        raise ValueError("Cannot use both --p-where and --p-no-where simultaneously.")

    # --- Command Construction ---
    cmd = [
        "qiime", "demux", "summarize",
        "--i-data", str(i_data),
        "--o-visualization", str(o_visualization),
        "--p-n", str(p_n),
    ]

    if m_metadata_file:
        for mf in m_metadata_file:
            cmd.extend(["--m-metadata-file", str(mf)])

    if m_metadata_column:
        cmd.extend(["--m-metadata-column", m_metadata_column])

    if p_where:
        cmd.extend(["--p-where", p_where])

    if p_no_where:
        cmd.append("--p-no-where")

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        stdout = result.stdout
        stderr = result.stderr
        logger.info("qiime demux summarize completed successfully.")

    except FileNotFoundError:
        # This error occurs if 'qiime' is not in the system's PATH
        raise RuntimeError(
            "The 'qiime' command was not found. "
            "Please ensure QIIME 2 is installed and the environment is activated."
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing qiime demux summarize: {e.stderr}")
        # Re-raise with a more informative message for the user
        raise RuntimeError(
            f"QIIME 2 command failed with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        ) from e

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "visualization": str(o_visualization)
        }
    }

if __name__ == '__main__':
    mcp.run()