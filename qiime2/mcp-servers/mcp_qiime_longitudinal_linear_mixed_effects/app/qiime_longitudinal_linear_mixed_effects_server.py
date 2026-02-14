import subprocess
from pathlib import Path
from typing import List, Optional, Dict
import logging

from fastmcp import FastMCP

mcp = FastMCP()

logging.basicConfig(level=logging.INFO)

@mcp.tool()
def linear_mixed_effects(
    m_metadata_file: List[Path],
    p_metric: str,
    o_visualization: Path,
    i_table: Optional[Path] = None,
    p_state_column: Optional[str] = None,
    p_individual_id_column: Optional[str] = None,
    p_group_columns: Optional[List[str]] = None,
    p_random_effects: Optional[List[str]] = None,
    p_formula: Optional[str] = None,
    p_lowess: bool = False,
    p_random_seed: Optional[int] = None,
    verbose: bool = False,
) -> Dict:
    """
    Fits a linear mixed effects model and computes tests for significance.

    This method can be used to determine the influence of metadata factors on a
    continuous dependent variable, e.g., alpha diversity. This method is a
    wrapper for the statsmodels LMER implementation.
    """
    # --- Input Validation ---
    if not m_metadata_file:
        raise ValueError("At least one metadata file must be provided via m_metadata_file.")
    for file_path in m_metadata_file:
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")

    if i_table and not i_table.exists():
        raise FileNotFoundError(f"Input table not found: {i_table}")

    if p_formula is None:
        if p_state_column is None:
            raise ValueError("p_state_column is required when p_formula is not provided.")
        if p_individual_id_column is None:
            raise ValueError("p_individual_id_column is required when p_formula is not provided.")
    
    if o_visualization.parent and not o_visualization.parent.exists():
        try:
            o_visualization.parent.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created output directory: {o_visualization.parent}")
        except OSError as e:
            raise OSError(f"Could not create output directory {o_visualization.parent}: {e}")


    # --- Command Construction ---
    cmd = ["qiime", "longitudinal", "linear-mixed-effects"]

    if i_table:
        cmd.extend(["--i-table", str(i_table)])

    for metadata_path in m_metadata_file:
        cmd.extend(["--m-metadata-file", str(metadata_path)])

    cmd.extend(["--p-metric", p_metric])

    if p_formula:
        cmd.extend(["--p-formula", p_formula])
    else:
        # These are validated to exist if p_formula is None
        cmd.extend(["--p-state-column", p_state_column])
        cmd.extend(["--p-individual-id-column", p_individual_id_column])

        if p_group_columns:
            for col in p_group_columns:
                cmd.extend(["--p-group-columns", col])
        
        if p_random_effects:
            for effect in p_random_effects:
                cmd.extend(["--p-random-effects", effect])

    if p_lowess:
        cmd.append("--p-lowess")
    # Note: The default is --p-no-lowess (False), so we only need to add the flag if True.

    if p_random_seed is not None:
        cmd.extend(["--p-random-seed", str(p_random_seed)])

    cmd.extend(["--o-visualization", str(o_visualization)])

    if verbose:
        cmd.append("--verbose")

    # --- Subprocess Execution ---
    command_str = " ".join(cmd)
    logging.info(f"Executing command: {command_str}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        
        output_files = {"visualization": str(o_visualization)}

        return {
            "command_executed": command_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files,
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"QIIME 2 command failed with exit code {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return {
            "command_executed": command_str,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 command failed.",
            "return_code": e.returncode,
        }
    except FileNotFoundError:
        raise RuntimeError("qiime command not found. Please ensure QIIME 2 is installed and in your PATH.")


if __name__ == '__main__':
    mcp.run()