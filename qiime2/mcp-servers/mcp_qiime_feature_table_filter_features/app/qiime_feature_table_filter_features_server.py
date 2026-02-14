from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

mcp = FastMCP()

@mcp.tool()
def feature_table_filter_features(
    i_table: Path,
    o_filtered_table: Path,
    m_metadata_file: Optional[List[Path]] = None,
    p_where: Optional[str] = None,
    p_exclude_ids: bool = False,
    p_min_frequency: Optional[int] = None,
    p_max_frequency: Optional[int] = None,
    p_min_samples: Optional[int] = None,
    p_max_samples: Optional[int] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """
    Filter features from a feature table based on frequency and/or metadata.

    This action can be used to filter features based on their total frequency,
    the number of samples they are observed in, or based on feature metadata.
    This tool is part of the QIIME 2 feature-table plugin.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found: {i_table}")

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            if not metadata_path.is_file():
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    if (p_where is not None or p_exclude_ids) and not m_metadata_file:
        raise ValueError("--m-metadata-file is required when using --p-where or --p-exclude-ids.")

    if p_min_frequency is not None and p_min_frequency < 0:
        raise ValueError("--p-min-frequency must be a non-negative integer.")
    if p_max_frequency is not None and p_max_frequency < 0:
        raise ValueError("--p-max-frequency must be a non-negative integer.")
    if p_min_samples is not None and p_min_samples < 0:
        raise ValueError("--p-min-samples must be a non-negative integer.")
    if p_max_samples is not None and p_max_samples < 0:
        raise ValueError("--p-max-samples must be a non-negative integer.")

    if verbose and quiet:
        raise ValueError("Cannot use --verbose and --quiet flags simultaneously.")

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "filter-features",
        "--i-table", str(i_table),
        "--o-filtered-table", str(o_filtered_table),
    ]

    if m_metadata_file:
        for metadata_path in m_metadata_file:
            cmd.extend(["--m-metadata-file", str(metadata_path)])

    if p_where:
        cmd.extend(["--p-where", p_where])

    if p_exclude_ids:
        cmd.append("--p-exclude-ids")

    if p_min_frequency is not None:
        cmd.extend(["--p-min-frequency", str(p_min_frequency)])

    if p_max_frequency is not None:
        cmd.extend(["--p-max-frequency", str(p_max_frequency)])

    if p_min_samples is not None:
        cmd.extend(["--p-min-samples", str(p_min_samples)])

    if p_max_samples is not None:
        cmd.extend(["--p-max-samples", str(p_max_samples)])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        # --- Structured Result Return on Success ---
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {
                "filtered_table": str(o_filtered_table)
            }
        }
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your system's PATH.",
            "error": "Executable not found",
            "return_code": 127
        }
    except subprocess.CalledProcessError as e:
        # --- Structured Error Return on Failure ---
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}",
            "return_code": e.returncode
        }

if __name__ == '__main__':
    mcp.run()