from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional
import logging

# Setup logging for better feedback
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP()

@mcp.tool()
def fasttree(
    alignment: Path,
    tree: Path,
    n_threads: int = 1,
    parttree: bool = False,
    no_support: bool = False,
    fastest: bool = False,
    raxml_one_per_branch: bool = False,
    scaffold_path: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Construct a phylogenetic tree with FastTree using QIIME 2.

    This tool uses the FastTree program to build an approximate maximum-likelihood
    phylogenetic tree from a multiple sequence alignment. It serves as a wrapper
    for the 'qiime phylogeny fasttree' command.

    Parameters
    ----------
    alignment : Path
        Path to the input aligned sequences artifact (`--i-alignment`). [required]
    tree : Path
        Path for the output phylogenetic tree artifact (`--o-tree`). [required]
    n_threads : int, optional
        The number of threads to use. Use 0 to automatically use all available cores.
        Corresponds to `--p-n-threads`. (default: 1)
    parttree : bool, optional
        (EXPERIMENTAL) Build a tree from a subset of sequences and add the rest
        using the "-fastest" option. Corresponds to `--p-parttree`. (default: False)
    no_support : bool, optional
        (ADVANCED) Do not compute support values. This is much faster.
        Corresponds to `--p-no-support`. (default: False)
    fastest : bool, optional
        (ADVANCED) Use the "-fastest" option in FastTree for increased speed.
        Corresponds to `--p-fastest`. (default: False)
    raxml_one_per_branch : bool, optional
        (ADVANCED) Use the "-spr 4" and "-fastest" options in FastTree for speed.
        Corresponds to `--p-raxml-one-per-branch`. (default: False)
    scaffold_path : Optional[Path], optional
        (ADVANCED) Path to a file containing a scaffold tree artifact.
        Corresponds to `--p-scaffold-path`. (default: None)
    verbose : bool, optional
        Display verbose output during execution. (default: False)
    quiet : bool, optional
        Silence output if execution is successful. (default: False)

    Returns
    -------
    dict
        A dictionary containing the executed command, stdout, stderr, and a
        dictionary of output file paths upon success. In case of an error, it
        includes an error message and return code.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")
    if scaffold_path and not scaffold_path.is_file():
        raise FileNotFoundError(f"Optional scaffold tree file not found at: {scaffold_path}")
    if n_threads < 0:
        raise ValueError("n_threads must be a non-negative integer (0 for all cores).")
    
    # Ensure the output directory exists
    if tree.parent and not tree.parent.is_dir():
        try:
            tree.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Created output directory: {tree.parent}")
        except OSError as e:
            raise OSError(f"Could not create output directory {tree.parent}: {e}")

    # --- Command Construction ---
    cmd = [
        "qiime", "phylogeny", "fasttree",
        "--i-alignment", str(alignment),
        "--o-tree", str(tree),
        "--p-n-threads", str(n_threads),
    ]

    if parttree:
        cmd.append("--p-parttree")
    if no_support:
        cmd.append("--p-no-support")
    if fastest:
        cmd.append("--p-fastest")
    if raxml_one_per_branch:
        cmd.append("--p-raxml-one-per-branch")
    if scaffold_path:
        cmd.extend(["--p-scaffold-path", str(scaffold_path)])
    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_str = " ".join(cmd)
    log.info(f"Executing command: {command_str}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        log.info("QIIME 2 fasttree execution completed successfully.")

    except FileNotFoundError:
        error_msg = "Executable 'qiime' not found. Please ensure QIIME 2 is installed and in your system's PATH."
        log.error(error_msg)
        return {
            "command_executed": command_str,
            "stdout": "",
            "stderr": error_msg,
            "error": "QIIME 2 not found.",
            "return_code": 127,
            "output_files": {}
        }
    except subprocess.CalledProcessError as e:
        log.error(f"QIIME 2 fasttree execution failed with return code {e.returncode}")
        log.error(f"Stderr:\n{e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 fasttree execution failed.",
            "return_code": e.returncode,
            "output_files": {}
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "tree": str(tree)
        }
    }

if __name__ == '__main__':
    mcp.run()