import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def beta_rarefaction(
    i_table: Path,
    p_metric: Literal[
        "braycurtis", "jaccard", "weighted_unifrac", "unweighted_unifrac"
    ],
    p_clustering_method: Literal["nj", "upgma"],
    p_sampling_depth: int,
    m_metadata_file: Path,
    output_dir: Path,
    i_phylogeny: Optional[Path] = None,
    p_iterations: int = 10,
    p_correlation_method: Literal["spearman", "pearson"] = "spearman",
    p_random_seed: Optional[int] = None,
):
    """
    Generate a beta diversity rarefaction plot to assess stability.

    This action rarefies a feature table multiple times at a given sampling depth,
    calculates a beta diversity metric, and produces a PCoA plot where the points
    are colored by sample metadata. The variability in PCoA results across rarefaction
    trials is visualized using ellipsoids.
    """
    # --- Input Validation ---
    if not i_table.is_file():
        raise FileNotFoundError(f"Input feature table not found: {i_table}")
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
    if p_sampling_depth <= 0:
        raise ValueError("p_sampling_depth must be a positive integer.")
    if p_iterations <= 0:
        raise ValueError("p_iterations must be a positive integer.")

    phylogenetic_metrics = ["weighted_unifrac", "unweighted_unifrac"]
    if p_metric in phylogenetic_metrics:
        if i_phylogeny is None:
            raise ValueError(
                f"A phylogenetic tree (--i-phylogeny) is required for the '{p_metric}' metric."
            )
        if not i_phylogeny.is_file():
            raise FileNotFoundError(f"Phylogeny file not found: {i_phylogeny}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_visualization_path = output_dir / f"{p_metric}_rarefaction.qzv"

    # --- Command Construction ---
    cmd = [
        "qiime",
        "diversity",
        "beta-rarefaction",
        "--i-table",
        str(i_table),
        "--p-metric",
        p_metric,
        "--p-clustering-method",
        p_clustering_method,
        "--p-sampling-depth",
        str(p_sampling_depth),
        "--m-metadata-file",
        str(m_metadata_file),
        "--o-visualization",
        str(output_visualization_path),
        "--p-iterations",
        str(p_iterations),
        "--p-correlation-method",
        p_correlation_method,
    ]

    if i_phylogeny:
        cmd.extend(["--i-phylogeny", str(i_phylogeny)])
    if p_random_seed is not None:
        cmd.extend(["--p-random-seed", str(p_random_seed)])

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed.",
        }

    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(output_visualization_path)],
    }


@mcp.tool()
def beta_group_significance(
    i_distance_matrix: Path,
    m_metadata_file: Path,
    m_metadata_column: str,
    output_dir: Path,
    p_method: Literal["permanova", "permdisp", "anosim"] = "permanova",
    p_permutations: int = 999,
    p_pairwise: bool = False,
    p_where: Optional[str] = None,
):
    """
    Test for significant differences in beta diversity between sample groups.

    This tool uses permutation-based statistical tests like PERMANOVA, ANOSIM,
    or PERMDISP to determine if microbial community structures differ
    significantly across categories defined in a metadata column.
    """
    # --- Input Validation ---
    if not i_distance_matrix.is_file():
        raise FileNotFoundError(
            f"Input distance matrix not found: {i_distance_matrix}"
        )
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
    if p_permutations <= 0:
        raise ValueError("p_permutations must be a positive integer.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_visualization_path = (
        output_dir / f"{m_metadata_column}_{p_method}_results.qzv"
    )

    # --- Command Construction ---
    cmd = [
        "qiime",
        "diversity",
        "beta-group-significance",
        "--i-distance-matrix",
        str(i_distance_matrix),
        "--m-metadata-file",
        str(m_metadata_file),
        "--m-metadata-column",
        m_metadata_column,
        "--o-visualization",
        str(output_visualization_path),
        "--p-method",
        p_method,
        "--p-permutations",
        str(p_permutations),
    ]

    if p_pairwise:
        cmd.append("--p-pairwise")
    if p_where:
        cmd.extend(["--p-where", p_where])

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed.",
        }

    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(output_visualization_path)],
    }


@mcp.tool()
def umap(
    i_distance_matrix: Path,
    output_dir: Path,
    p_n_components: int = 2,
    p_random_state: Optional[int] = None,
):
    """
    Perform Uniform Manifold Approximation and Projection (UMAP) on a distance matrix.

    UMAP is a non-linear dimensionality reduction technique that can be used for
    visualizing and exploring high-dimensional data, such as beta diversity distance matrices.
    """
    # --- Input Validation ---
    if not i_distance_matrix.is_file():
        raise FileNotFoundError(
            f"Input distance matrix not found: {i_distance_matrix}"
        )
    if p_n_components <= 0:
        raise ValueError("p_n_components must be a positive integer.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_umap_path = output_dir / "umap_ordination.qza"

    # --- Command Construction ---
    cmd = [
        "qiime",
        "diversity",
        "umap",
        "--i-distance-matrix",
        str(i_distance_matrix),
        "--o-umap",
        str(output_umap_path),
        "--p-n-components",
        str(p_n_components),
    ]

    if p_random_state is not None:
        cmd.extend(["--p-random-state", str(p_random_state)])

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed.",
        }

    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(output_umap_path)],
    }


@mcp.tool()
def adonis(
    i_distance_matrix: Path,
    m_metadata_file: Path,
    p_formula: str,
    output_dir: Path,
    p_permutations: int = 999,
    p_n_jobs: int = 1,
    p_random_state: Optional[int] = None,
):
    """
    Perform Adonis (PERMANOVA) statistical test on a distance matrix.

    This function is used for partitioning a distance matrix among sources of variation,
    fitting linear models to distance matrices. It is useful for analyzing complex
    experimental designs with multiple factors.
    """
    # --- Input Validation ---
    if not i_distance_matrix.is_file():
        raise FileNotFoundError(
            f"Input distance matrix not found: {i_distance_matrix}"
        )
    if not m_metadata_file.is_file():
        raise FileNotFoundError(f"Metadata file not found: {m_metadata_file}")
    if p_permutations <= 0:
        raise ValueError("p_permutations must be a positive integer.")
    if p_n_jobs <= 0:
        raise ValueError("p_n_jobs must be a positive integer.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_visualization_path = output_dir / "adonis_results.qzv"

    # --- Command Construction ---
    cmd = [
        "qiime",
        "diversity",
        "adonis",
        "--i-distance-matrix",
        str(i_distance_matrix),
        "--m-metadata-file",
        str(m_metadata_file),
        "--p-formula",
        p_formula,
        "--o-visualization",
        str(output_visualization_path),
        "--p-permutations",
        str(p_permutations),
        "--p-n-jobs",
        str(p_n_jobs),
    ]

    if p_random_state is not None:
        cmd.extend(["--p-random-state", str(p_random_state)])

    # --- Subprocess Execution ---
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error": "QIIME 2 command failed.",
        }

    return {
        "command_executed": " ".join(cmd),
        "stdout": stdout,
        "stderr": stderr,
        "output_files": [str(output_visualization_path)],
    }


if __name__ == "__main__":
    mcp.run()