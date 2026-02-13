import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def ancombc(
    table: Path,
    metadata_file: Path,
    formula: str,
    differentials: Path,
    p_adj_method: str = 'holm',
    prv_cut: float = 0.1,
    lib_cut: int = 0,
    reference_levels: Optional[List[str]] = None,
    neg_lb: bool = False,
    tol: float = 1e-05,
    max_iter: int = 100,
    conserve: bool = False,
    alpha: float = 0.05,
    global_test: bool = False,
):
    """
    Apply Analysis of Compositions of Microbiomes with Bias Correction (ANCOM-BC).

    This method identifies features that are differentially abundant across sample
    groups in a feature table.

    Parameters
    ----------
    table
        The feature table artifact (`FeatureTable[Frequency]`) to be used for ANCOM-BC analysis.
    metadata_file
        The sample metadata file.
    formula
        The statistical formula for testing (e.g., 'var1 + var2').
    differentials
        The path to write the resulting differentials artifact.
    p_adj_method
        The p-value correction method.
    prv_cut
        The prevalence cutoff. Features with prevalence less than this value will be excluded.
    lib_cut
        The library size cutoff. Samples with library size less than this value will be excluded.
    reference_levels
        Define the reference level for each variable in the formula (e.g., ['variable1:level1', 'variable2:level2']).
    neg_lb
        Whether to classify a taxon as a structural zero if its observed abundance is zero and its predicted abundance is negative.
    tol
        The convergence tolerance.
    max_iter
        The maximum number of iterations.
    conserve
        Whether to use a conservative variance estimate of the test statistic.
    alpha
        The level of significance.
    global_test
        Whether to perform a global test.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a list of output files.
    """
    # --- Input Validation ---
    if not table.exists():
        raise FileNotFoundError(f"Input table file not found: {table}")
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

    p_adj_method_choices = ['holm', 'hochberg', 'hommel', 'bonferroni', 'BH', 'BY', 'fdr', 'none']
    if p_adj_method not in p_adj_method_choices:
        raise ValueError(f"p_adj_method must be one of {p_adj_method_choices}, not '{p_adj_method}'")

    if not (0.0 <= prv_cut <= 1.0):
        raise ValueError(f"prv_cut must be between 0.0 and 1.0, not {prv_cut}")
    if lib_cut < 0:
        raise ValueError(f"lib_cut must be a non-negative integer, not {lib_cut}")
    if tol <= 0.0:
        raise ValueError(f"tol must be greater than 0.0, not {tol}")
    if max_iter < 1:
        raise ValueError(f"max_iter must be at least 1, not {max_iter}")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"alpha must be between 0.0 and 1.0, not {alpha}")

    # --- Command Construction ---
    cmd = [
        "qiime", "composition", "ancombc",
        "--i-table", str(table),
        "--m-metadata-file", str(metadata_file),
        "--p-formula", formula,
        "--o-differentials", str(differentials),
        "--p-p-adj-method", p_adj_method,
        "--p-prv-cut", str(prv_cut),
        "--p-lib-cut", str(lib_cut),
        "--p-tol", str(tol),
        "--p-max-iter", str(max_iter),
        "--p-alpha", str(alpha),
    ]

    if reference_levels:
        for level in reference_levels:
            cmd.extend(["--p-reference-levels", level])

    if neg_lb:
        cmd.append("--p-neg-lb")
    if conserve:
        cmd.append("--p-conserve")
    if global_test:
        cmd.append("--p-global-test")

    # --- Subprocess Execution ---
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
            "command_executed": " ".join(map(str, cmd)),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "ANCOM-BC execution failed.",
            "output_files": []
        }
    except FileNotFoundError:
        return {
            "command_executed": " ".join(map(str, cmd)),
            "stdout": "",
            "stderr": "qiime command not found. Make sure QIIME 2 is installed and in your PATH.",
            "return_code": 1,
            "error": "Command not found.",
            "output_files": []
        }

    # --- Structured Result Return ---
    return {
        "command_executed": " ".join(map(str, cmd)),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "differentials": str(differentials)
        }
    }


if __name__ == '__main__':
    mcp.run()