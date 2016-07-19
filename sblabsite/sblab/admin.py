import sblab
from sblab.models import FilingOrder, Contacts, Projects, SampleSources, Molecules, Organisms, Samples, ExpDesign, ExpVariables, ExpValues, Barcodes, LibraryTypes, Libraries, SolexaLims, Fastqfiles, ProjectSamples, Testfile, ViewBamqc, Lib2Seq, Fastqc, ViewDemuxReport, ViewLibraryServiceFastq, SamtoolsIdxstats, Sequencers
from django.contrib import admin
from django import forms
from django.db import models
import psycopg2
import os
import actions

"""
MEMO: To add models to the admin site:
- If not already there, add the model definition to models.py
- Add the model to import line: "from sblab.models import ..."
- Define ModelAdmin
- Register the model (make it visible): "admin.site.register(Model, ModelAdmin)"

Remember that the order matters. Make sure object with dependecies are coded
after.

"""

def get_psycopgpgpass(passfile= os.path.join(os.getenv("HOME"), '.psycopgpass')):
    """
    Read the passfile containing log in details for psycopg2.
    passfile is where the log in details are. pasfile should look like:
    
    dbname=mydb user=me host=xxx.xx.xxx.xx password=mypwd
    
    Return a string that can be passed to:
    psycopg2.connect(get_psycopgpgpass())
    """
    try:
        conn= open(passfile)
    except:
        sys.exit('amdin.get_psycopgpass: I cannot read file %s' %(passfile,))
    conn= conn.readlines()
    conn_args= [x.strip() for x in conn if x.strip() != '' and x.strip().startswith('#') is False][0]
    return(conn_args)
    
def get_table_schema(mytable):
    """
    Get column names and types for table mytable
    TO DO:
        - Note that datatypes are always CharField
    """
    conn = psycopg2.connect(get_psycopgpgpass())
    cur = conn.cursor()
    cur.execute("select column_name, data_type from information_schema.columns where table_name= %s order by ordinal_position;", (mytable,))
    schema= cur.fetchall() ## [('project', 'text'), ('sample_id', 'text'), ('cell_line', 'text'), ...]
        
    fields= {}
    for colname, coltype in schema:
        fields[colname]= models.CharField(max_length=255, verbose_name= ' ' + colname) ## Hack to avoid capitalizing first letter.
    ## fields['__str__']= lambda self: '%s %s' (self.project, self.sample_id)
    return(fields)

def get_table_colnames(mytable):
    """
    Get column names for table mytable and return them as list.
    
     - Note that schema is not specified
    """
    conn = psycopg2.connect(get_psycopgpgpass())
    cur = conn.cursor()
    cur.execute("select column_name from information_schema.columns where table_name= %s order by ordinal_position;", (mytable,))
    colnames= cur.fetchall()
    colnames= [x[0] for x in colnames]
    return(colnames)


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model. See https://code.djangoproject.com/wiki/DynamicModels
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass
    
    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)
    
    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)
    
    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}
    
    # Add in any fields that were provided
    if fields:
        attrs.update(fields)
    
    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    def __unicode__(self):
        ## Not sure this method is necessary or useful in any way!
        unicodename= fields[0][0]
        return(self.unicodename)
    
    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
#        admin.site.register(model, Admin)
    return model

" ----------------------[ Materialized views ]-------------------------------- "

APP_LABEL= 'Projects_experimental_designs'


" Get all the materialzed views "
conn = psycopg2.connect(get_psycopgpgpass())
cur = conn.cursor()
cur.execute("select table_name from information_schema.tables where table_schema = 'materialized_views' and table_name like 'view_%' order by table_name;")
table_projects= cur.fetchall()
table_projects= [str(x[0]) for x in table_projects] ## Note: you need str() otherwise it returns unicode


for table_project in table_projects:
    " Create and register a model for each matview "
    tableModel= table_project
    fields= get_table_schema(table_project)
    ## fields['__unicode__']= lambda self: '%s %s' (self.project, self.cell_line)
    
    createdModel= create_model(tableModel,
                           fields= fields,
                           app_label= APP_LABEL,
                           module= 'fake_project.fake_app.no_models',
                           options= {'db_table': unicode(table_project), 'verbose_name_plural': table_project},
                           admin_opts= {})
    
    
    " Create class model dynamically. This is bad and should be changed "
    class_string= """
class %sAdmin(admin.ModelAdmin):
    list_display= ['sample_id', 'organism', 'molecule', 'source_name'] + [x for x in get_table_colnames(table_project) if x not in ('project', 'id', 'sample_id', 'organism', 'molecule', 'source_name')]
    readonly_fields= get_table_colnames(table_project)
    ordering= ['sample_id']
    search_fields= get_table_colnames(table_project)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
admin.site.register(createdModel, %sAdmin)
""" %(tableModel, tableModel)
    exec(class_string)

" ---------------------------------[ Actions ]-------------------------------- "

def set_to_use_true(modeladmin, request, queryset):
        queryset.update(to_use= True)
set_to_use_true.short_description = "Set to_use to True"

def set_to_use_false(modeladmin, request, queryset):
        queryset.update(to_use= False)
set_to_use_false.short_description = "Set to_use to False"

def set_is_active_true(modeladmin, request, queryset):
        queryset.update(is_active= True)
set_to_use_true.short_description = "Set is_active to True"

def set_is_deprecated_true(modeladmin, request, queryset):
        queryset.update(is_deprecated= True)
set_to_use_true.short_description = "Set is_deprecated to True"

def set_is_active_false(modeladmin, request, queryset):
        queryset.update(is_active= False)
set_to_use_true.short_description = "Set is_active to False"

def set_is_deprecated_false(modeladmin, request, queryset):
        queryset.update(is_deprecated= False)
set_to_use_true.short_description = "Set is_deprecated to False"

""" -------------------------------[ inlines ]----------------------------------
These objects will be showed in the parent table
"""

class SamplesInline(admin.TabularInline):
    model = Samples

class ExpDesignInline(admin.TabularInline):
    model = ExpDesign

class LibrariesInline(admin.TabularInline):
    model = Libraries

#class ProjectFilesInline(admin.TabularInline):
#    model = ProjectFiles

class Lib2SeqInline(admin.TabularInline):
    model = Lib2Seq

" --------------------------[ ModelAdmin ]------------------------------------ "

class FilingOrderAdmin(admin.ModelAdmin):
    list_display= ['table_name', 'filing_order']
    ordering= ('filing_order',)
    formfield_overrides = {
        models.CharField:    {'widget': forms.TextInput(attrs={'size':'20'})},        
    }
    
class ProjectsAdmin(admin.ModelAdmin):
    list_display= ['project', 'start_date', 'contact', 'is_active', 'is_deprecated', 'description', 'redmine_link']
    ordering= ('-start_date', 'project')
    list_filter = ('contact', 'is_active', 'is_deprecated')
    search_fields= list_display
    actions= [set_is_active_true, set_is_active_false, set_is_deprecated_true, set_is_deprecated_false]
    def redmine_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.redmine_page, obj.redmine_page)
    redmine_link.allow_tags = True
    class Media:
        js = ("javascript/list_filter_collapse.js",)
    ## inlines= [ProjectFilesInline, ]

class ContactsAdmin(admin.ModelAdmin):
    list_display= ['contact_name', 'initials']
    ordering= ('contact_name',)
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]

#class ProjectFilesAdmin(admin.ModelAdmin):
#    list_display= ['filename', 'project', 'hostname', 'path', 'ctime', 'mtime', 'fsize', 'md5sum', 'removed', 'description']
#    ordering= ('project', 'filename', )
#    list_filter= ('project', )
#    search_fields= ['file_id', 'hostname', 'path', 'filename', 'ctime', 'mtime', 'fsize', 'md5sum', 'removed', 'description']

class SampleSourcesAdmin(admin.ModelAdmin):
    list_display= ['source_name', 'description']
    ordering= ['source_name']
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

    
class MoleculesAdmin(admin.ModelAdmin):
    list_display= ['molecule', 'is_geo', 'description']
    ordering= ['molecule']
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class OrganismsAdmin(admin.ModelAdmin):
    list_display= ['organism', 'description']
    ordering= ['organism']
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class SamplesAdmin(admin.ModelAdmin):
    list_display= ['sample_id', 'source_name', 'organism', 'molecule', 'contact', 'refdate', 'description']
    ordering= ('sample_id',)
    list_filter = ('contact', 'source_name', 'molecule')
    search_fields= ['sample_id', 'molecule__molecule', 'organism__organism', 'source_name__source_name', 'description', 'refdate'] ## ('sample_id', 'molecule', 'refdate', 'description')
    inlines= [ExpDesignInline, LibrariesInline]
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class ProjectSamplesAdmin(admin.ModelAdmin):
    list_display= ['project', 'sample']
    ordering= ('project', 'sample',)
    list_filter = ('project',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class ExpVariablesAdmin(admin.ModelAdmin):
    list_display= ['s_variable', 'in_use', 'variable_type', 'description']
    ordering= ('s_variable',)
    list_filter = ('s_variable',)
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)
    
class ExpDesignAdmin(admin.ModelAdmin):
    list_display= ['sample', 's_variable', 's_value']
    ordering= ('sample', 's_variable')
    list_filter = ('s_variable', )
    search_fields= ['sample__sample_id', 's_variable__s_variable', 's_value']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    
class ExpValuesAdmin(admin.ModelAdmin):
    list_display= ['s_variable', 's_value', 'description']
    ordering= ('s_variable',)
    list_filter= ('s_variable', )
    search_fields= ['s_variable__s_variable', 's_value']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    
class BarcodesAdmin(admin.ModelAdmin):
    list_display= ['barcode_id', 'barcode_sequence', 'adapter_sequence', 'description']
    ordering= ('barcode_id',)
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    
class SolexaLimsAdmin(admin.ModelAdmin):
    list_display= ['service_id', 'refdate', 'contact']
    ordering= ('service_id',)
    search_fields= ['service_id', 'contact__contact_name']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)
    
#class ReferenceSeqsAdmin(admin.ModelAdmin):
#   list_display= ['reference_seq', 'filename', 'format', 'md5sum', 'source', 'description']
#    ordering= ('reference_seq',)
#    search_field= list_display

class LibraryTypesAdmin(admin.ModelAdmin):
    list_display= ['library_type', 'is_geo', 'description']
    ordering = ('library_type',)
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    
class LibrariesAdmin(admin.ModelAdmin):
    list_display= ['library_id', 'sample', 'library_type', 'refdate', 'barcode', 'fragment_size', 'contact', 'description']
    ordering= ('library_id',)
    search_fields= ['library_id']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    list_filter = ('library_type','contact',)
    inlines= [Lib2SeqInline]
    class Media:
        js = ("javascript/list_filter_collapse.js",)
        
class SequencersAdmin(admin.ModelAdmin):
    list_display= ['sequencer_id', 'sequencing_platform', 'sequencer_ip', 'location']
    ordering= ('sequencing_platform',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)    
    
class FastqfilesAdmin(admin.ModelAdmin):
    list_display= ['fastqfile', 'library', 'md5sum', 'encoding', 'sequencing_platform', 'sequencer_id', 'read', 'description']
    ordering= ('fastqfile',)
    search_fields= ['fastqfile', 'encoding__encoding', 'md5sum', 'description', 'library__library_id', 'sequencing_platform__sequencing_platform', 'sequencer_id__sequencer_id', 'read'] ## , 
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class ViewMaxInitialsAdmin(admin.ModelAdmin):
    list_display= ['initials', 'contact_name', 'int_max']
    ordering= ['initials']
    search_fields= list_display
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    
class Lib2SeqAdmin(admin.ModelAdmin):
    list_display= ['library_id', 'service_id']
    search_fields= ['library_id__library_id', 'service_id__service_id']
    ordering= ('service_id',)
    list_filter= ('service_id',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class ViewBamqcAdmin(admin.ModelAdmin):
    list_display= ['bamfile', 'mtime', 'len_median', 'reads_millions', 'aln', 'perc_aln', 'mapq_5', 'perc_mapq_5', 'mapq_15', 'perc_mapq_15', 'mapq_30', 'perc_mapq_30', 'project', 'sample_id', 'md5sum', 'fullname']
    ordering= ('bamfile',)
    search_fields= list_display
    list_filter = ('project',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class FastqcAdmin(admin.ModelAdmin):
    list_display= ['filename', 'tot_sequences', 'sequence_length_all', 'tot_dupl_percentage', 'gc_cont', 'md5sum', 'fastqc_link']
    readonly_fields= ['fastqc', 'base_stats', 'filename', 'file_type', 'encoding', 'tot_sequences', 'fitered_sequences', 'sequence_length_all', 'gc_cont', 'per_base_sequence_quality', 'pbsq_mean', 'pbsq_median', 'pbsq_lower_quartile', 'pbsq_upper_quartile', 'pbsq_10th_percentile', 'pbsq_90th_percentile', 'per_sequence_quality_scores', 'psqs_quality', 'psqs_count', 'per_base_sequence_content', 'pbsc_g', 'pbsc_a', 'pbsc_t', 'pbsc_c', 'per_base_gc_content', 'pbgc', 'per_sequence_gc_content', 'ps_gc_content', 'ps_gc_count', 'per_base_n_content', 'pb_n_count', 'sequence_length_distribution', 'sequence_length', 'sequence_length_count', 'sequence_duplication_levels', 'tot_dupl_percentage', 'dupl_level', 'dupl_level_relative_count', 'overrepresented_sequences', 'overrepresented_sequence', 'overrepresented_sequence_count', 'overrepresented_sequence_percent', 'possible_source', 'kmer_content', 'kmer_sequence', 'kmer_count', 'obs_exp_overall', 'obs_exp_max', 'max_obs_exp_position', 'md5sum']
    ordering= ('filename',)
    search_fields= ['filename', 'tot_sequences', 'md5sum'] ## ['fastqc', 'base_stats', 'filename', 'file_type', 'encoding', 'tot_sequences', 'fitered_sequences', 'sequence_length_all', 'gc_cont', 'per_base_sequence_quality', 'pbsq_mean', 'pbsq_median', 'pbsq_lower_quartile', 'pbsq_upper_quartile', 'pbsq_10th_percentile', 'pbsq_90th_percentile', 'per_sequence_quality_scores', 'psqs_quality', 'psqs_count', 'per_base_sequence_content', 'pbsc_g', 'pbsc_a', 'pbsc_t', 'pbsc_c', 'per_base_gc_content', 'pbgc', 'per_sequence_gc_content', 'ps_gc_content', 'ps_gc_count', 'per_base_n_content', 'pb_n_count', 'sequence_length_distribution', 'sequence_length', 'sequence_length_count', 'sequence_duplication_levels', 'tot_dupl_percentage', 'dupl_level', 'dupl_level_relative_count', 'overrepresented_sequences', 'overrepresented_sequence', 'overrepresented_sequence_count', 'overrepresented_sequence_percent', 'possible_source', 'kmer_content', 'kmer_sequence', 'kmer_count', 'obs_exp_overall', 'obs_exp_max', 'max_obs_exp_position', 'md5sum']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class SamtoolsIdxstatsAdmin(admin.ModelAdmin):
    list_display= ['sequence_name', 'sequence_length', 'reads_mapped', 'reads_unmapped', 'bamfile', 'md5sum']
    readonly_fields= list_display
    ordering= ('bamfile',)
    search_fields= list_display
    list_filter= ('bamfile',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class CufflinksTranscriptsAdmin(admin.ModelAdmin):
    list_display= ['chrom', 'library_id', 'fstart', 'fend', 'strand', 'gene_id', 'transcript_id', 'fpkm', 'conf_lo', 'conf_hi', 'cov', 'project']
    readonly_fields= list_display
    ordering= ('library_id',)
    search_fields= ['library_id', 'attributes', 'project']
    #list_filter= ('library_id', 'project',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    #class Media:
    #    js = ("javascript/list_filter_collapse.js",)
 
class ViewDemuxReportAdmin(admin.ModelAdmin):
    list_display= ['fastqfile_demux', 'master_fastq', 'nreads_master', 'nreads_assigned', 'percent_assigned', 'nreads_with_perfect_match', 'percent_with_perfect_match', 'nreads_lost', 'percent_lost', 'nreads_with_n', 'n_best_unspec_barcode', 'barcode_id', 'barcode_sequence', 'nreads_in_barcode', 'percent_in_barcode']
    readonly_fields= list_display
    ordering= ('master_fastq',)
    search_fields= list_display
    list_filter= ('barcode_id',)
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class ViewLibraryServiceFastqAdmin(admin.ModelAdmin):
    list_display= ['service_id', 'library_id', 'service_contact', 'fastqfile']
    readonly_fields= list_display
    search_fields= list_display
    ordering= ['-fastqfile']
    actions = [actions.export_as_csv_action("CSV Export", fields= list_display)]
    class Media:
        js = ("javascript/list_filter_collapse.js",)

class TestfileAdmin(admin.ModelAdmin):
    list_display = ['fileid', 'file', 'file_link']
admin.site.register(Testfile, TestfileAdmin)


" ----------------------------[ Registration ]-------------------------------- "

admin.site.register(FilingOrder, FilingOrderAdmin) ## These are the classes (tables) defined in models.py
admin.site.register(Contacts, ContactsAdmin) ## These are the classes (tables) defined in models.py
admin.site.register(Projects, ProjectsAdmin)
admin.site.register(SampleSources, SampleSourcesAdmin)
admin.site.register(Organisms, OrganismsAdmin)
admin.site.register(Molecules, MoleculesAdmin)
admin.site.register(Samples, SamplesAdmin)
admin.site.register(ProjectSamples, ProjectSamplesAdmin)
admin.site.register(ExpDesign, ExpDesignAdmin)
admin.site.register(ExpVariables, ExpVariablesAdmin)
admin.site.register(ExpValues, ExpValuesAdmin)
admin.site.register(Barcodes, BarcodesAdmin)
admin.site.register(LibraryTypes, LibraryTypesAdmin)
admin.site.register(Libraries, LibrariesAdmin)
admin.site.register(SolexaLims, SolexaLimsAdmin)
admin.site.register(Sequencers, SequencersAdmin)
admin.site.register(Fastqfiles, FastqfilesAdmin)
admin.site.register(ViewDemuxReport, ViewDemuxReportAdmin)
admin.site.register(Lib2Seq, Lib2SeqAdmin)
admin.site.register(sblab.models.ViewMaxInitials, ViewMaxInitialsAdmin)
admin.site.register(ViewBamqc, ViewBamqcAdmin)
admin.site.register(SamtoolsIdxstats, SamtoolsIdxstatsAdmin)
admin.site.register(ViewLibraryServiceFastq, ViewLibraryServiceFastqAdmin)
admin.site.register(Fastqc, FastqcAdmin)

" ------------------------------------------------------------------------------ "
