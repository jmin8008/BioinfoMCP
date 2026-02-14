from fastmcp import FastMCP
from pathlib import Path
from typing import Optional
import subprocess
import logging

# Initialize MCP application
mcp = FastMCP()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@mcp.tool()
def phylogeny_midpoint_root(
    i_tree: Path,
    o_rooted_tree: Path,
    p_root_at: Optional[str] = None,
    p_root_on: Optional[str] = None,
    verbose: bool = False,
):
    """
    Midpoint root an unrooted phylogenetic tree using QIIME 2.

    This tool takes an unrooted phylogenetic tree and roots it at the midpoint
    of the longest edge, or at a user-specified node or edge.

    Parameters
    ----------
    i_tree : Path
        The input unrooted phylogenetic tree artifact (.qza).
    o_rooted_tree : Path
        The path for the output rooted phylogenetic tree artifact (.qza).
    p_root_at : Optional[str], optional
        Node to root the tree at. If not provided, the tree will be rooted
        at the midpoint of the longest edge.
    p_root_on : Optional[str], optional
        Edge to root the tree at. If not provided, the tree will be rooted
        at the midpoint of the longest edge.
    verbose : bool, optional
        Display verbose output during command execution. Default is False.

    Returns
    -------
    dict
        A dictionary containing the execution details, including the command,
        stdout, stderr, and a dictionary of output file paths. In case of
        an error, it returns a structured error dictionary.
    """
    # --- Input Validation ---
    if not i_tree.is_file():
        raise ValueError(f"Input tree file does not exist: {i_tree}")

    # --- File Path Handling ---
    # Ensure the output directory exists to prevent errors
    o_rooted_tree.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "phylogeny", "midpoint-root",
        "--i-tree", str(i_tree),
        "--o-rooted-tree", str(o_rooted_tree)
    ]

    if p_root_at:
        cmd.extend(["--p-root-at", p_root_at])

    if p_root_on:
        cmd.extend(["--p-root-on", p_root_on])

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution & Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        stdout = result.stdout
        stderr = result.stderr
        logging.info("QIIME 2 command executed successfully.")

    except FileNotFoundError:
        # This is a critical server configuration error.
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in the system's PATH.")
    except subprocess.CalledProcessError as e:
        # The tool itself failed; return a structured error message as per requirements.
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        logging.error(f"Stdout: {e.stdout}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error_message": "QIIME 2 command failed. Check stderr for details.",
            "return_code": e.returncode
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": {
            "rooted_tree": str(o_rooted_tree)
        }
    }

if __name__ == '__main__':
    mcp.run()