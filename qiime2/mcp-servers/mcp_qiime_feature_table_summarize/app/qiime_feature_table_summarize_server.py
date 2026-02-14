import subprocess
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def feature_table_summarize(
    i_table: Path,
    o_visualization: Path,
    m_sample_metadata_file: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Summarize a feature table.

    This tool generates a visualization that summarizes the key properties of a
    feature table, such as the number of samples, features, and the distribution
    of frequencies per sample and per feature.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {i_table}")

    if m_sample_metadata_file and not m_sample_metadata_file.is_file():
        raise FileNotFoundError(f"Sample metadata file not found at: {m_sample_metadata_file}")

    if o_visualization.exists():
        print(f"Warning: Output file {o_visualization} already exists and will be overwritten.")
    
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "feature-table", "summarize",
        "--i-table", str(i_table),
        "--o-visualization", str(o_visualization),
    ]

    if m_sample_metadata_file:
        cmd.extend(["--m-sample-metadata-file", str(m_sample_metadata_file)])

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
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed.",
            "output_files": []
        }
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "qiime command not found. Please ensure QIIME 2 is installed and in your PATH.",
            "return_code": 1,
            "error": "Command not found.",
            "output_files": []
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(o_visualization)]
    }

if __name__ == '__main__':
    mcp.run()