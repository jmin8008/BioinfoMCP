import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def volatility(
    i_table: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    p_state_column: str,
    p_individual_id_column: str,
    o_visualization: Path,
    p_default_group_column: Optional[str] = None,
    p_default_metric: Optional[str] = None,
    p_yscale: str = 'linear',
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Generate a volatility plot to visualize the rate of change of a single metric over time.

    This plot displays the mean rate of change between all pairs of time points
    for each group of samples. The x-axis is the distance in time between time
    points, and the y-axis is the mean change in the metric at that time
    distance. A linear regression is fit to these data, and the slope and R^2
    values are reported.
    """
    # --- Input Validation ---
    if not i_table.exists():
        raise FileNotFoundError(f"Input table artifact not found: {i_table}")
    if not m_metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")

    valid_yscales = ['linear', 'log', 'pow']
    if p_yscale not in valid_yscales:
        raise ValueError(f"Invalid p_yscale: '{p_yscale}'. Must be one of {valid_yscales}")

    # Ensure output directory exists
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "longitudinal", "volatility",
        "--i-table", str(i_table),
        "--m-metadata-file", str(m_metadata_file),
        "--m-metadata-column", m_metadata_column,
        "--p-state-column", p_state_column,
        "--p-individual-id-column", p_individual_id_column,
        "--o-visualization", str(o_visualization),
        "--p-yscale", p_yscale,
    ]

    if p_default_group_column:
        cmd.extend(["--p-default-group-column", p_default_group_column])
    
    if p_default_metric:
        cmd.extend(["--p-default-metric", p_default_metric])

    if verbose:
        cmd.append("--verbose")
    
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(o_visualization)]
        }
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and in your system's PATH.",
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": []
        }

if __name__ == '__main__':
    mcp.run()