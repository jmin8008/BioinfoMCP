#!/bin/bash

echo "Starting QIIME 2 Skills Generation..."

# ==========================================
# 1. Core Framework
# ==========================================
echo "Processing: Core Framework..."
python -m main --name "qiime_tools_import" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_export" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_extract" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_view" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_peek" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_inspect_metadata" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_cast_metadata" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_citations" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_tools_validate" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 2. Demux & QC
# ==========================================
echo "Processing: Demux & QC..."
python -m main --name "qiime_demux_emp_single" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_demux_emp_paired" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_demux_summarize" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_demux_filter_samples" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_cutadapt_trim_single" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_cutadapt_trim_paired" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_cutadapt_demux_single" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_cutadapt_demux_paired" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_quality_filter_q_score" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 3. Denoising
# ==========================================
echo "Processing: Denoising..."
python -m main --name "qiime_dada2_denoise_single" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_dada2_denoise_paired" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_dada2_denoise_pyro" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_deblur_denoise_16S" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_deblur_denoise_other" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_deblur_visualize_stats" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_vsearch_cluster_features_de_novo" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_vsearch_cluster_features_closed_reference" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_vsearch_cluster_features_open_reference" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_vsearch_dereplicate_sequences" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 4. Phylogeny
# ==========================================
echo "Processing: Phylogeny..."
python -m main --name "qiime_alignment_mafft" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_alignment_mask" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_phylogeny_fasttree" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_phylogeny_raxml" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_phylogeny_iqtree" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_phylogeny_midpoint_root" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_fragment_insertion_sepp" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 5. Taxonomy
# ==========================================
echo "Processing: Taxonomy..."
python -m main --name "qiime_feature_classifier_classify_sklearn" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_classifier_classify_consensus_blast" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_classifier_classify_consensus_vsearch" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_classifier_fit_classifier_naive_bayes" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_taxa_barplot" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_taxa_filter_table" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_taxa_filter_seqs" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_taxa_collapse" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 6. Diversity
# ==========================================
echo "Processing: Diversity..."
python -m main --name "qiime_diversity_alpha" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_beta" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_alpha_phylogenetic" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_beta_phylogenetic" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_core_metrics_phylogenetic" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_lib_shannon" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_lib_faith_pd" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_diversity_lib_unifrac" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_emperor_plot" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_emperor_biplot" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 7. Stats & ML
# ==========================================
echo "Processing: Stats & ML..."
python -m main --name "qiime_composition_add_pseudocount" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_composition_ancom" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_composition_ancombc" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_longitudinal_pairwise_differences" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_longitudinal_pairwise_distances" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_longitudinal_linear_mixed_effects" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_longitudinal_volatility" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_sample_classifier_classify_samples" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_sample_classifier_regress_samples" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_sample_classifier_heatmap" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 8. Utils
# ==========================================
echo "Processing: Utils..."
python -m main --name "qiime_feature_table_summarize" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_filter_samples" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_filter_features" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_subsample" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_merge" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_merge_seqs" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_feature_table_group" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_metadata_tabulate" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_metadata_distance_matrix" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

# ==========================================
# 9. Extensions
# ==========================================
echo "Processing: Extensions..."
python -m main --name "qiime_rescript" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_picrust2" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_moshpit" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini
python -m main --name "qiime_decontam" --manual /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/combined.pdf --output_location ./skills/ --model gemini

echo "All skills generated!"
