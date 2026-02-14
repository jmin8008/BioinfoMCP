from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, Literal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP()

@mcp.tool()
def raxml(
    alignment: Path,
    tree: Path,
    seed: Optional[int] = None,
    n_threads: int = 1,
    substitution_model: str = 'GTRGAMMA',
    raxml_version: Literal['raxml', 'raxml-ng'] = 'raxml',
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """
    Construct a phylogenetic tree with RAxML using QIIME 2.

    This tool wraps the 'qiime phylogeny raxml' command to infer a phylogenetic
    tree from a multiple sequence alignment using the RAxML program.

    Parameters
    ----------
    alignment : Path
        Path to the input artifact: Aligned sequences to be used for
        phylogenetic reconstruction. (QIIME 2 type: FeatureData[AlignedSequence])
    tree : Path
        Path for the output artifact: The resulting phylogenetic tree.
        (QIIME 2 type: Phylogeny[Rooted])
    seed : Optional[int], optional
        Random number seed. Some RAxML versions may require this parameter.
        If not provided, no seed is set.
    n_threads : int, optional
        The number of threads to use for multithreaded processing. Use 0 to let
        RAxML automatically determine the number of threads to use.
        (default: 1)
    substitution_model : str, optional
        Model of Nucleotide Substitution to be used by RAxML.
        (default: 'GTRGAMMA')
    raxml_version : Literal['raxml', 'raxml-ng'], optional
        Specify which version of RAxML to use.
        (default: 'raxml')
    verbose : bool, optional
        Display verbose QIIME 2 output to stdout. (default: False)
    quiet : bool, optional
        Silence QIIME 2 output if execution is successful. (default: False)

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output file paths.

    Raises
    ------
    FileNotFoundError
        If the input alignment file does not exist.
    ValueError
        If n_threads is a negative number.
    subprocess.CalledProcessError
        If the underlying QIIME 2 command fails.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")
    if n_threads < 0:
        raise ValueError("The number of threads (n_threads) must be a non-negative integer.")

    # --- Command Construction ---
    cmd = [
        "qiime", "phylogeny", "raxml",
        "--i-alignment", str(alignment),
        "--o-tree", str(tree),
        "--p-n-threads", str(n_threads),
        "--p-substitution-model", substitution_model,
        "--p-raxml-version", raxml_version,
    ]

    if seed is not None:
        cmd.extend(["--p-seed", str(seed)])

    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")

    command_executed = " ".join(cmd)
    logger.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        stdout = result.stdout
        stderr = result.stderr
        output_files = {"tree": str(tree)}

        logger.info(f"QIIME 2 RAxML completed successfully. Output tree at: {tree}")
        return {
            "command_executed": command_executed,
            "stdout": stdout,
            "stderr": stderr,
            "output_files": output_files
        }
    except FileNotFoundError:
        err_msg = "`qiime` command not found. Please ensure QIIME 2 is installed and accessible in your system's PATH."
        logger.error(err_msg)
        # Re-raising with a more informative message or as a different exception type might be desired
        # depending on the server's error handling strategy.
        raise RuntimeError(err_msg)
    except subprocess.CalledProcessError as e:
        logger.error(f"QIIME 2 RAxML command failed with exit code {e.returncode}")
        # Stderr often contains the most useful error message from QIIME 2
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Stdout: {e.stdout}")
        # Propagate the exception to let the MCP framework handle it
        raise e

if __name__ == '__main__':
    mcp.run()