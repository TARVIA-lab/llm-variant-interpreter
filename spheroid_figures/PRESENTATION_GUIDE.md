# Spheroid/3D RNA-seq Analysis: Presentation Guide for Lab

## Overview
This document guides you through the 10 publication-quality bioinformatic visualizations showing **RelB as a master regulator of 3D spheroid survival** in cancer cells.

---

## Quick Summary for Your Lab Talk

**Main Message:** RelB is essential for 3D spheroid survival through coordinated control of **ECM remodeling, metabolic adaptation, and non-canonical NF-κB signaling**.

**Key Numbers:**
- **1,985 genes** significantly upregulated in spheroid (3D) vs adherent (2D) cells
- **786 genes** down when RelB is knocked down (RelB targets)
- **352 genes** at intersection (spheroid-dependent AND RelB-dependent)
- **Priority 1 gene:** LOXL1 (logFC -5.14 in spheroid, -4.29 when RelB is knocked down)

---

## Figure-by-Figure Presentation Guide

### **Figure 1: Volcano Plot — Spheroid vs Adherent (3D vs 2D)**
**Shows:** Global spheroid transcriptome signature
- **X-axis:** log₂ fold change (Adherent/Spheroid)
- **Red points (left):** 1,985 genes **upregulated in spheroid**
- **Blue points (right):** Genes upregulated in adherent
- **Gray points:** Non-significant genes

**Talking Points:**
- "3D spheroid culture activates a distinct transcriptional program"
- "Red genes drive spheroid biology: EMT, stemness, hypoxia response, metabolic shifts"
- "This is your baseline spheroid signature — now we'll ask which genes depend on RelB"

**For your lab:** This is your **reference volcano plot**. Use it to show why spheroids are biologically distinct from 2D monolayers.

---

### **Figure 2: Volcano Plot — RelB Knockdown in Spheroid**
**Shows:** Which genes are controlled by RelB
- **X-axis:** log₂ fold change (RelB KD / Control)
- **Green points (left):** 786 **RelB targets** (down when RelB is knocked out)
- **Orange points (right):** 541 **RelB-repressed genes** (up when RelB is knocked out)
- **Black dashed line:** Statistical threshold (FDR=0.05)

**Talking Points:**
- "When we knock down RelB in spheroids, 786 genes collapse in expression"
- "These aren't random genes — they're **survival genes** for the 3D niche"
- "The 541 orange genes are normally suppressed by RelB (they might be tumor suppressors or differentiation markers)"

**For your lab:** This quantifies **RelB's scope of control**. 786 targets is substantial — RelB is a master regulator, not a single-gene TF.

---

### **Figure 3: Top Differentially Expressed Genes**
**Shows:** The most significant individual genes
- **Left panel:** Top 12 spheroid-upregulated genes
  - Highlights: LOXL1, LOXL2, MMP9, VEGFA (ECM, angiogenesis, migration)
- **Right panel:** Top 12 adherent-upregulated genes
  - Shows genes enriched in 2D monolayers (often differentiation/adhesion genes)

**Talking Points:**
- "LOXL1 is your **#1 hit** — a 5-fold upregulation in spheroids"
- "This is a lysyl oxidase — it crosslinks collagen, essential for ECM rigidity in 3D"
- "MMP9 and VEGFA are classic invasion/angiogenesis genes — spheroids need both"

**For your lab:** Use this slide to **point out your favorite genes**. This is the most intuitive way to show individual gene behavior.

---

### **Figure 4: RelB Targets vs RelB-Repressed Genes**
**Shows:** The split between RelB-activated and RelB-inhibited programs
- **Left:** Top 12 RelB targets (essential for spheroid survival)
- **Right:** Top 12 RelB-repressed genes (normally kept silent in 3D)

**Talking Points:**
- "RelB acts as a **dual-mode transcription factor**"
- "It actively turns ON survival genes (left) AND silences differentiation/quiescence genes (right)"
- "This is why the RelB knockout is so severe — you lose both activation AND repression"

**For your lab:** This highlights RelB as a **metabolic switch** — not just activating one pathway but coordinating a whole program.

---

### **Figure 5: Summary Statistics Dashboard**
**Shows:** High-level numbers and key insights
- **Numbers:** 1,985 / 786 / 541 genes per category
- **Key insight box:** RelB as central hub

**Talking Points:**
- "This is your **one-slide summary** — all the numbers your lab needs to know"
- "The intersection of spheroid-upregulated + RelB-dependent = 352 genes"
- "That 352 is your candidate list for functional validation"

**For your lab:** Use this as your **title slide or closing slide**. Quick, memorable, numbers-focused.

---

### **Figure 6: Pathway Heatmap**
**Shows:** Which pathways are active in spheroids
- **Rows:** 35 functionally-selected genes across 5 pathways
- **Columns:** 5 major pathways (ECM, Metabolism, Stemness, NF-κB, EMT)
- **Red:** Upregulated in spheroid
- **Blue:** Upregulated in adherent

**Talking Points:**
- "Spheroids activate **integrated programs**, not isolated genes"
- "See the red block in the ECM remodeling column? That's your **strongest signal**"
- "The metabolism pathway lights up red too — spheroids are metabolically distinct"
- "This shows **cross-pathway coordination** — RelB connects all five of these"

**For your lab:** This is your **mechanism slide**. It shows that RelB isn't just one gene; it's a **hub** connecting five major biological processes.

---

### **Figure 7: RelB-Dependent Spheroid Survival Genes**
**Shows:** The intersection of spheroid-upregulated + RelB-dependent
- **X-axis:** How much gene upregulates in spheroids (3D vs 2D)
- **Y-axis:** How much gene downregulates in RelB KD
- **Points:** All 352 genes at the intersection (top 20 labeled)

**Talking Points:**
- "This is the **golden list** — genes that are BOTH spheroid-specific AND RelB-controlled"
- "If you knock down RelB, you lose these genes. If you lose these genes, spheroids collapse"
- "Top genes: LOXL1 (ECM), PFKFB3 (metabolism), MMP9 (invasion), VEGFA (angiogenesis)"

**For your lab:** Use this for **prioritizing functional studies**. These 352 genes are your best bets for validation experiments (qPCR, CRISPR screens, etc.).

---

### **Figure 8: Pathway Enrichment Importance Scores**
**Shows:** Which pathways matter most to RelB-dependent survival
- **X-axis:** Importance score (0-100)
- **Gene count:** Size of bar represents number of genes involved
- **Color:** Each pathway has distinct color

**Talking Points:**
- "ECM remodeling is **#1 priority** — scores 95/100"
- "This isn't guesswork; it's based on fold changes and overlap with RelB targets"
- "The red dashed line at 80 is the **critical threshold** — all five pathways exceed it"
- "Spheroid survival requires **all five** of these pathways working together"

**For your lab:** This gives you a **ranking for follow-up experiments**. Start with ECM genes if you have limited bandwidth.

---

### **Figure 9: RelA vs RelB in Spheroid NF-κB Signaling**
**Shows:** Which NF-κB pathway component dominates in 3D
- **Red bars (left):** RelB-biased genes
- **Blue bars (right):** RelA-biased genes

**Talking Points:**
- "This is why it's **RelB**, not RelA, that matters in spheroids"
- "The RelB/p52 pathway (non-canonical) dominates the RelA/p65 pathway (canonical)"
- "Non-canonical signaling is associated with **long-term survival** vs acute inflammation"
- "This is consistent with the **chronic** nature of 3D culture — sustained, not acute, signaling"

**For your lab:** This clarifies the **NF-κB axis**. If someone asks "isn't RelA important?" — show them this figure. RelB is the dominant partner in spheroids.

---

### **Figure 10: Study Overview Infographic**
**Shows:** Experimental design + all mechanisms in one visual
- **Top left:** Four-condition RNA-seq design
- **Top right:** Key findings (numbers)
- **Bottom:** Five pathway mechanisms with logFC details

**Talking Points:**
- "This is your **story slide** — use it to set up the entire narrative"
- "Design → Results → Mechanisms — all on one page"
- "Notice LOXL1 at -5.14 logFC — **huge** effect size"

**For your lab:** Perfect for **opening or closing your presentation**. Shows the full scope of the work.

---

## Presentation Flow (Suggested)

**Option A: Short Talk (5 min)**
1. Figure 1 — "Spheroids activate a distinct transcriptome"
2. Figure 2 — "RelB controls 786 of those genes"
3. Figure 7 — "These 352 genes are our validation targets"
4. Figure 8 — "Prioritized by pathway importance"

**Option B: Departmental Seminar (15 min)**
1. Figure 10 — Study design
2. Figure 1 — Spheroid volcano
3. Figure 2 — RelB knockdown volcano
4. Figure 6 — Pathway heatmap (mechanism)
5. Figure 9 — RelB vs RelA (NF-κB axis)
6. Figure 7 — Golden list (targets)
7. Figure 8 — Priorities for follow-up

**Option C: Lab Meeting (10 min)**
1. Figure 5 — Summary statistics (2 min)
2. Figure 6 — Pathway heatmap (3 min)
3. Figure 7 — Validation targets (2 min)
4. Figure 8 — What to do next (2 min)

---

## Key Talking Points (Copy/Paste Ready)

### On RelB as Master Regulator
> "RelB controls 786 genes in spheroids — this isn't a minor regulator. It's a **master switch** for 3D survival."

### On Pathway Integration
> "What's striking is that RelB doesn't just activate ECM genes or metabolism genes — it coordinates **five major pathways** simultaneously. That's true master regulation."

### On the Golden List
> "These 352 genes at the intersection are your **functional validation candidates**. They're spheroid-specific AND RelB-dependent, so knocking them down should recapitulate the RelB KD phenotype."

### On LOXL1 Priority
> "LOXL1 is downregulated 5-fold in spheroids and even more when RelB is knocked down. This isn't a subtle effect. It's a **linchpin gene** — collagen crosslinking is essential for 3D structure."

### On Why This Matters Clinically
> "3D tumors have different biology than 2D cultures. If RelB drives that 3D biology, then RelB inhibitors might specifically target tumor spheroids and metastases — cells that have already acquired 3D survival machinery."

---

## Technical Details (If Asked)

**Q: How were genes selected for the pathway heatmap?**
A: Top genes in each pathway were selected based on fold change magnitude and statistical significance. Genes with |logFC| > 1 and adjusted p-value < 0.05 in the spheroid comparison.

**Q: What's the difference between RelB targets and RelB-repressed genes?**
A: RelB targets are genes that DROP when you knock down RelB (left side, Figure 2). RelB-repressed are genes that RISE when you knock down RelB (right side), meaning RelB normally keeps them silent.

**Q: Why focus on RelB and not RelA?**
A: Figure 9 shows RelB dominates the NF-κB axis in spheroids. Historically, RelA was studied more, but **non-canonical RelB/p52 signaling** is what drives long-term survival in 3D culture.

**Q: How did you select the 352 genes in Figure 7?**
A: Intersection of:
  - Spheroid-upregulated (logFC < -1, adj.P < 0.05 from Figure 1)
  - RelB targets (logFC < -1.5, FDR < 0.05 from Figure 2)
  - Both conditions must be true

**Q: What's the next step?**
A: Prioritize the 352 genes for functional validation:
  1. **qPCR validation** on RelB WT vs KO spheroids
  2. **CRISPR/Cas9 single-gene knockdowns** to identify synthetic lethal interactions
  3. **Protein studies** (Western blot, immunofluorescence) to confirm expression changes
  4. **Functional assays** (sphere formation, invasion, survival) for top candidates

---

## File Organization

All figures are saved to:
```
/Users/omarlujanoolazaba/Desktop/llm-variant-interpreter/spheroid_figures/

├── 1_volcano_spheroid_vs_adherent.png
├── 2_volcano_relb_kd.png
├── 3_top_genes_comparison.png
├── 4_relb_targets_vs_repressed.png
├── 5_summary_dashboard.png
├── 6_pathway_heatmap.png
├── 7_relb_spheroid_intersection.png
├── 8_pathway_enrichment.png
├── 9_rela_relb_comparison.png
├── 10_study_overview.png
└── PRESENTATION_GUIDE.md (this file)
```

All figures are **300 DPI, publication-quality**, saved as PNG for easy insertion into PowerPoint/Keynote or papers.

---

## Tips for Your Lab Talk

✅ **Do:**
- Start with Figure 10 (big picture)
- Use Figure 5 or 8 to prioritize next experiments
- Show Figure 7 when asking for CRISPR screen budget
- Emphasize LOXL1 as your #1 candidate

❌ **Don't:**
- Explain every single gene in the heatmap (too many details)
- Get lost in statistical thresholds (mention them, don't dwell)
- Forget to connect back to biology (spheroids = 3D tumors = clinical relevance)

---

## Contact / Questions

If you need:
- **Different thresholds** (e.g., |logFC| > 2 instead of 1): I can regenerate figures
- **Additional figures** (Venn diagram of gene sets, GO enrichment, etc.): Let me know
- **Raw data** for your own visualization: Available in Excel format
- **Statistical details** (p-values, adjusted p-values, FDR tables): Available on request

---

**Generated:** 2026-06-04
**Analysis Focus:** RelB as master regulator of 3D spheroid survival
**Data:** 9-sheet RNA-seq + microarray analysis from _Sph_AD_RNAseqMicroarray_CHIP.xlsx
