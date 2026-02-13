import subprocess
import logging
from pathlib import Path
from typing import List
from fastmcp import FastMCP

# Initialize MCP and logging
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

@mcp.tool()
def emperor_biplot(
    i_biplot: Path,
    i_sample_metadata: List[Path],
    o_visualization: Path,
    p_number_of_features: int = 5,
    p_ignore_missing_samples: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Visualize and Interact with Biplot Ordinations using QIIME 2 Emperor.

    This tool generates an interactive biplot visualization from a PCoAResults
    artifact that contains biplot properties, along with associated sample metadata.

    Args:
        i_biplot: The biplot ordination matrix to be visualized. (QIIME 2 Artifact: PCoAResults % Properties('biplot'))
        i_sample_metadata: One or more metadata files or artifacts viewable as metadata.
        o_visualization: The path for the resulting visualization file (.qzv).
        p_number_of_features: The number of features to plot as arrows.
        p_ignore_missing_samples: If True, ignore samples present in the ordination but not in the metadata.
                                  By default (False), the command will fail in this case.
        verbose: If True, display verbose output during command execution.

    Returns:
        A dictionary containing the executed command, stdout, stderr, and a map of output file names to their paths.
    """
    # --- Input Validation ---
    if not i_biplot.is_file():
        raise FileNotFoundError(f"Input biplot artifact not found at: {i_biplot}")

    if not i_sample_metadata:
        raise ValueError("At least one sample metadata file must be provided via --i-sample-metadata.")

    for metadata_file in i_sample_metadata:
        if not metadata_file.is_file():
            raise FileNotFoundError(f"Sample metadata file not found at: {metadata_file}")

    if p_number_of_features <= 0:
        raise ValueError("--p-number-of-features must be a positive integer.")

    # Ensure the output directory exists
    o_visualization.parent.mkdir(parents=True, exist_ok=True)

    # --- Command Construction ---
    cmd = [
        "qiime", "emperor", "biplot",
        "--i-biplot", str(i_biplot),
        "--o-visualization", str(o_visualization),
        "--p-number-of-features", str(p_number_of_features),
    ]

    for metadata_file in i_sample_metadata:
        cmd.extend(["--i-sample-metadata", str(metadata_file)])

    if p_ignore_missing_samples:
        cmd.append("--p-ignore-missing-samples")
    else:
        # This is the default behavior in QIIME 2, but we add it for clarity
        cmd.append("--p-no-ignore-missing-samples")

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    # --- Subprocess Execution and Error Handling ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("The 'qiime' command was not found. Please ensure QIIME 2 is installed and accessible in your system's PATH.")
    except subprocess.CalledProcessError as e:
        error_message = (
            f"QIIME 2 emperor biplot command failed with exit code {e.returncode}.\n"
            f"Command: {command_str}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )
        logging.error(error_message)
        raise RuntimeError(error_message) from e

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "visualization": str(o_visualization)
        }
    }

if __name__ == '__main__':
    mcp.run()