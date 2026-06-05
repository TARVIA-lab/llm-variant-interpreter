#!/bin/bash

# Golden Genes PNG Figures - Copy Commands
# All 5 figures ready for manuscripts, presentations, and posters

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     GOLDEN GENES PNG FIGURES - COPY TO YOUR LOCATION          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# QUICK COPY - All figures to Desktop
echo "OPTION 1: Copy all PNG figures to Desktop"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/*.png ~/Desktop/"
echo ""

# OPTION 2: Copy to manuscript folder
echo "OPTION 2: Copy to Manuscript folder"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "mkdir -p ~/Documents/Manuscript/Figures"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/*.png ~/Documents/Manuscript/Figures/"
echo ""

# OPTION 3: Copy individual figures
echo "OPTION 3: Copy individual figures (select as needed)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "# Overview (best for talks)"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/Fig1_Golden_Genes_Overview.png ~/Desktop/"
echo ""
echo "# Heatmap (best for manuscript results)"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/Fig2_Manuscript_Genes_Heatmap.png ~/Desktop/"
echo ""
echo "# Top genes (best for candidate selection)"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/Fig3_Top_Golden_Genes.png ~/Desktop/"
echo ""
echo "# Integration model (best for conceptual diagram)"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/Fig4_Multi_System_Integration.png ~/Desktop/"
echo ""
echo "# Dashboard (best for comprehensive summary)"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/Fig5_Summary_Dashboard.png ~/Desktop/"
echo ""

# OPTION 4: Copy with guide
echo "OPTION 4: Copy figures + guide to new folder"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "mkdir -p ~/Desktop/Golden_Genes_Figures"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/*.png ~/Desktop/Golden_Genes_Figures/"
echo "cp /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/FIGURE_GUIDE.md ~/Desktop/Golden_Genes_Figures/"
echo "open ~/Desktop/Golden_Genes_Figures/"
echo ""

# FILE INFORMATION
echo "═══════════════════════════════════════════════════════════════"
echo "FIGURE INFORMATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Fig1_Golden_Genes_Overview.png          (690 KB)"
echo "  → 4-panel overview: composition, validation, claims, stats"
echo ""
echo "Fig2_Manuscript_Genes_Heatmap.png       (366 KB)"
echo "  → Expression heatmap of ~30 key manuscript genes"
echo ""
echo "Fig3_Top_Golden_Genes.png               (392 KB)"
echo "  → Top 30 genes by spheroid upregulation & RelB dependency"
echo ""
echo "Fig4_Multi_System_Integration.png       (446 KB)"
echo "  → RelB as master switch model (6 systems)"
echo ""
echo "Fig5_Summary_Dashboard.png              (795 KB)"
echo "  → 7-panel comprehensive statistics dashboard"
echo ""
echo "Total: 2.6 MB of publication-quality figures (300 DPI)"
echo ""

# VERIFICATION
echo "═══════════════════════════════════════════════════════════════"
echo "VERIFY FILES EXIST"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "ls -lh /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/*.png"
echo ""

# OPEN IN FINDER
echo "═══════════════════════════════════════════════════════════════"
echo "VIEW FIGURES IN FINDER"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "open /Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/golden_genes_figures/"
echo ""

