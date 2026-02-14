import subprocess
import tempfile
from pathlib import Path
from typing import List, Literal, Optional

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def alpha(
    table: Path,
    metric: Literal[
        "ace",
        "chao1",
        "chao1_ci",
        "berger_parker_d",
        "brillouin_d",
        "dominance",
        "doubles",
        "enspie",
        "esty_ci",
        "faith_pd",
        "fisher_alpha",
        "gini_index",
        "goods_coverage",
        "heip_e",
        "kempton_taylor_q",
        "margalef",
        "mcintosh_d",
        "mcintosh_e",
        "menhinick",
        "michaelis_menten_fit",
        "observed_features",
        "osd",
        "pielou_e",
        "robbins",
        "shannon",
        "simpson",
        "simpson_e",
        "singles",
        "strong",
    ],
    output_diversity: Path,
    phylogeny: Optional[Path] = None,
):
    """Computes a user-specified alpha diversity metric for all samples in a feature table.

    This action calculates alpha diversity for each sample in the feature table,
    producing a QIIME 2 artifact containing the results. For phylogenetic metrics
    like Faith's PD, a phylogenetic tree must be provided.

    Args:
        table: The feature table containing the samples over which alpha diversity should be computed. (QIIME 2 artifact: FeatureTable[Frequency])
        metric: The alpha diversity metric to be computed.
        output_diversity: The path where the resulting alpha diversity vector artifact (.qza) will be written.
        phylogeny: The phylogenetic tree containing tip identifiers that correspond to the feature identifiers in the table. Required for phylogenetic metrics. (QIIME 2 artifact: Phylogeny[Rooted])
    """
    # Input validation
    if not table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {table}")
    if metric == "faith_pd":
        if not phylogeny:
            raise ValueError("A phylogenetic tree must be provided for the 'faith_pd' metric.")
        if not phylogeny.is_file():
            raise FileNotFoundError(f"Phylogenetic tree not found at: {phylogeny}")

    # Command construction
    cmd = [
        "qiime",
        "diversity",
        "alpha",
        "--i-table",
        str(table),
        "--p-metric",
        metric,
        "--o-alpha-diversity",
        str(output_diversity),
    ]

    if phylogeny:
        cmd.extend(["--i-phylogeny", str(phylogeny)])

    # Subprocess execution
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "output_files": [str(output_diversity)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 diversity alpha command failed.",
            "return_code": e.returncode,
        }


@mcp.tool()
def alpha_rarefaction(
    table: Path,
    metadata: Path,
    max_depth: int,
    output_visualization: Path,
    phylogeny: Optional[Path] = None,
    min_depth: int = 1,
    steps: int = 10,
    iterations: int = 10,
):
    """Generates alpha rarefaction plots.

    This visualizer computes alpha diversity metrics at multiple rarefaction depths
    and plots the results. The visualization allows for interactive exploration of
    how alpha diversity changes with sequencing depth across different sample metadata categories.

    Args:
        table: The feature table to rarefy. (QIIME 2 artifact: FeatureTable[Frequency])
        metadata: The sample metadata file.
        max_depth: The maximum rarefaction depth. Samples with fewer sequences will be excluded.
        output_visualization: The path where the output visualization file (.qzv) will be written.
        phylogeny: The phylogenetic tree for phylogenetic metrics. (QIIME 2 artifact: Phylogeny[Rooted])
        min_depth: The minimum rarefaction depth. Defaults to 1.
        steps: The number of rarefaction depths to include between min_depth and max_depth. Defaults to 10.
        iterations: The number of rarefied tables to compute at each depth. Defaults to 10.
    """
    # Input validation
    if not table.is_file():
        raise FileNotFoundError(f"Input feature table not found at: {table}")
    if not metadata.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata}")
    if phylogeny and not phylogeny.is_file():
        raise FileNotFoundError(f"Phylogenetic tree not found at: {phylogeny}")
    if max_depth <= 0:
        raise ValueError("max_depth must be a positive integer.")
    if min_depth < 1:
        raise ValueError("min_depth must be at least 1.")
    if max_depth < min_depth:
        raise ValueError("max_depth must be greater than or equal to min_depth.")

    # Command construction
    cmd = [
        "qiime",
        "diversity",
        "alpha-rarefaction",
        "--i-table",
        str(table),
        "--m-metadata-file",
        str(metadata),
        "--p-max-depth",
        str(max_depth),
        "--p-min-depth",
        str(min_depth),
        "--p-steps",
        str(steps),
        "--p-iterations",
        str(iterations),
        "--o-visualization",
        str(output_visualization),
    ]

    if phylogeny:
        cmd.extend(["--i-phylogeny", str(phylogeny)])

    # Subprocess execution
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "output_files": [str(output_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 alpha-rarefaction command failed.",
            "return_code": e.returncode,
        }


@mcp.tool()
def alpha_group_significance(
    alpha_diversity: Path,
    metadata: Path,
    output_visualization: Path,
):
    """Tests for significant differences in alpha diversity between sample groups.

    This visualizer uses a Kruskal-Wallis test to determine if there are significant
    differences in alpha diversity among groups defined by a metadata column.
    Pairwise tests are also performed.

    Args:
        alpha_diversity: Vector of alpha diversity values by sample. (QIIME 2 artifact: SampleData[AlphaDiversity])
        metadata: The sample metadata file containing the grouping column.
        output_visualization: The path where the output visualization file (.qzv) will be written.
    """
    # Input validation
    if not alpha_diversity.is_file():
        raise FileNotFoundError(f"Alpha diversity artifact not found at: {alpha_diversity}")
    if not metadata.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata}")

    # Command construction
    cmd = [
        "qiime",
        "diversity",
        "alpha-group-significance",
        "--i-alpha-diversity",
        str(alpha_diversity),
        "--m-metadata-file",
        str(metadata),
        "--o-visualization",
        str(output_visualization),
    ]

    # Subprocess execution
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "output_files": [str(output_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 alpha-group-significance command failed.",
            "return_code": e.returncode,
        }


@mcp.tool()
def alpha_correlation(
    alpha_diversity: Path,
    metadata: Path,
    output_visualization: Path,
    method: Literal["spearman", "pearson"] = "spearman",
):
    """Determines if a correlation exists between alpha diversity and a continuous metadata variable.

    This visualizer uses Spearman or Pearson correlation to test for a monotonic
    relationship between an alpha diversity metric and a numeric metadata column.

    Args:
        alpha_diversity: Vector of alpha diversity values by sample. (QIIME 2 artifact: SampleData[AlphaDiversity])
        metadata: The sample metadata file containing the continuous variable.
        output_visualization: The path where the output visualization file (.qzv) will be written.
        method: The correlation method to use. Defaults to 'spearman'.
    """
    # Input validation
    if not alpha_diversity.is_file():
        raise FileNotFoundError(f"Alpha diversity artifact not found at: {alpha_diversity}")
    if not metadata.is_file():
        raise FileNotFoundError(f"Metadata file not found at: {metadata}")

    # Command construction
    cmd = [
        "qiime",
        "diversity",
        "alpha-correlation",
        "--i-alpha-diversity",
        str(alpha_diversity),
        "--m-metadata-file",
        str(metadata),
        "--p-method",
        method,
        "--o-visualization",
        str(output_visualization),
    ]

    # Subprocess execution
    try:
        process = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        return {
            "command_executed": " ".join(cmd),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "output_files": [str(output_visualization)],
        }
    except subprocess.CalledProcessError as e:
        return {
            "command_executed": " ".join(cmd),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "error": "QIIME 2 alpha-correlation command failed.",
            "return_code": e.returncode,
        }


if __name__ == "__main__":
    mcp.run()