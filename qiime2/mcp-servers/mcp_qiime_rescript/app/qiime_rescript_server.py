import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastmcp import FastMCP

mcp = FastMCP()
logging.basicConfig(level=logging.INFO)

def _run_command(cmd: List[str], output_files: Dict[str, Path]) -> Dict[str, Any]:
    """Helper function to run a command and return a structured response."""
    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": {k: str(v) for k, v in output_files.items()},
            "return_code": result.returncode,
        }
    except FileNotFoundError:
        logging.error("Error: 'qiime' command not found. Is QIIME 2 installed and in your PATH?")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"stdout: {e.stdout}")
        logging.error(f"stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "Command execution failed.",
            "return_code": e.returncode,
        }

@mcp.tool()
def cull_seqs(
    sequences: Path,
    culled_sequences: Path,
    discarded_sequences: Optional[Path] = None,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    max_ambig: int = 0,
    max_homopol: int = 8,
    num_jobs: int = 1,
    perc_identity: float = 0.9,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Cull sequences by length, ambiguous bases, and homopolymers.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")
    if num_jobs <= 0:
        raise ValueError("Number of jobs must be a positive integer.")
    if not (0.0 <= perc_identity <= 1.0):
        raise ValueError("perc_identity must be between 0.0 and 1.0.")

    cmd = ["qiime", "rescript", "cull-seqs", "--i-sequences", str(sequences), "--o-culled-sequences", str(culled_sequences)]
    
    output_files = {"culled_sequences": culled_sequences}

    if discarded_sequences:
        cmd.extend(["--o-discarded-sequences", str(discarded_sequences)])
        output_files["discarded_sequences"] = discarded_sequences
    if min_len is not None:
        cmd.extend(["--p-min-len", str(min_len)])
    if max_len is not None:
        cmd.extend(["--p-max-len", str(max_len)])
    
    cmd.extend(["--p-max-ambig", str(max_ambig)])
    cmd.extend(["--p-max-homopol", str(max_homopol)])
    cmd.extend(["--p-num-jobs", str(num_jobs)])
    cmd.extend(["--p-perc-identity", str(perc_identity)])

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def degap_seqs(
    sequences: Path,
    degapped_sequences: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Remove gap characters from sequences.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")

    cmd = ["qiime", "rescript", "degap-seqs", "--i-sequences", str(sequences), "--o-degapped-sequences", str(degapped_sequences)]
    output_files = {"degapped_sequences": degapped_sequences}

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def dereplicate(
    sequences: Path,
    taxa: Path,
    dereplicated_sequences: Path,
    dereplicated_taxa: Path,
    mode: str = "uniq",
    perc_identity: float = 1.0,
    threads: int = 1,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Dereplicate sequences and associated taxonomies.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")
    if not taxa.is_file():
        raise FileNotFoundError(f"Input taxonomy file not found: {taxa}")
    if mode not in ["uniq", "lca", "super"]:
        raise ValueError("Mode must be one of 'uniq', 'lca', or 'super'.")
    if not (0.0 <= perc_identity <= 1.0):
        raise ValueError("perc_identity must be between 0.0 and 1.0.")
    if threads <= 0:
        raise ValueError("Number of threads must be a positive integer.")

    cmd = [
        "qiime", "rescript", "dereplicate",
        "--i-sequences", str(sequences),
        "--i-taxa", str(taxa),
        "--o-dereplicated-sequences", str(dereplicated_sequences),
        "--o-dereplicated-taxa", str(dereplicated_taxa),
        "--p-mode", mode,
        "--p-perc-identity", str(perc_identity),
        "--p-threads", str(threads),
    ]
    output_files = {
        "dereplicated_sequences": dereplicated_sequences,
        "dereplicated_taxa": dereplicated_taxa,
    }

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def get_gtdb_data(
    version: str,
    domain: str,
    gtdb_sequences: Path,
    gtdb_taxonomy: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Download GTDB release data files.
    """
    if domain not in ["arc", "bac", "both"]:
        raise ValueError("Domain must be one of 'arc', 'bac', or 'both'.")

    cmd = [
        "qiime", "rescript", "get-gtdb-data",
        "--p-version", version,
        "--p-domain", domain,
        "--o-gtdb-sequences", str(gtdb_sequences),
        "--o-gtdb-taxonomy", str(gtdb_taxonomy),
    ]
    output_files = {
        "gtdb_sequences": gtdb_sequences,
        "gtdb_taxonomy": gtdb_taxonomy,
    }

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def get_ncbi_data(
    query: str,
    sequences: Path,
    taxonomy: Path,
    n_jobs: int = 1,
    chunk_size: int = 200,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Download NCBI data files based on a search query.
    """
    if n_jobs <= 0:
        raise ValueError("Number of jobs must be a positive integer.")
    if chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer.")

    cmd = [
        "qiime", "rescript", "get-ncbi-data",
        "--p-query", query,
        "--o-sequences", str(sequences),
        "--o-taxonomy", str(taxonomy),
        "--p-n-jobs", str(n_jobs),
        "--p-chunk-size", str(chunk_size),
    ]
    output_files = {"sequences": sequences, "taxonomy": taxonomy}

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def get_silva_data(
    version: str,
    target: str,
    silva_sequences: Path,
    silva_taxonomy: Path,
    include_parvo: bool = False,
    n_jobs: int = 1,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Download SILVA release data files.
    """
    if n_jobs <= 0:
        raise ValueError("Number of jobs must be a positive integer.")
    
    cmd = [
        "qiime", "rescript", "get-silva-data",
        "--p-version", version,
        "--p-target", target,
        "--o-silva-sequences", str(silva_sequences),
        "--o-silva-taxonomy", str(silva_taxonomy),
        "--p-n-jobs", str(n_jobs),
    ]
    output_files = {
        "silva_sequences": silva_sequences,
        "silva_taxonomy": silva_taxonomy,
    }

    if include_parvo:
        cmd.append("--p-include-parvo")
    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def merge_taxa(
    taxa: List[Path],
    merged_taxa: Path,
    mode: str = "lca",
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Merge taxonomies via LCA or majority consensus.
    """
    if not taxa:
        raise ValueError("At least one input taxonomy file is required.")
    for tax_file in taxa:
        if not tax_file.is_file():
            raise FileNotFoundError(f"Input taxonomy file not found: {tax_file}")
    if mode not in ["lca", "majority"]:
        raise ValueError("Mode must be one of 'lca' or 'majority'.")

    cmd = ["qiime", "rescript", "merge-taxa", "--o-merged-taxa", str(merged_taxa), "--p-mode", mode]
    for tax_file in taxa:
        cmd.extend(["--i-taxa", str(tax_file)])
    
    output_files = {"merged_taxa": merged_taxa}

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def reverse_transcribe(
    dna_sequences: Path,
    rna_sequences: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Reverse transcribe DNA sequences to RNA sequences.
    """
    if not dna_sequences.is_file():
        raise FileNotFoundError(f"Input DNA sequence file not found: {dna_sequences}")

    cmd = [
        "qiime", "rescript", "reverse-transcribe",
        "--i-dna-sequences", str(dna_sequences),
        "--o-rna-sequences", str(rna_sequences),
    ]
    output_files = {"rna_sequences": rna_sequences}

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def evaluate_classifications(
    expected_taxa: Path,
    observed_taxa: Path,
    evaluation: Path,
    labels: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate taxonomic classification accuracy.
    """
    if not expected_taxa.is_file():
        raise FileNotFoundError(f"Expected taxa file not found: {expected_taxa}")
    if not observed_taxa.is_file():
        raise FileNotFoundError(f"Observed taxa file not found: {observed_taxa}")

    cmd = [
        "qiime", "rescript", "evaluate-classifications",
        "--i-expected-taxa", str(expected_taxa),
        "--i-observed-taxa", str(observed_taxa),
        "--o-evaluation", str(evaluation),
    ]
    output_files = {"evaluation": evaluation}

    if labels:
        for label in labels:
            cmd.extend(["--p-labels", label])

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def evaluate_seqs(
    sequences: Path,
    evaluation: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate sequence quality.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")

    cmd = [
        "qiime", "rescript", "evaluate-seqs",
        "--i-sequences", str(sequences),
        "--o-evaluation", str(evaluation),
    ]
    output_files = {"evaluation": evaluation}

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def filter_seqs_length(
    sequences: Path,
    filtered_sequences: Path,
    discarded_sequences: Optional[Path] = None,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Filter sequences by length.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")

    cmd = [
        "qiime", "rescript", "filter-seqs-length",
        "--i-sequences", str(sequences),
        "--o-filtered-sequences", str(filtered_sequences),
    ]
    output_files = {"filtered_sequences": filtered_sequences}

    if discarded_sequences:
        cmd.extend(["--o-discarded-sequences", str(discarded_sequences)])
        output_files["discarded_sequences"] = discarded_sequences
    if min_len is not None:
        cmd.extend(["--p-min-len", str(min_len)])
    if max_len is not None:
        cmd.extend(["--p-max-len", str(max_len)])

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

@mcp.tool()
def filter_seqs_length_by_taxon(
    sequences: Path,
    taxonomy: Path,
    filtered_sequences: Path,
    discarded_sequences: Optional[Path] = None,
    labels: Optional[List[str]] = None,
    min_len: int = 0,
    max_len: int = 0,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Filter sequences by length and taxonomy.
    """
    if not sequences.is_file():
        raise FileNotFoundError(f"Input sequence file not found: {sequences}")
    if not taxonomy.is_file():
        raise FileNotFoundError(f"Input taxonomy file not found: {taxonomy}")

    cmd = [
        "qiime", "rescript", "filter-seqs-length-by-taxon",
        "--i-sequences", str(sequences),
        "--i-taxonomy", str(taxonomy),
        "--o-filtered-sequences", str(filtered_sequences),
        "--p-min-len", str(min_len),
        "--p-max-len", str(max_len),
    ]
    output_files = {"filtered_sequences": filtered_sequences}

    if discarded_sequences:
        cmd.extend(["--o-discarded-sequences", str(discarded_sequences)])
        output_files["discarded_sequences"] = discarded_sequences
    if labels:
        for label in labels:
            cmd.extend(["--p-labels", label])

    if verbose:
        cmd.append("--verbose")

    return _run_command(cmd, output_files)

if __name__ == '__main__':
    mcp.run()