from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

mcp = FastMCP()

@mcp.tool()
def iqtree(
    alignment: Path,
    tree: Path,
    seed: Optional[int] = None,
    n_cores: str = '1',
    substitution_model: str = 'auto',
    fast: bool = False,
    alrt: int = 1000,
    bootstrap_replicates: int = 1000,
    stop_iter: int = 200,
    perturb_nni_strength: float = 0.5,
    spr_radius: int = 6,
    allnni: bool = False,
    safe: bool = False,
    other_args: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Construct a phylogenetic tree with IQ-TREE using the QIIME 2 plugin.

    This tool uses IQ-TREE to infer a phylogenetic tree from a multiple
    sequence alignment. It provides a wide range of options to control the
    tree inference process, including substitution models, bootstrap support,
    and search algorithms.

    Args:
        alignment: Path to the input phylogenetic sequence alignment artifact (.qza).
        tree: Path for the output phylogenetic tree artifact (.qza).
        seed: Random number seed. If not provided, a random seed will be used.
        n_cores: The number of cores to use. Use 'auto' to let IQ-TREE decide,
                 or provide a positive integer as a string.
        substitution_model: Model of nucleotide substitution (e.g., 'GTR+G', 'auto').
        fast: Use fast search to reduce computing time.
        alrt: Number of bootstrap replicates for SH-aLRT single branch test.
        bootstrap_replicates: Number of bootstrap replicates for the main analysis.
        stop_iter: Number of unsuccessful iterations to stop the search.
        perturb_nni_strength: Perturbation strength for NNI (Nearest Neighbor Interchange) search.
        spr_radius: Radius for SPR (Subtree Pruning and Regrafting) search.
        allnni: Perform a more thorough NNI search.
        safe: Use safe likelihood kernel to avoid numerical underflow.
        other_args: A string of other arguments to be passed to the IQ-TREE command-line.
                    Example: "-ntmax 5 -m MFP"
        verbose: Display verbose QIIME 2 output during execution.

    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output file paths. In case of an error, it includes an
        error message.
    """
    # --- Input Validation ---
    if not alignment.is_file():
        raise FileNotFoundError(f"Input alignment file not found at: {alignment}")

    if not str(tree).endswith(".qza"):
        raise ValueError("Output tree path must have a .qza extension.")

    if n_cores != 'auto':
        try:
            n_cores_int = int(n_cores)
            if n_cores_int <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("n_cores must be 'auto' or a string representing a positive integer.")

    if alrt < 0:
        raise ValueError("alrt must be a non-negative integer.")
    if bootstrap_replicates < 0:
        raise ValueError("bootstrap_replicates must be a non-negative integer.")
    if stop_iter < 0:
        raise ValueError("stop_iter must be a non-negative integer.")
    if spr_radius < 0:
        raise ValueError("spr_radius must be a non-negative integer.")

    # --- Output Directory Handling ---
    try:
        tree.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create output directory {tree.parent}: {e}")

    # --- Command Construction ---
    cmd = [
        "qiime", "phylogeny", "iqtree",
        "--i-alignment", str(alignment),
        "--o-tree", str(tree),
        "--p-n-cores", str(n_cores),
        "--p-substitution-model", substitution_model,
        "--p-alrt", str(alrt),
        "--p-bootstrap-replicates", str(bootstrap_replicates),
        "--p-stop-iter", str(stop_iter),
        "--p-perturb-nni-strength", str(perturb_nni_strength),
        "--p-spr-radius", str(spr_radius),
    ]

    if seed is not None:
        cmd.extend(["--p-seed", str(seed)])
    if fast:
        cmd.append("--p-fast")
    if allnni:
        cmd.append("--p-allnni")
    if safe:
        cmd.append("--p-safe")
    if other_args:
        cmd.extend(["--p-other-args", other_args])
    if verbose:
        cmd.append("--verbose")
    else:
        cmd.append("--quiet")

    command_str = " ".join(cmd)

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        stdout = result.stdout
        stderr = result.stderr

    except FileNotFoundError:
        raise RuntimeError("The 'qiime' command was not found. Ensure QIIME 2 is installed and accessible in the system's PATH.")

    except subprocess.CalledProcessError as e:
        # Return structured error information as per requirements
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 q2-phylogeny iqtree command failed with exit code {e.returncode}.",
            "output_files": {}
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {"tree": str(tree)}
    }

if __name__ == '__main__':
    mcp.run()