from fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional, List
import logging

# Initialize the MCP server and logging
mcp = FastMCP()
logging.basicConfig(level=logging.INFO)


@mcp.tool()
def tools_import(
    type: str,
    input_path: Path,
    output_path: Path,
    input_format: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """
    Import data from a standard file format into a new QIIME 2 Artifact.

    Args:
        type: The semantic type of the artifact to create (e.g., 'SampleData[PairedEndSequencesWithQuality]').
        input_path: Path to the file or directory to import.
        output_path: Path where the output QIIME 2 Artifact (.qza) should be written.
        input_format: The format of the data to be imported (e.g., 'CasavaOneEightSingleLanePerSampleDirFmt').
        verbose: Display verbose command-line output.
    """
    # Input validation
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    if output_path.exists():
        logging.warning(f"Output path {output_path} already exists and will be overwritten.")

    # Command construction
    cmd = [
        "qiime", "tools", "import",
        "--type", type,
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]
    if input_format:
        cmd.extend(["--input-format", input_format])
    if verbose:
        cmd.append("--verbose")

    # Subprocess execution
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(output_path)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def tools_export(
    input_path: Path,
    output_path: Path,
    verbose: bool = False,
) -> dict:
    """
    Export (extract) data from a QIIME 2 Artifact or Visualization.

    Args:
        input_path: Path to the QIIME 2 Artifact (.qza) or Visualization (.qzv) to export.
        output_path: Path to the directory where data should be exported.
        verbose: Display verbose command-line output.
    """
    # Input validation
    if not input_path.exists():
        raise FileNotFoundError(f"Input artifact does not exist: {input_path}")
    if not input_path.name.endswith(('.qza', '.qzv')):
        logging.warning(f"Input file {input_path} does not have a typical QIIME 2 extension (.qza, .qzv).")

    # Command construction
    cmd = [
        "qiime", "tools", "export",
        "--input-path", str(input_path),
        "--output-path", str(output_path),
    ]
    if verbose:
        cmd.append("--verbose")

    # Subprocess execution
    try:
        # The output path is a directory, so we ensure it exists.
        output_path.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        # List files in the output directory to report what was created
        exported_files = [str(p) for p in output_path.rglob('*') if p.is_file()]

        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": exported_files,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def feature_classifier_extract_reads(
    sequences: Path,
    f_primer: str,
    r_primer: str,
    reads: Path,
    trunc_len: int = 0,
    trim_left: int = 0,
    min_length: int = 0,
    max_length: int = 0,
    identity: float = 0.8,
    n_jobs: int = 1,
    read_orientation: str = 'forward',
    verbose: bool = False,
) -> dict:
    """
    Extract reads from reference sequences based on primer pairs.

    Args:
        sequences: The sequences from which reads should be extracted (FeatureData[Sequence] artifact).
        f_primer: Forward primer sequence.
        r_primer: Reverse primer sequence.
        reads: The output artifact for the extracted reads (FeatureData[Sequence]).
        trunc_len: Truncate reads at this length. Reads shorter are discarded. 0 means no truncation.
        trim_left: Number of bases to trim from 5' end.
        min_length: Minimum amplicon length. Shorter amplicons are discarded.
        max_length: Maximum amplicon length. Longer amplicons are discarded. 0 means no maximum.
        identity: Minimum sequence identity threshold (0.0 to 1.0).
        n_jobs: Number of jobs to run in parallel.
        read_orientation: Read orientation ('forward', 'reverse-complement', 'both').
        verbose: Display verbose command-line output.
    """
    # Input validation
    if not sequences.exists():
        raise FileNotFoundError(f"Input sequences artifact does not exist: {sequences}")
    if reads.exists():
        logging.warning(f"Output path {reads} already exists and will be overwritten.")
    if not (0.0 <= identity <= 1.0):
        raise ValueError("Identity must be between 0.0 and 1.0.")
    if n_jobs < 1:
        raise ValueError("n_jobs must be at least 1.")
    allowed_orientations = ['forward', 'reverse-complement', 'both']
    if read_orientation not in allowed_orientations:
        raise ValueError(f"read_orientation must be one of {allowed_orientations}")

    # Command construction
    cmd = [
        "qiime", "feature-classifier", "extract-reads",
        "--i-sequences", str(sequences),
        "--p-f-primer", f_primer,
        "--p-r-primer", r_primer,
        "--o-reads", str(reads),
        "--p-trunc-len", str(trunc_len),
        "--p-trim-left", str(trim_left),
        "--p-min-length", str(min_length),
        "--p-max-length", str(max_length),
        "--p-identity", str(identity),
        "--p-n-jobs", str(n_jobs),
        "--p-read-orientation", read_orientation,
    ]
    if verbose:
        cmd.append("--verbose")

    # Subprocess execution
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": [str(reads)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def tools_show_importable_types() -> dict:
    """
    Show the semantic types that can be imported into QIIME 2.
    """
    cmd = ["qiime", "tools", "import", "--show-importable-types"]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


@mcp.tool()
def tools_show_importable_formats() -> dict:
    """
    Show the file formats that can be imported into QIIME 2.
    """
    cmd = ["qiime", "tools", "import", "--show-importable-formats"]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "error": "QIIME 2 command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
        }


if __name__ == '__main__':
    mcp.run()