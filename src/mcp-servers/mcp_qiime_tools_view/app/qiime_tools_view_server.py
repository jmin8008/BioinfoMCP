import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP()


def _run_qiime_command(cmd: List[str]):
    """Helper function to run a QIIME command and handle common errors."""
    command_executed = " ".join(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "command_executed": command_executed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
    except FileNotFoundError:
        raise RuntimeError("QIIME 2 is not installed or not in the system's PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"QIIME 2 command failed with exit code {e.returncode}.\n"
            f"Command: {command_executed}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )


@mcp.tool()
def qiime_tools_cast_metadata(
    column: str,
    metadata_file: Path,
    to_type: str,
    ignore_missing_values: bool = False,
):
    """
    Casts a column of metadata to a new type.

    The new metadata is written to standard output.
    """
    if not metadata_file.exists() or not metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
    if to_type not in ["numeric", "categorical"]:
        raise ValueError("`to_type` must be either 'numeric' or 'categorical'.")

    cmd = [
        "qiime", "tools", "cast-metadata", column,
        "--metadata-file", str(metadata_file),
        "--to-type", to_type,
    ]
    if ignore_missing_values:
        cmd.append("--ignore-missing-values")

    result = _run_qiime_command(cmd)
    result["new_metadata"] = result["stdout"]
    return result


@mcp.tool()
def qiime_tools_citations(
    paths: List[Path],
    verbose: bool = False,
):
    """
    Prints citations for one or more QIIME 2 results.

    Citations are returned in BibTeX format.
    """
    cmd = ["qiime", "tools", "citations"]
    if not paths:
        raise ValueError("At least one input path must be provided.")
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        cmd.append(str(path))

    if verbose:
        cmd.append("--verbose")

    result = _run_qiime_command(cmd)
    result["citations"] = result["stdout"]
    return result


@mcp.tool()
def qiime_tools_export(
    input_path: Path,
    output_path: Path,
):
    """
    Exports a QIIME 2 Artifact or Visualization to a directory.
    """
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input artifact/visualization not found: {input_path}")

    # QIIME will create the output directory, but its parent must exist.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and any(output_path.iterdir()):
        raise ValueError(f"Output directory '{output_path}' already exists and is not empty.")

    cmd = [
        "qiime", "tools", "export",
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]

    result = _run_qiime_command(cmd)
    
    exported_files = [str(f) for f in output_path.rglob('*') if f.is_file()]
    result["output_directory"] = str(output_path)
    result["output_files"] = exported_files
    return result


@mcp.tool()
def qiime_tools_extract(
    input_path: Path,
    output_path: Path,
):
    """
    Extracts a QIIME 2 Artifact or Visualization.

    This is an advanced feature that extracts the raw, untransformed data.
    For most use cases, `qiime_tools_export` is more appropriate.
    """
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input artifact/visualization not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and any(output_path.iterdir()):
        raise ValueError(f"Output directory '{output_path}' already exists and is not empty.")

    cmd = [
        "qiime", "tools", "extract",
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]

    result = _run_qiime_command(cmd)

    extracted_files = [str(f) for f in output_path.rglob('*') if f.is_file()]
    result["output_directory"] = str(output_path)
    result["output_files"] = extracted_files
    return result


@mcp.tool()
def qiime_tools_import(
    artifact_type: str,
    input_path: Path,
    output_path: Path,
    input_format: Optional[str] = None,
):
    """
    Imports data into a new QIIME 2 Artifact.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file or directory not found: {input_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise ValueError(f"Output path '{output_path}' already exists.")

    cmd = [
        "qiime", "tools", "import",
        "--type", artifact_type,
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]
    if input_format:
        cmd.extend(["--input-format", input_format])

    result = _run_qiime_command(cmd)
    result["output_artifact"] = str(output_path)
    return result


@mcp.tool()
def qiime_tools_show_importable_types():
    """Shows the semantic types that can be imported."""
    cmd = ["qiime", "tools", "import", "--show-importable-types"]
    result = _run_qiime_command(cmd)
    result["importable_types"] = result["stdout"].strip().split('\n')
    return result


@mcp.tool()
def qiime_tools_show_importable_formats():
    """Shows the file formats that can be imported."""
    cmd = ["qiime", "tools", "import", "--show-importable-formats"]
    result = _run_qiime_command(cmd)
    result["importable_formats"] = result["stdout"].strip().split('\n')
    return result


@mcp.tool()
def qiime_tools_inspect_metadata(
    paths: List[Path],
    tsv: bool = False,
):
    """
    Inspects columns of one or more metadata files or artifacts.
    """
    cmd = ["qiime", "tools", "inspect-metadata"]
    if not paths:
        raise ValueError("At least one input path must be provided.")
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        cmd.append(str(path))

    if tsv:
        cmd.append("--tsv")

    result = _run_qiime_command(cmd)
    result["metadata_summary"] = result["stdout"]
    return result


@mcp.tool()
def qiime_tools_peek(
    path: Path,
):
    """
    Displays basic information about a QIIME 2 Artifact or Visualization.
    """
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    cmd = ["qiime", "tools", "peek", str(path)]
    result = _run_qiime_command(cmd)
    result["artifact_info"] = result["stdout"]
    return result


@mcp.tool()
def qiime_tools_validate(
    path: Path,
    level: str = "max",
):
    """
    Validates a QIIME 2 result.
    """
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    if level not in ["max", "min"]:
        raise ValueError("`level` must be either 'max' or 'min'.")

    cmd = ["qiime", "tools", "validate", str(path), "--level", level]
    
    # A successful validation returns exit code 0 and prints to stdout.
    # A failed validation returns a non-zero exit code and prints to stderr.
    # The helper function handles this logic.
    result = _run_qiime_command(cmd)
    result["validation_status"] = "Success"
    result["validation_report"] = result["stdout"]
    return result


@mcp.tool()
def qiime_tools_view(
    path: Path,
    index_path: Optional[Path] = None,
):
    """
    Views a QIIME 2 Artifact or Visualization by extracting it to a directory.

    This tool extracts the contents of a QIIME 2 Artifact (.qza) or
    Visualization (.qzv) to a specified directory, making it viewable.
    If no output directory is specified, a temporary one will be created.
    """
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    if index_path is None:
        # Create a directory that persists after the function returns.
        # The MCP environment is responsible for cleanup.
        output_dir = Path(tempfile.mkdtemp(prefix="qiime_view_"))
    else:
        output_dir = index_path
        output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "qiime", "tools", "view",
        str(path),
        "--index-path", str(output_dir),
    ]

    result = _run_qiime_command(cmd)

    output_files_list = [str(f) for f in output_dir.rglob('*') if f.is_file()]
    result["output_directory"] = str(output_dir)
    result["output_files"] = output_files_list
    result["message"] = f"Visualization extracted to {output_dir}. Open 'index.html' in that directory to view."
    return result


if __name__ == '__main__':
    mcp.run()