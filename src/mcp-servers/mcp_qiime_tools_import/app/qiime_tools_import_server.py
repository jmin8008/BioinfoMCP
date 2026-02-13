import subprocess
from pathlib import Path
from typing import Optional, Dict, List

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def tools_import(
    semantic_type: str,
    input_path: Path,
    output_path: Path,
    input_format: Optional[str] = None,
) -> Dict:
    """
    Import data into a QIIME 2 Artifact.

    This tool is a wrapper for the 'qiime tools import' command. It allows
    importing various data formats into a .qza file, which is the standard
    QIIME 2 artifact format.

    For more details, see https://docs.qiime2.org/2024.2/tutorials/importing/

    Args:
        semantic_type: The semantic type of the artifact that will be created.
        input_path: Path to the file or directory that should be imported.
        output_path: Path where the new artifact (.qza) should be written.
        input_format: The format of the data to be imported. If not provided,
                      QIIME 2 will attempt to automatically infer the format.
    
    Returns:
        A dictionary containing the command executed, stdout, stderr, and a
        dictionary of output files.
    """
    # 1. Input Validation
    if not semantic_type:
        raise ValueError("The 'semantic_type' parameter cannot be empty.")

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    # Ensure the output directory exists before running the command
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Command Construction
    cmd: List[str] = [
        "qiime", "tools", "import",
        "--type", semantic_type,
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]

    if input_format:
        cmd.extend(["--input-format", input_format])

    command_executed = " ".join(cmd)

    # 3. Subprocess Execution and Error Handling
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "The 'qiime' command was not found. Please ensure QIIME 2 is "
            "installed and the conda environment is activated."
        )
    except subprocess.CalledProcessError as e:
        error_message = (
            f"QIIME 2 tools import failed with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        )
        raise RuntimeError(error_message) from e

    # 4. Structured Result Return
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": {
            "output_artifact": str(output_path)
        }
    }


@mcp.tool()
def tools_show_importable_types() -> Dict:
    """
    Show the semantic types that can be imported into QIIME 2.

    This corresponds to the '--show-importable-types' flag in 'qiime tools import'.
    The output will be a list of all available semantic types that can be used
    with the 'semantic_type' parameter in the tools_import function.
    
    Returns:
        A dictionary containing the command executed, stdout, and stderr.
    """
    # 1. Command Construction
    cmd = ["qiime", "tools", "import", "--show-importable-types"]
    command_executed = " ".join(cmd)

    # 2. Subprocess Execution and Error Handling
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "The 'qiime' command was not found. Please ensure QIIME 2 is "
            "installed and the conda environment is activated."
        )
    except subprocess.CalledProcessError as e:
        error_message = (
            f"Failed to show importable types with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        )
        raise RuntimeError(error_message) from e

    # 3. Structured Result Return
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@mcp.tool()
def tools_show_importable_formats() -> Dict:
    """
    Show the file and directory formats that can be imported into QIIME 2.

    This corresponds to the '--show-importable-formats' flag in 'qiime tools import'.
    The output will be a list of all available formats that can be used with the
    'input_format' parameter in the tools_import function.
    
    Returns:
        A dictionary containing the command executed, stdout, and stderr.
    """
    # 1. Command Construction
    cmd = ["qiime", "tools", "import", "--show-importable-formats"]
    command_executed = " ".join(cmd)

    # 2. Subprocess Execution and Error Handling
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "The 'qiime' command was not found. Please ensure QIIME 2 is "
            "installed and the conda environment is activated."
        )
    except subprocess.CalledProcessError as e:
        error_message = (
            f"Failed to show importable formats with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        )
        raise RuntimeError(error_message) from e

    # 3. Structured Result Return
    return {
        "command_executed": command_executed,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


if __name__ == '__main__':
    mcp.run()