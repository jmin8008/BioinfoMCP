import subprocess
import logging
from pathlib import Path
from typing import Literal, Optional, List

from fastmcp import FastMCP

mcp = FastMCP()

logging.basicConfig(level=logging.INFO)

@mcp.tool()
def picrust2_full_pipeline(
    table: Path,
    seq: Path,
    pathway_abundance: Path,
    ec_abundance: Optional[Path] = None,
    ko_abundance: Optional[Path] = None,
    out_trait_table: Optional[Path] = None,
    threads: int = 1,
    placement_tool: Literal['sepp', 'epa-ng', 'apples'] = 'sepp',
    hsp_method: Literal['pic', 'scp', 'mp'] = 'mp',
    max_nsti: float = 2.0,
    no_stratified: bool = False,
    bypass_map: bool = False,
    min_reads: int = 1,
    min_samples: int = 1,
    verbose: bool = False,
):
    """
    Runs the full PICRUSt2 pipeline for functional prediction from 16S rRNA data.

    This pipeline includes sequence placement, hidden-state prediction of genomes,
    metagenome prediction, and pathway-level inference.
    """
    # --- Input Validation ---
    if not table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {table}")
    if not seq.is_file():
        raise FileNotFoundError(f"Input sequence file not found at: {seq}")

    if threads < 1:
        raise ValueError("threads must be a positive integer.")
    if max_nsti < 0:
        raise ValueError("max_nsti must be a non-negative float.")
    if min_reads < 0:
        raise ValueError("min_reads must be a non-negative integer.")
    if min_samples < 0:
        raise ValueError("min_samples must be a non-negative integer.")

    output_files: List[Path] = [pathway_abundance]
    if ec_abundance:
        output_files.append(ec_abundance)
    if ko_abundance:
        output_files.append(ko_abundance)
    if out_trait_table:
        output_files.append(out_trait_table)

    for output_path in output_files:
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created output directory: {output_path.parent}")

    # --- Command Construction ---
    cmd = [
        "qiime", "picrust2", "full-pipeline",
        "--i-table", str(table),
        "--i-seq", str(seq),
        "--p-threads", str(threads),
        "--p-placement-tool", placement_tool,
        "--p-hsp-method", hsp_method,
        "--p-max-nsti", str(max_nsti),
        "--p-min-reads", str(min_reads),
        "--p-min-samples", str(min_samples),
        "--o-pathway-abundance", str(pathway_abundance),
    ]

    if ec_abundance:
        cmd.extend(["--o-ec-abundance", str(ec_abundance)])
    if ko_abundance:
        cmd.extend(["--o-ko-abundance", str(ko_abundance)])
    if out_trait_table:
        cmd.extend(["--o-out-trait-table", str(out_trait_table)])

    if no_stratified:
        cmd.append("--p-no-stratified")
    if bypass_map:
        cmd.append("--p-bypass-map")
    if verbose:
        cmd.append("--verbose")

    command_executed = " ".join(cmd)
    logging.info(f"Executing command: {command_executed}")

    # --- Subprocess Execution ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        stderr = result.stderr
        logging.info("PICRUSt2 pipeline completed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing PICRUSt2 pipeline. Return code: {e.returncode}")
        logging.error(f"stdout: {e.stdout}")
        logging.error(f"stderr: {e.stderr}")
        raise e

    # --- Structured Result Return ---
    return {
        "command_executed": command_executed,
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(p) for p in output_files if p.exists()],
    }


if __name__ == '__main__':
    mcp.run()