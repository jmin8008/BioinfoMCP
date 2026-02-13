import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def demux_filter_samples(
    i_demux: Path,
    m_metadata_file: Path,
    o_filtered_demux: Path,
    p_where: Optional[str] = None,
    p_exclude_ids: bool = False,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Filter samples from a demultiplexed QZA based on metadata.

    This tool filters samples from a demultiplexed sequence artifact (QIIME 2 QZA format)
    based on criteria specified in a metadata file. You can either include or exclude
    samples that match a SQL WHERE clause.

    Parameters
    ----------
    i_demux
        Path to the demultiplexed sequences artifact (.qza) to be filtered.
    m_metadata_file
        Path to the sample metadata file. The file must contain a column with
        the sample IDs to be filtered.
    o_filtered_demux
        Path where the resulting filtered demultiplexed sequences artifact (.qza)
        will be saved.
    p_where
        SQLite WHERE clause specifying sample IDs to keep or discard.
        Example: "[body-site] IN ('gut', 'tongue')"
    p_exclude_ids
        If True, the samples selected by the 'p_where' clause will be excluded,
        rather than included. Defaults to False.
    verbose
        Display verbose output during command execution.
    quiet
        Silence output if execution is successful.

    Returns
    -------
    dict
        A dictionary containing the executed command, stdout, stderr, and a
        dictionary of output files.
    """
    # --- Input Validation ---
    if not i_demux.is_file():
        raise FileNotFoundError(f"Input demux artifact not found at: {i_demux}")
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {m_metadata_file}")
    if not o_filtered_demux.parent.is_dir():
        raise NotADirectoryError(
            f"Output directory does not exist: {o_filtered_demux.parent}"
        )

    # --- Command Construction ---
    cmd = [
        "qiime",
        "demux",
        "filter-samples",
        "--i-demux",
        str(i_demux),
        "--m-metadata-file",
        str(m_metadata_file),
        "--o-filtered-demux",
        str(o_filtered_demux),
    ]

    if p_where:
        cmd.extend(["--p-where", p_where])

    if p_exclude_ids:
        cmd.append("--p-exclude-ids")

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_executed = " ".join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "qiime command not found. Please ensure QIIME 2 is installed and in your PATH."
        )
    except subprocess.CalledProcessError as e:
        # QIIME 2 often prints detailed errors to stderr
        error_message = (
            f"QIIME 2 command failed with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr:\n{e.stderr}\n"
            f"Stdout:\n{e.stdout}"
        )
        raise RuntimeError(error_message) from e

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {"filtered_demux": str(o_filtered_demux)},
    }


if __name__ == "__main__":
    mcp.run()