import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def feature_table_filter_samples(
    i_table: Path,
    o_filtered_table: Path,
    m_metadata_file: Optional[List[Path]] = None,
    p_where: Optional[str] = None,
    p_min_frequency: Optional[int] = None,
    p_max_frequency: Optional[int] = None,
    p_min_features: Optional[int] = None,
    p_max_features: Optional[int] = None,
    p_filter_empty_features: bool = True,
    p_exclude_ids: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """
    Filter samples from a feature table based on metadata and/or feature/frequency counts.

    This tool filters samples from a feature table based on sample metadata and/or
    the number of features or total frequency per sample. At least one filtering
    criterion must be provided.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found: {i_table}")

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            if not Path(metadata_path).is_file():
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    # QIIME 2 requires at least one filtering criterion.
    if all(p is None for p in [m_metadata_file, p_where, p_min_frequency, p_max_frequency, p_min_features, p_max_features]):
        raise ValueError(
            "At least one filtering criterion (--m-metadata-file, --p-where, "
            "--p-min-frequency, --p-max-frequency, --p-min-features, or "
            "--p-max-features) must be provided."
        )

    # Validate numeric ranges
    if p_min_frequency is not None and p_min_frequency < 0:
        raise ValueError("--p-min-frequency must be a non-negative integer.")
    if p_max_frequency is not None and p_max_frequency < 0:
        raise ValueError("--p-max-frequency must be a non-negative integer.")
    if p_min_features is not None and p_min_features < 0:
        raise ValueError("--p-min-features must be a non-negative integer.")
    if p_max_features is not None and p_max_features < 0:
        raise ValueError("--p-max-features must be a non-negative integer.")

    if p_min_frequency is not None and p_max_frequency is not None and p_min_frequency > p_max_frequency:
        raise ValueError("--p-min-frequency cannot be greater than --p-max-frequency.")
    if p_min_features is not None and p_max_features is not None and p_min_features > p_max_features:
        raise ValueError("--p-min-features cannot be greater than --p-max-features.")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "filter-samples",
        "--i-table", str(i_table),
        "--o-filtered-table", str(o_filtered_table),
    ]

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            cmd.extend(["--m-metadata-file", str(metadata_path)])

    if p_where:
        cmd.extend(["--p-where", p_where])

    if p_min_frequency is not None:
        cmd.extend(["--p-min-frequency", str(p_min_frequency)])

    if p_max_frequency is not None:
        cmd.extend(["--p-max-frequency", str(p_max_frequency)])

    if p_min_features is not None:
        cmd.extend(["--p-min-features", str(p_min_features)])

    if p_max_features is not None:
        cmd.extend(["--p-max-features", str(p_max_features)])

    cmd.append("--p-filter-empty-features" if p_filter_empty_features else "--p-no-filter-empty-features")
    cmd.append("--p-exclude-ids" if p_exclude_ids else "--p-no-exclude-ids")

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    try:
        command_str = " ".join(map(str, cmd))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        return {
            "error": "QIIME 2 command not found. Please ensure 'qiime' is in your system's PATH."
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "Command execution failed.",
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "filtered_table": str(o_filtered_table)
        }
    }

if __name__ == '__main__':
    mcp.run()