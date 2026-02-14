from fastmcp import FastMCP
from pathlib import Path
import subprocess
from typing import Optional

mcp = FastMCP()

@mcp.tool()
def vsearch_dereplicate_sequences(
    sequences: Path,
    dereplicated_table: Path,
    dereplicated_sequences: Path,
    derep_prefix: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Dereplicates sequences using the VSEARCH plugin in QIIME 2.

    This method maps each input sequence to a representative sequence and
    creates a feature table indicating the frequency of each input sequence.
    It is a common step in OTU clustering workflows to reduce computational load.

    Args:
        sequences (Path): The QIIME 2 artifact (.qza) containing the sequences to be dereplicated.
                          (QIIME 2 type: FeatureData[Sequence])
        dereplicated_table (Path): The path for the output dereplicated feature table artifact (.qza).
                                   (QIIME 2 type: FeatureTable[Frequency])
        dereplicated_sequences (Path): The path for the output dereplicated sequences artifact (.qza).
                                       (QIIME 2 type: FeatureData[Sequence])
        derep_prefix (bool, optional): If True, sequences that are prefixes of other sequences
                                       will also be dereplicated. Defaults to False, which only
                                       dereplicates identical sequences.
        verbose (bool, optional): If True, display verbose output from the QIIME 2 command.
                                  Defaults to False.

    Returns:
        dict: A dictionary containing the execution command, stdout, stderr, and a
              dictionary of output file paths.
    """
    # --- Input Validation ---
    if not sequences.exists():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")
    
    if dereplicated_table.suffix != ".qza":
        raise ValueError("Output dereplicated_table must have a .qza extension.")

    if dereplicated_sequences.suffix != ".qza":
        raise ValueError("Output dereplicated_sequences must have a .qza extension.")

    # --- Command Construction ---
    cmd = [
        "qiime", "vsearch", "dereplicate-sequences",
        "--i-sequences", str(sequences),
        "--o-dereplicated-table", str(dereplicated_table),
        "--o-dereplicated-sequences", str(dereplicated_sequences),
    ]

    if derep_prefix:
        cmd.append("--p-derep-prefix")
    # The default is --p-no-derep-prefix, so no action is needed for False.

    if verbose:
        cmd.append("--verbose")

    command_str = " ".join(cmd)

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
        
        output_files = {
            "dereplicated_table": str(dereplicated_table),
            "dereplicated_sequences": str(dereplicated_sequences),
        }

    except subprocess.CalledProcessError as e:
        # Return a structured error if the command fails
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "output_files": {}
        }

    # --- Structured Result Return ---
    return {
        "command_executed": command_str,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": output_files,
    }

if __name__ == '__main__':
    mcp.run()