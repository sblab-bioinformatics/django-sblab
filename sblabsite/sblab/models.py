# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
import psycopg2
import os

" -----------------------[ Help to show for the fields ]---------------------- "

help_text_library_id= 'ID of the library'
help_text_sample_id= 'ID of the biological sample'

" -------------------------[ Functions ]-------------------------------------- "

" ---------------------------------------------------------------------------- "


class FilingOrder(models.Model):
    filing_order = models.DecimalField(unique=True, max_digits=10, decimal_places=4)
    table_name = models.CharField(primary_key=True, max_length= 100)
    class Meta:
        db_table = u'filing_order'
        verbose_name_plural = db_table
    def __unicode__(self):
        return(self.table_name)

class Contacts(models.Model):
    contact_name = models.CharField(primary_key=True, max_length= 100)
    initials= models.CharField(max_length= 100)
    class Meta:
        db_table = u'contacts'
        verbose_name_plural = db_table
        ordering= ['contact_name']
    def __unicode__(self):
        return(self.contact_name)

class Projects(models.Model):
    project = models.CharField(primary_key=True, max_length= 100)
    start_date = models.DateField()
    contact = models.ForeignKey(Contacts, db_column='contact')
    description = models.TextField()
    redmine_page= models.TextField()
    is_active= models.BooleanField()
    is_deprecated= models.BooleanField()
    class Meta:
        db_table = u'projects'
        verbose_name_plural = db_table
        ordering= ['project']
        app_label= 'Projects_experimental_designs'
    def __unicode__(self):
        return(self.project)

#class ProjectFiles(models.Model):
#    file_id = models.IntegerField(primary_key=True)
#    project = models.ForeignKey(Projects, db_column='project')
#    hostname = models.CharField(max_length= 100)
#    path = models.CharField(max_length= 100)
#    filename = models.CharField(max_length= 100)
#    ctime = models.DateTimeField()
#    mtime = models.DateTimeField()
#    fsize = models.BigIntegerField()
#    md5sum = models.CharField(max_length= 32)
#    removed = models.BooleanField()
#    description = models.TextField()
#    class Meta:
#        db_table = u'project_files'
#        verbose_name_plural = db_table
#    def __unicode__(self):
#        return(self.filename)
        
class ViewChipseqDesign(models.Model):
    project = models.CharField(max_length= 100)
    basename = models.CharField(max_length= 100)
    library_id = models.CharField(max_length= 100, help_text= help_text_library_id)
    alignment_bam = models.CharField(max_length= 100)
    sample_id = models.CharField(max_length= 100, help_text= help_text_sample_id)
    s_variable = models.CharField(max_length= 100)
    s_value = models.CharField(max_length= 100)
    input_id = models.CharField(max_length= 100)
    input= models.CharField(max_length= 100)
    id = models.TextField(primary_key= True)
    class Meta:
        db_table = u'view_chipseq_design'
        verbose_name_plural = db_table
    def __unicode__(self):
        return(self.project)

class SampleSources(models.Model):
    source_name= models.CharField(primary_key=True, max_length= 255)
    description= models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'sample_sources'
        verbose_name_plural = db_table
        ordering= ['source_name']
    def __unicode__(self):
        return(self.source_name)

class Organisms(models.Model):
    organism= models.CharField(primary_key=True, max_length= 255)
    description= models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'organisms'
        verbose_name_plural = db_table
        ordering= ['organism']
    def __unicode__(self):
        return(self.organism)

class Molecules(models.Model):
    molecule= models.CharField(primary_key=True, max_length= 255)
    is_geo= models.BooleanField(help_text= 'Is this entry allowed in GEO?')
    description= models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'molecules'
        verbose_name_plural = db_table
        ordering= ['molecule']
    def __unicode__(self):
        return(self.molecule)

class Samples(models.Model):
    """The experimental samples prepared"""
    sample_id = models.CharField(primary_key=True, max_length= 100, help_text= help_text_sample_id)
    contact = models.ForeignKey(Contacts, db_column='contact')
    refdate= models.DateField(verbose_name= 'refdate', help_text= 'Reference date (preparation date)', null= True, blank= True)
    description = models.TextField(blank= True, null= True)
    source_name= models.ForeignKey(SampleSources, db_column='source_name')
    organism= models.ForeignKey(Organisms, db_column='organism', help_text= 'Entry should be suitable for GEO submission')
    molecule= models.ForeignKey(Molecules, db_column='molecule')
    class Meta:
        db_table = u'samples'
        verbose_name_plural = db_table
        ordering= ['sample_id']
    def __unicode__(self):
        return(self.sample_id)

class ProjectSamples(models.Model):
    project = models.ForeignKey(Projects, db_column='project')
    sample = models.ForeignKey(Samples, help_text= help_text_sample_id)
    class Meta:
        db_table = u'project_samples'
        verbose_name_plural = db_table
    def __unicode__(self):
        return(str(self.project))
        
class ExpVariables(models.Model):
    s_variable = models.CharField(primary_key=True, max_length= 100)
    in_use= models.BooleanField()
    variable_type= models.CharField(max_length= 255, blank= True, null= True)
    description = models.TextField()
    class Meta:
        db_table = u'exp_variables'
        verbose_name_plural = db_table
        ordering= ['s_variable']
        app_label= 'experimental_variables'
    def __unicode__(self):
        return(self.s_variable)

class ExpValues(models.Model):
    s_variable= models.ForeignKey(ExpVariables, db_column='s_variable')
    s_value= models.CharField(max_length= 100)
    description= models.TextField(blank=True, null=True)
    class Meta:
        db_table= u'exp_values'
        verbose_name_plural = db_table
        ordering= ['s_variable']
        app_label= 'experimental_variables'
    def __unicode__(self):
        return(str(self.s_variable))
    
class ExpDesign(models.Model):
    """
    Each sample :model:`Samples` has one or more lines describing
    its treatmentes and characteristics relevant to the experimental design.
    """
    sample = models.ForeignKey(Samples, help_text= help_text_sample_id)
    s_variable = models.ForeignKey(ExpVariables, db_column='s_variable')
    s_value = models.CharField(max_length= 100)
    ## s_value = models.ManyToManyField(ExpValues, db_column='s_value')
    ## id= models.IntegerField(primary_key= True)
    class Meta:
        db_table = u'exp_design'
        verbose_name_plural = db_table
        ordering= ['sample']
        app_label= 'experimental_variables'
    def __unicode__(self):
        return(str(self.sample))

class Barcodes(models.Model):
    barcode_id = models.CharField(primary_key=True, max_length= 100)
    barcode_sequence = models.CharField(max_length= 100)
    adapter_sequence= models.CharField(max_length= 255, null= True, blank= True)
    description = models.TextField()
    class Meta:
        db_table = u'barcodes'
        verbose_name_plural = db_table
        ordering= ['barcode_id']
    def __unicode__(self):
        return(str(self.barcode_id))

class Instruments(models.Model):
    instrument = models.CharField(primary_key=True, max_length= 255)
    class Meta:
        db_table = u'instruments'
        verbose_name_plural = db_table
        ordering= ['instrument']
    def __unicode__(self):
        return(str(self.instrument))

class SolexaLims(models.Model):
    service_id = models.CharField(primary_key=True, max_length= 100)
    refdate = models.DateField()
    contact = models.ForeignKey(Contacts, db_column='contact', blank=True, null=True)
##    solexa_pipeline_results = models.CharField(max_length= 255)
    description = models.TextField(blank= True, null= True)
##     instrument = models.ForeignKey(Instruments, db_column='instrument', blank=True, null=True)
    class Meta:
        db_table = u'solexa_lims'
        verbose_name_plural = db_table
        ordering= ['service_id']
    def __unicode__(self):
        return(str(self.service_id))

#class ReferenceSeqs(models.Model):
#    reference_seq = models.CharField(primary_key=True, max_length= True)
#    filename = models.CharField(max_length= 255)
#    format = models.CharField(max_length= 255)
#    md5sum = models.CharField(max_length= 32)
#    source = models.CharField(max_length= 255)
#    description = models.TextField(blank= True, null= True)
#    class Meta:
#        db_table = u'reference_seqs'
#        verbose_name_plural = db_table
#        ordering= ['reference_seq']
#    def __unicode__(self):
#        return(str(self.reference_seq))

class LibraryTypes(models.Model):
    library_type = models.CharField(primary_key=True, max_length= 255, help_text= 'A Short Read Archive-specific field that describes the sequencing technique for this library')
    is_geo= models.BooleanField(help_text= 'Is this entry allowed in GEO?') 
    description = models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'library_types'
        verbose_name_plural = db_table
        ordering= ['library_type']
    class Media:
        js = ("javascript/test_script.js",)
    def __unicode__(self):
        return(str(self.library_type))
        
class Libraries(models.Model):
    library_id = models.CharField(primary_key=True, max_length= 255, help_text= help_text_library_id)
    sample = models.ForeignKey(Samples, help_text= help_text_sample_id)
    refdate= models.DateField(verbose_name= 'refdate', help_text= 'Reference date (preparation date)', null= True, blank= True)
    barcode = models.ForeignKey(Barcodes)
    contact = models.ForeignKey(Contacts, db_column='contact')
    library_type = models.ForeignKey(LibraryTypes, db_column='library_type', verbose_name= 'Library_type')
    description = models.TextField(blank= True, null= True)
    fragment_size= models.CharField(blank= True, null= True, max_length= 255) 
    class Meta:
        db_table = u'libraries'
        verbose_name_plural = db_table
        ordering= ['library_id']
    class Media:
        js = ("javascript/test_script.js",)
    def __unicode__(self):
        return(str(self.library_id))

class Encodings(models.Model):
    encoding= models.CharField(primary_key=True, max_length= 255)
    description= models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'encodings'
        verbose_name_plural = db_table
        ordering= ['encoding']
    class Media:
        js = ("javascript/test_script.js",)
    def __unicode__(self):
        return(str(self.encoding))

class SequencingPlatforms(models.Model):
    sequencing_platform= models.CharField(primary_key=True, max_length= 255)
    description= models.TextField(blank= True, null= True)
    class Meta:
        db_table = u'sequencing_platforms'
        verbose_name_plural = db_table
        ordering= ['sequencing_platform']
    class Media:
        js = ("javascript/test_script.js",)
    def __unicode__(self):
        return(str(self.sequencing_platform))

class Sequencers(models.Model):
    sequencer_id= models.CharField(primary_key=True, max_length= 255)
    sequencing_platform= models.ForeignKey(SequencingPlatforms, db_column= 'sequencing_platform', null= False, blank= False, help_text= 'Sequencing platform')
    sequencer_ip= models.CharField(primary_key=False, max_length= 255)
    location= models.CharField(primary_key=False, max_length= 255)
    class Meta:
        db_table = u'sequencers'
        verbose_name_plural = db_table
        ordering= ['sequencing_platform']
    class Media:
        js = ("javascript/test_script.js",)
    def __unicode__(self):
        return(str(self.sequencer_id))

class Fastqfiles(models.Model):
    fastqfile = models.CharField(primary_key=True, max_length= 255)
    encoding = models.ForeignKey(Encodings, db_column= 'encoding', null= False, blank= False, help_text= 'Quality encodings allowed by GEO')
    md5sum = models.CharField(max_length= 32)
    description = models.TextField(blank= True, null= True)
    library = models.ForeignKey(Libraries, db_column= 'library_id', null= False, blank= False, help_text= help_text_library_id)
    sequencing_platform= models.ForeignKey(SequencingPlatforms, db_column= 'sequencing_platform', null= True, blank= True)
    sequencer_id= models.ForeignKey(Sequencers, db_column= 'sequencer_id', null= True, blank= True)
    read= models.TextField(blank= True, null= True)
    def file_link(self):
        if self.fastqc:
            return("<a href='%s'>%s</a>" %(self.fastqc.url, os.path.split(self.fastqc.url)[1],))
        else:
            return("No attachment")
    class Meta:
        db_table = u'fastqfiles'
        verbose_name_plural = db_table
        ordering= ['fastqfile']
    def __unicode__(self):
        return(str(self.fastqfile))
    file_link.allow_tags = True

#class ViewFastqForLibrary(models.Model):
#    library_id= models.CharField(max_length= 255, primary_key= True)
#    fastqfile= models.CharField(max_length= 255, blank= True, null= True)
#    service_id= models.CharField(max_length= 255, blank= True, null= True)
#    barcode_id= models.CharField(max_length= 255, blank= True, null= True)
#    demultiplexed_file= models.CharField(max_length= 255, blank= True, null= True)
#    demux_sheet= models.CharField(max_length= 255, blank= True, null= True)
#    class Meta:
#        db_table = u'view_fastq_for_library'
#        verbose_name_plural = db_table
#        ordering= ['service_id']
#    def __unicode__(self):
#        return(str(self.library_id))

class ViewDemuxReport(models.Model):
    fastqfile_demux= models.CharField(max_length= 255, primary_key= True)
    master_fastq= models.CharField(max_length= 255, blank= True, null= True)
    nreads_master= models.IntegerField()
    nreads_assigned= models.IntegerField()
    percent_assigned= models.DecimalField(decimal_places= 2, max_digits= 100)
    nreads_with_perfect_match= models.IntegerField()
    percent_with_perfect_match= models.DecimalField(decimal_places= 2, max_digits= 100)
    nreads_lost= models.IntegerField()
    percent_lost= models.DecimalField(decimal_places= 2, max_digits= 100)
    nreads_with_n= models.IntegerField()
    n_best_unspec_barcode= models.IntegerField()
    barcode_id= models.CharField(max_length= 255, blank= True, null= True)
    barcode_sequence= models.CharField(max_length= 255, blank= True, null= True)
    nreads_in_barcode= models.IntegerField()
    percent_in_barcode= models.DecimalField(decimal_places= 2, max_digits= 100)
    class Meta:
        db_table = u'view_demux_report'
        verbose_name_plural = db_table
        ordering= ['master_fastq', 'nreads_in_barcode']
        app_label= 'Quality control'
    def __unicode__(self):
        return(str(self.fastqfile_demux))
                
class Lib2Seq(models.Model):
    library_id = models.ForeignKey(Libraries, db_column='library_id')
    service_id = models.ForeignKey(SolexaLims, db_column='service_id')
    class Meta:
        db_table = u'lib2seq'        
    def __unicode__(self):
        return(str(self.library_id))

class ViewMaxInitials(models.Model):
    initials= models.CharField(primary_key= True, max_length= 255, null= True, blank= True)
    int_max= models.CharField(max_length= 255, null= True, blank= True)
    contact_name= models.CharField(max_length= 255, null= True, blank= True)
    class Meta:
        db_table = u'view_max_initials'
        verbose_name_plural = db_table
    def __unicode__(self):
        return(str(self.initial))
        
class ViewBamqc(models.Model):
    project= models.CharField(max_length= 255, null= True, blank= True)
    sample_id= models.CharField(max_length= 255, null= True, blank= True)
    bamfile= models.CharField(max_length= 255, primary_key= True)
    reference_seq= models.CharField(max_length= 255, null= True, blank= True)
    len_median= models.IntegerField(null= True, blank= True)
    reads_millions= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True)
    aln= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True)
    perc_aln= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True, verbose_name= '% Aln')
    mapq_5= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True)
    perc_mapq_5= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True, verbose_name= '% MAPQ 5')
    mapq_15= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True)
    perc_mapq_15= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True, verbose_name= '% MAPQ 15')
    mapq_30= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True)
    perc_mapq_30= models.DecimalField(max_digits=65535, decimal_places=2, null= True, blank= True, verbose_name= '% MAPQ 30')
    fullname= models.CharField(max_length= 255, null= True, blank= True)
    md5sum= models.CharField(max_length= 255, null= True, blank= True)
    fsize= models.CharField(max_length= 255, blank= True, null= True)
    ctime= models.CharField(max_length= 255, blank= True, null= True)
    mtime= models.CharField(max_length= 255, blank= True, null= True)
    class Meta:
        db_table = u'view_bamqc'
        verbose_name_plural = db_table
        app_label= 'Quality control'
    def __unicode__(self):
        return(str(self.bamfile))

class SamtoolsIdxstats(models.Model):
    sequence_name= models.CharField(max_length= 255, primary_key= True)
    sequence_length= models.IntegerField()
    reads_mapped= models.IntegerField()
    reads_unmapped= models.IntegerField()
    bamfile= models.CharField(max_length= 255, null= True, blank= True)
    md5sum=  models.CharField(max_length= 255, null= True, blank= True)
    class Meta:
        db_table = u'samtools_idxstats'
        verbose_name_plural = db_table
        app_label= 'Quality control'
    def __unicode__(self):
        return(str(self.bamfile))

class Fastqc(models.Model):
    " Created by select names() vartypes should be checked!"
    fastqc= models.CharField(max_length= 255, blank= True, null= True)
    base_stats= models.CharField(max_length= 255, blank= True, null= True)
    filename= models.CharField(primary_key= True, max_length= 255, blank= True, null= True)
    file_type= models.CharField(max_length= 255, blank= True, null= True)
    encoding= models.CharField(max_length= 255, blank= True, null= True)
    tot_sequences= models.CharField(max_length= 255, blank= True, null= True)
    fitered_sequences= models.CharField(max_length= 255, blank= True, null= True)
    sequence_length_all= models.CharField(max_length= 255, blank= True, null= True)
    gc_cont= models.IntegerField(max_length= 255, blank= True, null= True)
    md5sum= models.CharField(max_length= 255, blank= True, null= True)
    per_base_sequence_quality= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_mean= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_median= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_lower_quartile= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_upper_quartile= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_10th_percentile= models.CharField(max_length= 255, blank= True, null= True)
    pbsq_90th_percentile= models.CharField(max_length= 255, blank= True, null= True)
    per_sequence_quality_scores= models.CharField(max_length= 255, blank= True, null= True)
    psqs_quality= models.CharField(max_length= 255, blank= True, null= True)
    psqs_count= models.CharField(max_length= 255, blank= True, null= True)
    per_base_sequence_content= models.CharField(max_length= 255, blank= True, null= True)
    pbsc_g= models.CharField(max_length= 255, blank= True, null= True)
    pbsc_a= models.CharField(max_length= 255, blank= True, null= True)
    pbsc_t= models.CharField(max_length= 255, blank= True, null= True)
    pbsc_c= models.CharField(max_length= 255, blank= True, null= True)
    per_base_gc_content= models.CharField(max_length= 255, blank= True, null= True)
    pbgc= models.CharField(max_length= 255, blank= True, null= True)
    per_sequence_gc_content= models.CharField(max_length= 255, blank= True, null= True)
    ps_gc_content= models.CharField(max_length= 255, blank= True, null= True)
    ps_gc_count= models.CharField(max_length= 255, blank= True, null= True)
    per_base_n_content= models.CharField(max_length= 255, blank= True, null= True)
    pb_n_count= models.CharField(max_length= 255, blank= True, null= True)
    sequence_length_distribution= models.CharField(max_length= 255, blank= True, null= True)
    sequence_length= models.CharField(max_length= 255, blank= True, null= True)
    sequence_length_count= models.CharField(max_length= 255, blank= True, null= True)
    sequence_duplication_levels= models.CharField(max_length= 255, blank= True, null= True)
    tot_dupl_percentage= models.DecimalField(decimal_places= 2, max_digits= 10, blank= True, null= True)
    dupl_level= models.CharField(max_length= 255, blank= True, null= True)
    dupl_level_relative_count= models.CharField(max_length= 255, blank= True, null= True)
    overrepresented_sequences= models.CharField(max_length= 255, blank= True, null= True)
    overrepresented_sequence= models.CharField(max_length= 255, blank= True, null= True)
    overrepresented_sequence_count= models.CharField(max_length= 255, blank= True, null= True)
    overrepresented_sequence_percent= models.CharField(max_length= 255, blank= True, null= True)
    possible_source= models.CharField(max_length= 255, blank= True, null= True)
    kmer_content= models.CharField(max_length= 255, blank= True, null= True)
    kmer_sequence= models.CharField(max_length= 255, blank= True, null= True)
    kmer_count= models.CharField(max_length= 255, blank= True, null= True)
    obs_exp_overall= models.CharField(max_length= 255, blank= True, null= True)
    obs_exp_max= models.CharField(max_length= 255, blank= True, null= True)
    max_obs_exp_position= models.CharField(max_length= 255, blank= True, null= True)
    fastqc_file= models.FileField(upload_to= 'uploads/fastqc/', blank=True, null=True)
    def fastqc_link(self):
        if self.fastqc_file:
            return("<a href='%s'>%s</a>" %(self.fastqc_file.url, self.fastqc_file.url.replace('/fastqc_report.html', ''),))
        else:
            return("No attachment")
    class Meta:
        db_table = u'fastqc'
        verbose_name_plural = db_table
        app_label= 'Quality control'
    fastqc_link.allow_tags = True
    def __unicode__(self):
        return(str(self.filename))

#class CufflinksTranscripts(models.Model):
#    chrom = models.CharField(max_length= 255)
#    ## library= models.ForeignKey(Libraries, blank= True, null= True, db_column= 'library_id')
#    library_id= models.CharField(max_length= 255)
#    feature = models.CharField(max_length= 255)
#    fstart= models.IntegerField()
#    fend= models.IntegerField()
#    score= models.IntegerField()
#    strand= models.CharField(max_length= 1)
#    frame= models.CharField(max_length= 1)
#    gene_id= models.CharField(max_length= 255)
#    transcript_id= models.CharField(max_length= 255)
#    fpkm= models.DecimalField(max_digits=65535, decimal_places=3)
#    frac= models.DecimalField(max_digits=65535, decimal_places=3)
#    conf_lo= models.DecimalField(max_digits=65535, decimal_places=3)
#    conf_hi= models.DecimalField(max_digits=65535, decimal_places=3)
#    cov= models.DecimalField(max_digits=65535, decimal_places=3)
#    attributes= models.CharField(max_length= 255, primary_key= True)
#    #project= models.ForeignKey(Projects, blank= True, null= True, db_column= 'project_id')
#    project= models.CharField(max_length= 255, db_column= 'project_id')
#    class Meta:
#        db_table = '"20120622_rnaseq_pdsa"."cufflinks_gtf"'
#        verbose_name_plural = 'cufflinks_gtf'
#        ordering= ['library_id']
#    def __unicode__(self):
#        return(str(self.attributes))
        
class Testfile(models.Model):
    fileid= models.CharField(primary_key= True, max_length= 255)
    file= models.FileField(upload_to= 'testfile/')
    def file_link(self):
        if self.file:
            return "<a href='%s'>download</a>" % (self.file.url,)
        else:
            return "No attachment"
    class Meta:
        db_table = u'testfile'
    def __unicode__(self):
        return(str(self.fileid))
    file_link.allow_tags = True

class ViewLibraryServiceFastq(models.Model):
    service_id= models.CharField(max_length= 255, primary_key= True)
    library_id= models.CharField(max_length= 255)
    service_contact= models.CharField(max_length= 255)
    fastqfile= models.CharField(max_length= 255)
    class Meta:
        db_table = 'view_library_service_fastq'
        verbose_name_plural = 'view_library_service_fastq'
        ordering= ['library_id']
    def __unicode__(self):
        return(str(self.service_id))
