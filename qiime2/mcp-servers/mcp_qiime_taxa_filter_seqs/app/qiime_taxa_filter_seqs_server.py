from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def taxa_filter_table(
    i_table: Path,
    i_taxonomy: Path,
    o_filtered_table: Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    mode: str = "exact",
    verbose: bool = False,
):
    """
    Filter a feature table based on taxonomy.

    This tool filters a feature table, retaining or discarding features based on their
    taxonomic annotations.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not i_taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy artifact not found: {i_taxonomy}")
    if mode not in ["exact", "contains"]:
        raise ValueError("Mode must be either 'exact' or 'contains'.")
    
    o_filtered_table.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "taxa", "filter-table",
        "--i-table", str(i_table),
        "--i-taxonomy", str(i_taxonomy),
        "--o-filtered-table", str(o_filtered_table),
        "--p-mode", mode,
    ]

    if include:
        # The tool expects repeated flags for multiple values
        for term in include:
            cmd.extend(["--p-include", term])

    if exclude:
        # The tool expects repeated flags for multiple values
        for term in exclude:
            cmd.extend(["--p-exclude", term])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_table)],
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

@mcp.tool()
def taxa_filter_seqs(
    i_sequences: Path,
    i_taxonomy: Path,
    o_filtered_sequences: Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    mode: str = "exact",
    verbose: bool = False,
):
    """
    Filter sequences based on taxonomy.

    This tool filters a sequence artifact, retaining or discarding sequences based on their
    taxonomic annotations.
    """
    # --- Input Validation ---
    if not i_sequences.is_file():
        raise FileNotFoundError(f"Input sequences artifact not found: {i_sequences}")
    if not i_taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy artifact not found: {i_taxonomy}")
    if mode not in ["exact", "contains"]:
        raise ValueError("Mode must be either 'exact' or 'contains'.")

    o_filtered_sequences.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "taxa", "filter-seqs",
        "--i-sequences", str(i_sequences),
        "--i-taxonomy", str(i_taxonomy),
        "--o-filtered-sequences", str(o_filtered_sequences),
        "--p-mode", mode,
    ]

    if include:
        for term in include:
            cmd.extend(["--p-include", term])

    if exclude:
        for term in exclude:
            cmd.extend(["--p-exclude", term])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_sequences)],
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

@mcp.tool()
def feature_table_filter_seqs(
    i_data: Path,
    i_table: Path,
    o_filtered_data: Path,
    where: Optional[str] = None,
    exclude_ids: bool = False,
    m_metadata_file: Optional[Path] = None,
    verbose: bool = False,
):
    """
    Filter features from a sequence artifact based on a feature table.

    This tool is useful for ensuring that a sequence artifact contains only the
    features present in a corresponding (and potentially filtered) feature table.
    """
    # --- Input Validation ---
    if not i_data.is_file():
        raise FileNotFoundError(f"Input sequence data not found: {i_data}")
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if m_metadata_file and not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
    if where and not m_metadata_file:
        logger.warning("The 'where' parameter is typically used with a metadata file.")

    o_filtered_data.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "filter-seqs",
        "--i-data", str(i_data),
        "--i-table", str(i_table),
        "--o-filtered-data", str(o_filtered_data),
    ]

    if where:
        cmd.extend(["--p-where", where])
    
    if exclude_ids:
        cmd.append("--p-exclude-ids")

    if m_metadata_file:
        cmd.extend(["--m-metadata-file", str(m_metadata_file)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logger.info(f"Executing command: {command_str}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_filtered_data)],
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

if __name__ == '__main__':
    mcp.run()