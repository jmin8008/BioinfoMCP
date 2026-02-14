from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional

mcp = FastMCP()

@mcp.tool()
def peek(
    artifact: Path
):
    """
    Peeks at a QIIME 2 artifact (.qza) or visualization (.qzv) to view its UUID and type.

    This utility inspects a QIIME 2 artifact file to provide basic metadata about it,
    which is useful for provenance tracking and understanding the data type within a workflow.

    Args:
        artifact: The path to the QIIME 2 artifact or visualization file (.qza or .qzv).
    """
    # 1. Input validation
    if not artifact.is_file():
        raise FileNotFoundError(f"Input artifact file not found at: {artifact}")

    # 2. Command construction
    cmd = [
        "qiime",
        "tools",
        "peek",
        str(artifact)
    ]
    command_executed = " ".join(cmd)

    # 3. Subprocess execution and error handling
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
        # This error is caught if the 'qiime' command itself is not found
        return {
            "command_executed": command_executed,
            "stdout": "",
            "stderr": "Error: 'qiime' command not found. Make sure QIIME 2 is installed and accessible in the system's PATH.",
            "output_files": []
        }
    except subprocess.CalledProcessError as e:
        # This error is caught for non-zero exit codes from the tool
        return {
            "command_executed": command_executed,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "output_files": []
        }

    # 4. Structured result return
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [] # This tool does not generate output files
    }

if __name__ == '__main__':
    mcp.run()