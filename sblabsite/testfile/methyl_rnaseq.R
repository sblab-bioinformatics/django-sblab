# -----------------------------------------------------------------------------
# Correlate fC-enriched genes (actually their nearest CpG) to gene expression
# -----------------------------------------------------------------------------

gene_rpkm<- read.table('/data01/sblab/users/berald01/projects/20111212_chipseq_formylseq_raiberea/gene_expression/ESC_RNA_RPKM.txt', sep= '\t', header= TRUE)
## Convert 'Transcript name' to 'Gene name'
gene_rpkm$gene_name<- sub('\\-\\d\\d\\d$', '', gene_rpkm$mRNA, perl= TRUE)
gene_rpkm<- aggregate(gene_rpkm$wt, by= list(gene_rpkm$gene_name), max) ## The most expressed transcript as representative of the whole gene.
names(gene_rpkm)<- c('gene_name', 'rpkm')
gene_rpkm$log_z<- (log(gene_rpkm$rpkm+0.001) - mean(log(gene_rpkm$rpkm+0.001))) / sd(log(gene_rpkm$rpkm+0.001)) ## z-score of log(rpkm)
#gene_rpkm$log_z<- (gene_rpkm$rpkm - mean(gene_rpkm$rpkm)) / sd(gene_rpkm$rpkm) ## z-score of log(rpkm)


# Link functional region (e.g. CpG island) to nearest gene ===
# 1. Produce bed file of features to annotate (e.g. CpG islands)
# 2. Assign to each feature the nearest TSS
feature_refgene<- system('
       tail -n+2 ~/reference_seqs/mm9.refgene.tss.bed > /tmp/mm9.refgene.tss.bed;
       tail -n+2 ~/reference_seqs/mm9.cpgIslandExt.bed > /tmp/mm9.cpgIslandExt.bed;
       closestBed -d -t first -a /tmp/mm9.cpgIslandExt.bed -b /tmp/mm9.refgene.tss.bed > /tmp/feature_refgene.bed;
       rm /tmp/mm9*.bed')
feature_refgene<- read.table('/tmp/feature_refgene.bed', sep= '\t', stringsAsFactors= FALSE)
feature_refgene$V4 <- paste(feature_refgene$V1, feature_refgene$V2, feature_refgene$V3, sep= '_') ## This ID must be identical to the rownames used in edger
file.remove('/tmp/feature_refgene.bed')
all(sort(rownames(de.table)) %in% sort(feature_refgene$V4)) ## Must return TRUE

de.genes<- cbind(de.table[order(rownames(de.table)),], feature_refgene[order(feature_refgene$V4),])
all(rownames(de.genes) == de.genes$V4) ## Must return TRUE

de.gene.rpkm<- gene_rpkm[na.omit(match(unique(de.genes$V9), gene_rpkm$gene_name)),]
de.gene.rpkm.fc<- gene_rpkm[na.omit(match(unique(de.genes[de.genes$adj.P.Val < 0.01 & de.genes$logFC < 0, "V9"]), gene_rpkm$gene_name)),]
de.gene.rpkm.mc<- gene_rpkm[na.omit(match( unique(de.genes[de.genes$adj.P.Val < 0.01 & de.genes$logFC > 0, "V9"]), gene_rpkm$gene_name)),]

## This is just to get sensible limits for the y-axis
bx<- c(boxplot(gene_rpkm$rpkm, plot= FALSE)$stats, 
       boxplot(de.gene.rpkm$rpkm, plot= FALSE)$stats, 
       boxplot(de.gene.rpkm.fc$rpkm, plot= FALSE)$stats,
       boxplot(de.gene.rpkm.mc$rpkm, plot= FALSE)$stats
)
cols<- brewer.pal(8, 'Set2')
pdf('boxplot_methyl_gene_expr.pdf', width= 8/2.54, height= 10/2.54, pointsize= 9)
par(las=1, mar= c(3,4,4,0.2))
  boxplot(gene_rpkm$rpkm, outline= FALSE, at= 2, xlim= c(1,9), boxwex= 2, ylim=c(min(bx), max(bx)), col= cols[1] )
  boxplot(de.gene.rpkm.mc$rpkm, outline= FALSE, add= TRUE, at= 4, boxwex= 2, col= cols[2])
  boxplot(de.gene.rpkm$rpkm, outline= FALSE, add= TRUE, at= 6, boxwex= 2, col= cols[3])
  boxplot(de.gene.rpkm.fc$rpkm, outline= FALSE, add= TRUE, at= 8, boxwex= 2, col= cols[4])
  mtext(side= 1, text= c('All', 'mC+', 'All CpG', 'fC+'), line= 0.25, at= c(2,4,6,8), font= c(1,2,1,2))
  mtext(side= 1, text= c(length(gene_rpkm$rpkm), length(de.gene.rpkm.mc$rpkm), length(de.gene.rpkm$rpkm), length(de.gene.rpkm.fc$rpkm)), line= 1.5, at= c(2,4,6,8), font=c(1,2,1,2))
  mtext(side= 2, text= 'Gene expression level (RPKM)', line= 2.25, las= 0)
  mtext(side=3, text= 'Effect of cytosine status in CGIs\non gene expression', line= 0.25, font=2, cex= 1.2)
  points(x= c(2,4,6,8), y= c(mean(gene_rpkm$rpkm), mean(de.gene.rpkm.mc$rpkm), mean(de.gene.rpkm$rpkm), mean(de.gene.rpkm.fc$rpkm)), pch= 19, col= cols[1:4], cex= 1.5)
dev.off()
system('scp boxplot_methyl_gene_expr.pdf 143.65.172.155:/Volumes/cri_public/sblab/berald01/projects/20111212_chipseq_formylseq_raiberea/Documents/')
## Test differences between groups
wilcox.test(de.gene.rpkm.fc$rpkm, de.gene.rpkm.mc$rpkm)
wilcox.test(de.gene.rpkm.fc$rpkm, de.gene.rpkm$rpkm)
wilcox.test(de.gene.rpkm.mc$rpkm, de.gene.rpkm$rpkm)
