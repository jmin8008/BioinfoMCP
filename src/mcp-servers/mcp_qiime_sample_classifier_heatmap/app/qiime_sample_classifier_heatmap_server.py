import subprocess
import logging
from pathlib import Path
from typing import Optional, List

from fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP
mcp = FastMCP()

@mcp.tool()
def sample_classifier_heatmap(
    i_table: Path,
    i_importance: Path,
    o_heatmap: Path,
    o_filtered_table: Optional[Path] = None,
    p_feature_count: int = 100,
    m_sample_metadata_file: Optional[Path] = None,
    m_sample_metadata_column: Optional[str] = None,
    p_group_samples: bool = False,
    p_normalize: bool = True,
    verbose: bool = False,
) -> dict:
    """
    Generate a heatmap of the top n most important features from a QIIME2 sample classifier analysis.

    This tool visualizes the abundances of the most important features across samples,
    optionally ordering and annotating them based on sample metadata.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {i_table}")
    if not i_importance.is_file():
        raise FileNotFoundError(f"Input importance artifact not found at: {i_importance}")
    if m_sample_metadata_file and not m_sample_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {m_sample_metadata_file}")
    if p_feature_count < 0:
        raise ValueError("--p-feature-count must be a non-negative integer.")
    if p_group_samples and not m_sample_metadata_column:
        raise ValueError("--m-sample-metadata-column must be provided when --p-group-samples is True.")
    if m_sample_metadata_column and not m_sample_metadata_file:
        raise ValueError("--m-sample-metadata-file must be provided when --m-sample-metadata-column is set.")

    # --- Command Construction ---
    cmd = [
        "qiime", "sample-classifier", "heatmap",
        "--i-table", str(i_table),
        "--i-importance", str(i_importance),
        "--o-heatmap", str(o_heatmap),
        "--p-feature-count", str(p_feature_count),
    ]

    if o_filtered_table:
        cmd.extend(["--o-filtered-table", str(o_filtered_table)])

    if m_sample_metadata_file:
        cmd.extend(["--m-sample-metadata-file", str(m_sample_metadata_file)])

    if m_sample_metadata_column:
        cmd.extend(["--m-sample-metadata-column", m_sample_metadata_column])

    if p_group_samples:
        cmd.append("--p-group-samples")
    # The default is --p-no-group-samples, so we only add the flag if True.

    if p_normalize:
        cmd.append("--p-normalize")
    else:
        cmd.append("--p-no-normalize")

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
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        logger.info("Command executed successfully.")

    except FileNotFoundError:
        logger.error("QIIME2 command not found. Is it installed and in your PATH?")
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "QIIME2 command not found. Is it installed and in your PATH?",
            "output_files": [],
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
        }

    # --- Prepare and Return Structured Output ---
    output_files: List[str] = [str(o_heatmap)]
    if o_filtered_table:
        output_files.append(str(o_filtered_table))

    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()