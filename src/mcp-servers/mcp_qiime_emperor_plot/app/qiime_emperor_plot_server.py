import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def emperor_plot(
    pcoa: Path,
    visualization: Path,
    metadata: Optional[Path] = None,
    metadata_column: Optional[str] = None,
    custom_axes: Optional[str] = None,
    ignore_missing_samples: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """
    Generate an Emperor plot from a PCoA results artifact.

    This tool visualizes principal coordinates analysis (PCoA) results using Emperor.
    It allows for coloring points by sample metadata, customizing axes, and handling
    mismatches between PCoA results and metadata.

    Args:
        pcoa (Path): The principal coordinates matrix to be visualized (PCoAResults artifact).
        visualization (Path): The path to write the output Emperor plot visualization (.qzv).
        metadata (Optional[Path]): The sample metadata file. Defaults to None.
        metadata_column (Optional[str]): Categorical metadata column to use for coloring.
                                          Requires 'metadata' to be provided. Defaults to None.
        custom_axes (Optional[str]): Comma-separated list of principal coordinate axes to plot.
                                     By default, all axes are plotted. Defaults to None.
        ignore_missing_samples (bool): If True, ignore samples present in the PCoA results
                                       but not in the metadata. By default (False), the command
                                       will fail if samples are missing from the metadata.
        verbose (bool): Display verbose output to stdout. Defaults to False.
        quiet (bool): Silence output if execution is successful. Defaults to False.

    Returns:
        dict: A dictionary containing the execution command, stdout, stderr,
              and a list of output files.
    """
    # --- Input Validation ---
    if not pcoa.is_file():
        raise FileNotFoundError(f"Input PCoA artifact not found at: {pcoa}")

    if metadata and not metadata.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata}")

    if metadata_column and not metadata:
        raise ValueError(
            "'metadata_column' was provided, but the 'metadata' file was not."
        )

    if not visualization.parent.is_dir():
        raise NotADirectoryError(
            f"The parent directory for the output visualization does not exist: {visualization.parent}"
        )

    # --- Command Construction ---
    cmd = ["qiime", "emperor", "plot", "--i-pcoa", str(pcoa)]

    if metadata:
        cmd.extend(["--m-metadata-file", str(metadata)])

    if metadata_column:
        cmd.extend(["--m-metadata-column", metadata_column])

    if custom_axes:
        cmd.extend(["--p-custom-axes", custom_axes])

    if ignore_missing_samples:
        cmd.append("--p-ignore-missing-samples")

    cmd.extend(["--o-visualization", str(visualization)])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except FileNotFoundError:
        return {
            "command_executed": " ".join(cmd),
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Please ensure QIIME 2 is installed and in your PATH.",
            "output_files": [],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
        }

    # --- Structured Result Return ---
    output_files = [str(visualization)] if visualization.exists() else []

    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }


if __name__ == "__main__":
    mcp.run()