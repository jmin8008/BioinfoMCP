import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def taxa_barplot(
    i_table: Path,
    i_taxonomy: Path,
    p_level: int,
    o_visualization: Path,
    m_metadata_file: Optional[List[Path]] = None,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Generate an interactive barplot of taxon abundances.

    This tool wraps the 'qiime taxa barplot' command. It produces an interactive
    barplot of taxon abundances, allowing for visualization at various taxonomic
    levels and grouping of samples by metadata.

    Args:
        i_table: Path to the feature table artifact (FeatureTable[Frequency]).
        i_taxonomy: Path to the taxonomy classifications artifact (FeatureData[Taxonomy]).
        p_level: The taxonomic level at which the features should be collapsed.
        o_visualization: Path to the output visualization file (.qzv).
        m_metadata_file: Optional list of paths to sample metadata files or artifacts.
        verbose: Display verbose output to stdout and stderr.
        quiet: Suppress all output to stdout and stderr.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output files.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found: {i_table}")
    if not i_taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy file not found: {i_taxonomy}")

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            if not Path(metadata_path).is_file():
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    if p_level <= 0:
        raise ValueError("p_level must be a positive integer.")

    if verbose and quiet:
        raise ValueError("Cannot set both --verbose and --quiet flags simultaneously.")

    # Ensure output directory exists
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "taxa", "barplot",
        "--i-table", str(i_table),
        "--i-taxonomy", str(i_taxonomy),
        "--p-level", str(p_level),
        "--o-visualization", str(o_visualization),
    ]

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            cmd.extend(["--m-metadata-file", str(metadata_path)])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        
        # --- Structured Result Return (Success) ---
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "visualization": str(o_visualization)
            }
        }
    except FileNotFoundError:
        logger.error("QIIME 2 is not installed or not in the system's PATH.")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME taxa barplot command failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        # --- Structured Result Return (Failure) ---
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME taxa barplot command failed.",
            "return_code": e.returncode,
            "output_files": {}
        }

if __name__ == '__main__':
    mcp.run()