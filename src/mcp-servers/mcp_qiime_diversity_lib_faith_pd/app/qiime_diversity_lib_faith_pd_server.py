from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import List, Dict, Any

mcp = FastMCP()

@mcp.tool()
def diversity_lib_faith_pd(
    i_table: Path,
    i_phylogeny: Path,
    o_vector: Path,
    p_threads: int = 1,
) -> Dict[str, Any]:
    """
    Computes Faith's Phylogenetic Diversity (PD) using QIIME 2.

    This tool calculates Faith's PD, a measure of biodiversity that incorporates
    phylogenetic relationships between features. It requires a feature table and a
    corresponding phylogenetic tree.

    Parameters
    ----------
    i_table : Path
        The feature table artifact containing the samples for which Faith's PD
        should be computed. (QIIME 2 artifact: FeatureTable[Frequency])
    i_phylogeny : Path
        The rooted phylogenetic tree artifact containing tip identifiers that
        correspond to the feature identifiers in the table.
        (QIIME 2 artifact: Phylogeny[Rooted])
    o_vector : Path
        The path for the output vector artifact of Faith's PD values by sample.
        (QIIME 2 artifact: SampleData[AlphaDiversity])
    p_threads : int, optional
        The number of threads to use for computation. Defaults to 1.

    Returns
    -------
    dict
        A dictionary containing the command executed, stdout, stderr, and a list
        of output files. In case of an error, it includes error details and the
        return code.
    """
    # 1. Input Validation
    if not i_table.is_file():
        raise FileNotFoundError(f"Input table file not found at: {i_table}")
    if not i_phylogeny.is_file():
        raise FileNotFoundError(f"Input phylogeny file not found at: {i_phylogeny}")
    if not o_vector.parent.exists():
        o_vector.parent.mkdir(parents=True, exist_ok=True)
    if p_threads < 1:
        raise ValueError("The number of threads (--p-threads) must be a positive integer.")

    # 2. Command Construction
    cmd = [
        "qiime", "diversity-lib", "faith-pd",
        "--i-table", str(i_table),
        "--i-phylogeny", str(i_phylogeny),
        "--o-vector", str(o_vector),
        "--p-threads", str(p_threads),
    ]

    # 3. Subprocess Execution and Error Handling
    command_str = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # 4. Structured Result Return on Success
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [
                {"path": str(o_vector), "type": "SampleData[AlphaDiversity]"}
            ]
        }

    except FileNotFoundError:
        # This error is raised if the 'qiime' command is not found.
        raise RuntimeError("QIIME 2 is not installed or not in the system's PATH.")

    except subprocess.CalledProcessError as e:
        # This error is raised if the QIIME 2 command returns a non-zero exit code.
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": f"QIIME 2 command failed with exit code {e.returncode}.",
            "return_code": e.returncode,
            "output_files": []
        }

if __name__ == '__main__':
    mcp.run()