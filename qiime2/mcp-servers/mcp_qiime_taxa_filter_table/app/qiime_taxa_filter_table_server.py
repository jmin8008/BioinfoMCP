from fastmcp import FastMCP
from pathlib import Path
import subprocess
from typing import Optional, List

# Initialize the MCP server
mcp = FastMCP()

@mcp.tool()
def qiime_taxa_filter_table(
    i_table: Path,
    i_taxonomy: Path,
    o_filtered_table: Path,
    p_include: Optional[str] = None,
    p_exclude: Optional[str] = None,
    p_mode: str = 'contains',
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """
    Filter features from a feature table based on their taxonomy using QIIME 2.

    This tool filters a feature table, retaining or removing features based on
    their taxonomic assignments. Filtering can be done by including or excluding
    specific taxa.

    Args:
        i_table (Path): The feature table artifact (FeatureTable[Frequency]) from which features should be filtered.
        i_taxonomy (Path): The feature taxonomy artifact (FeatureData[Taxonomy]).
        o_filtered_table (Path): The path to write the resulting filtered feature table artifact.
        p_include (Optional[str]): Comma-separated list of taxa to be included.
        p_exclude (Optional[str]): Comma-separated list of taxa to be excluded.
        p_mode (str): How to apply include/exclude lists. 'contains' matches taxa within the lineage,
                      'exact' matches the deepest assigned taxon. Defaults to 'contains'.
        verbose (bool): Display verbose output to stdout.
        quiet (bool): Silence output if execution is successful.

    Returns:
        dict: A dictionary containing the executed command, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found: {i_table}")
    if not i_taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy file not found: {i_taxonomy}")

    allowed_modes = ['contains', 'exact']
    if p_mode not in allowed_modes:
        raise ValueError(f"Invalid mode '{p_mode}'. Allowed modes are: {', '.join(allowed_modes)}")

    if p_include is None and p_exclude is None:
        raise ValueError("At least one of 'p_include' or 'p_exclude' must be provided.")

    # --- Command Construction ---
    cmd = [
        "qiime", "taxa", "filter-table",
        "--i-table", str(i_table),
        "--i-taxonomy", str(i_taxonomy),
        "--o-filtered-table", str(o_filtered_table),
        "--p-mode", p_mode,
    ]

    if p_include:
        cmd.extend(["--p-include", p_include])
    if p_exclude:
        cmd.extend(["--p-exclude", p_exclude])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    # --- Subprocess Execution and Error Handling ---
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and in your system's PATH.",
            "output_files": [],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": [],
        }

    # --- Structured Result Return ---
    output_files: List[str] = []
    if o_filtered_table.exists():
        output_files.append(str(o_filtered_table))

    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()