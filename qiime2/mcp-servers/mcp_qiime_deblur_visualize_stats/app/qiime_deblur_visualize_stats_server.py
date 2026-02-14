import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def visualize_deblur_stats(
    deblur_stats: Path,
    dist: bool = False,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Generate a visualization of summary statistics from a Deblur run.

    This tool visualizes Deblur statistics, providing insights into the denoising
    process, such as the number of reads filtered at each step.

    Args:
        deblur_stats (Path): The DeblurStats artifact (.qza) produced by the
                             deblur denoise-* methods.
        dist (bool): If True, create an interactive distance plot.
                     Defaults to False, which corresponds to the QIIME 2
                     default of --p-no-dist.
        verbose (bool): If True, print verbose output to stdout and/or stderr.
        quiet (bool): If True, suppress all output to stdout and/or stderr.

    Returns:
        dict: A dictionary containing the executed command, stdout, stderr,
              and the path to the output visualization file.
    """
    # --- Input Validation ---
    if not deblur_stats.is_file():
        raise FileNotFoundError(f"Input Deblur stats file not found: {deblur_stats}")

    if quiet and verbose:
        raise ValueError("Cannot set both 'quiet' and 'verbose' to True.")

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        output_visualization = temp_dir / "deblur-stats-summary.qzv"

        # --- Command Construction ---
        cmd = [
            "qiime", "deblur", "visualize-stats",
            "--i-deblur-stats", str(deblur_stats),
            "--o-visualization", str(output_visualization),
        ]

        if dist:
            cmd.append("--p-dist")
        else:
            # This is the default behavior in QIIME 2
            cmd.append("--p-no-dist")

        if verbose:
            cmd.append("--verbose")
        if quiet:
            cmd.append("--quiet")

        command_executed = " ".join(cmd)

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
        except FileNotFoundError:
            return {
                "error": "QIIME 2 is not installed or not in the system's PATH.",
                "command_executed": command_executed,
            }
        except subprocess.CalledProcessError as e:
            return {
                "error": "QIIME 2 command failed.",
                "command_executed": command_executed,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode,
            }

        # --- Return Structured Output ---
        return {
            "command_executed": command_executed,
            "stdout": stdout,
            "stderr": stderr,
            "output_files": {
                "visualization": str(output_visualization)
            }
        }


if __name__ == '__main__':
    mcp.run()