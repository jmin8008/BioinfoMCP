import subprocess
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def qiime_diversity_lib_shannon(
    i_table: Path,
    o_vector: Path,
    p_base: int = 2,
    m_metadata_file: Optional[List[Path]] = None,
    m_metadata_column: Optional[str] = None,
    p_where: Optional[str] = None,
    p_no_where: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    cmd_config: Optional[Path] = None,
):
    """
    Computes Shannon's index for all samples in a frequency table using QIIME 2.

    This tool is a wrapper for the 'qiime diversity-lib shannon' command.
    Shannon's index accounts for both the abundance and evenness of the features present.

    Parameters
    ----------
    i_table : Path
        The feature table artifact (FeatureTable[Frequency]) to compute Shannon's index from. [required]
    o_vector : Path
        The path to write the resulting Shannon's index vector artifact (SampleData[AlphaDiversity]). [required]
    p_base : int, optional
        The logarithm base to use when calculating Shannon's index. Default is 2.
    m_metadata_file : Optional[List[Path]], optional
        Metadata file(s) or artifact(s) viewable as metadata. Can be supplied multiple times.
    m_metadata_column : Optional[str], optional
        Column from metadata file or artifact to use for filtering.
    p_where : Optional[str], optional
        SQLite WHERE clause for filtering samples/features based on metadata.
    p_no_where : bool, optional
        DEPRECATED: Do not filter the feature table based on metadata. Use --p-where "" instead. Default is False.
    verbose : bool, optional
        Display verbose output to stdout. Default is False.
    quiet : bool, optional
        Silence output if execution is successful. Default is False.
    cmd_config : Optional[Path], optional
        Use a config file for command options.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a map of output files.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table artifact not found at: {i_table}")

    if p_base < 2:
        raise ValueError(f"Logarithm base '--p-base' must be an integer >= 2, but got {p_base}.")

    if m_metadata_file:
        for mf in m_metadata_file:
            if not mf.is_file():
                raise FileNotFoundError(f"Metadata file not found at: {mf}")

    if cmd_config and not cmd_config.is_file():
        raise FileNotFoundError(f"Command config file not found at: {cmd_config}")

    # --- File Path Handling ---
    # Ensure the output directory exists
    o_vector.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "diversity-lib", "shannon",
        "--i-table", str(i_table),
        "--o-vector", str(o_vector),
        "--p-base", str(p_base),
    ]

    if m_metadata_file:
        for mf in m_metadata_file:
            cmd.extend(["--m-metadata-file", str(mf)])

    if m_metadata_column:
        cmd.extend(["--m-metadata-column", m_metadata_column])

    if p_where is not None:
        cmd.extend(["--p-where", p_where])

    if p_no_where:
        cmd.append("--p-no-where")

    if verbose:
        cmd.append("--verbose")

    if quiet:
        cmd.append("--quiet")

    if cmd_config:
        cmd.extend(["--cmd-config", str(cmd_config)])

    # --- Subprocess Execution and Error Handling ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        return {
            "error": "QIIME 2 command not found. Please ensure 'qiime' is installed and in your system's PATH.",
            "command_executed": command_executed,
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "QIIME 2 command failed with a non-zero exit code.",
            "return_code": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "command_executed": command_executed,
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "shannon_vector": str(o_vector)
        }
    }

if __name__ == '__main__':
    mcp.run()