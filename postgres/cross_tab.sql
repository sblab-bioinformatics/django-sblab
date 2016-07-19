-- Function: public.cross_tab(text, text, boolean, boolean, boolean)

-- DROP FUNCTION public.cross_tab(text, text, boolean, boolean, boolean);

CREATE OR REPLACE FUNCTION public.cross_tab(sql_query text, dest_table text, temp boolean DEFAULT true, overwrite boolean DEFAULT true, cascade boolean DEFAULT false)
  RETURNS text AS
$BODY$
""" -------------------------[ cross_tab-4.1 ]------------------------------- 

DESCRIPTION
Returns a crosstab table from a normalized table (similar to MS Access's 
pivot table). Table is created as TEMPORARY (new in 4.1).
Requirements: An SQL returning a normalized table with at least three 
columns corresponding to (in this order!) one or more row headers, 
column header, and value. E.g.

       |------- row headers ------| |-- 2nd last--]  |-- last --|
SELECT row_header, [opt.row_head 2], column_header,      value    FROM etc... ;

Each combination of row header(s) and column header should be unique.

Note: cross_tab() will re-order the table produced by sql_query by row header
(left to right) then by column header.

ARGUMENTS
sql_query:  A string containing an SQL statement returning the normalized 
            table to transform. See above how columns should be selected.

dest_table: Name of the output table that will store the cross-tab query.

temp:       True/False should the output table be created as TEMPORARY? 
            (Defualt True).

overwrite:  True/False. Overwrite existing dest_table? (Default True)

cascade:    Issues a DROP ... CASCADE to drop the existing cross tab table. Ignored 
            if overwrite is False. Default False.

TODO

 - Avoid string interpolation to compile SQLs.
 - Better coping with inout queries returning 0 rows. Currently no table is created and a message
   is returned. Better to create an empty table instead?
 - DONE: Use plpy.quote_ident() to properly quote table and column names to respect capitalization

"""

import sys
import datetime
import os
import tempfile

sql_query2= sql_query.rstrip()
sql_query2= sql_query2.rstrip(';')

" ------------------------[ Define functions ]------------------------------- "

def get_query_colnames(sql_query):
    """ Return a list with the column names in the query string sql_query.
    The order of names in the list is the same as in the query.
    """
    sql_query= sql_query.rstrip()
    sql_query= sql_query.rstrip(';')
    qry_table_colnames= 'DROP TABLE IF EXISTS colnames; CREATE TEMP TABLE colnames ON COMMIT DROP AS (SELECT * FROM (' + sql_query + ') AS t WHERE 1 = 2);'
    plpy.execute(qry_table_colnames)
    qry_colnames= "select * from information_schema.columns where table_name = 'colnames' order by ordinal_position;"
    colnames_results= plpy.execute(qry_colnames)
    nrows= colnames_results.nrows()
    colnames= []
    for i in range(0, nrows):
         colnames.append(colnames_results[i]["column_name"])
    return(colnames)

def plpy_get_line(cur, i, colnames):
    """ Return line number i from the plpy result object cur. in the column order given in list colnames.
    Note: The colnames for query q can be obtained with can be obtained with get_query_colnames(q).
    E.g.
    q= 'select a, b, c from t1'  ## Where first (i= 0) row has values: a= 1, b= 2, c= 3
    cur= plpy.execute(q)
    colnames= get_query_colnames(q)   ## >>> ['a', 'b', 'c']
    plpy_get_line(cur, 0, colnames)   ## >>> [1, 2, 3]
    """
    line= []
    for x in colnames:
        line.append(cur[i][x])
    return(line)

## Some functions for crosstabing
def reformat(x):
    " Substitute python's None with empty string or False if datatype is boolean "
    " Substitute date-times to isoformat "
    if x is None:
        if col_types[vi] == 'boolean':
            return(False)
        else:
            return('')
    elif type(x) == type(datetime.datetime.now()):
        return(datetime.date.isoformat(x))
    else:
        return(x)

def write_line(lst_line):
    " Reformat each block of input lines to a single line to be sent to outfile "
    outlinex= [reformat(x) for x in lst_line]
    line= '\t'.join([str(x) for x in outlinex]) + '\n'
    outfile.write(line)

def check_duplicate():
    " Stop execution if two rows have the same Row and column header (i.e. there are multiple values/row) "
    if (line is not None) and (current_row_heading == [line[i] for i in ri]) and (current_col_heading == line[ci]):
        sys.exit('Duplicate found for line\n' + str(line))

" -------------------[ Get input table column names and datatypes ]--------- "

if cascade is True:
    drop_cascade= 'CASCADE'
else:
    drop_cascade= ''

if overwrite is True:
    drop_sql= 'DROP TABLE IF EXISTS %s %s' %(plpy.quote_ident(dest_table), drop_cascade, )
    plpy.execute(drop_sql)

" Test if destination table already exists."
table_exists= 0
try:
    qry_test= 'SELECT * FROM %s LIMIT 1;' %(plpy.quote_ident(dest_table)) 
    table_exists= plpy.execute(qry_test)
    table_exists= 1
except:
    pass
if table_exists == 1:
    sys.exit('Destination table %s already exists.' %(plpy.quote_ident(dest_table)))

" Prepare temp output file "
outdir= tempfile.gettempdir()
outf= os.path.join(outdir, 'tmp_query_cross_tab.txt')
outfile= open(outf, 'w')

qry_input_table= 'CREATE TEMP TABLE tmp_cross_tab_input AS (SELECT * FROM (' + sql_query2 + ') AS t1);'
cur= plpy.execute(qry_input_table)

## w/o distinct it returns each name twice (!?)
qry_names_ord= """SELECT DISTINCT column_name, ordinal_position, data_type
  FROM information_schema.columns 
  WHERE table_name like 'tmp_cross_tab_input' 
  ORDER BY ordinal_position;"""
cur= plpy.execute(qry_names_ord)
## cur.execute(qry_names_ord)
nrows= cur.nrows()

col_names= []
for i in range(0, nrows):
    col_names.append(cur[i]['column_name'])
col_types= []
for i in range(0, nrows):
    col_types.append(cur[i]['data_type'])

" Replace NULL and empty string in future column names in order to avoid invalid column names "
sql_null= """SELECT * FROM (%s) AS t WHERE t.%s::text IS NULL OR t.%s::text = '' LIMIT 1;""" %(sql_query2, plpy.quote_ident(col_names[-2]), plpy.quote_ident(col_names[-2])) 
cur= plpy.execute(sql_null)
nrows= cur.nrows()
if nrows > 0:
    sys.exit("""cross_tab(): One or more values in the second last column (%s) contain a NULL or empty string.
Null and empty strings will not be valid column names for the output crosstab.
Add a CASE...WHEN or replace in the input query to avoid null and empty.
Found by:
%s
""" %(plpy.quote_ident(col_names[-2]), sql_null))

## Indexes of headers:
ri_s= 0 ## Row header starts
ri_e= len(col_names)-2 ## Row header finishes
ri= range(ri_s, ri_e)
ci= -2
vi= -1

## Default header names:
row_header= ', '.join([plpy.quote_ident(x) for x in col_names[ri_s:ri_e]]) ## All columns but last two
column_header= plpy.quote_ident(col_names[ci]) ## Second last columns  in input query
value= '"' + str(col_names[vi]) + '"' ## Last columns

## String to plug in SELECT statement
row_header__col_header__value= ', '.join([row_header, column_header + '::text', value])

## Collect column header names
qry_column_header= 'SELECT DISTINCT ' + column_header + '::text AS colheader FROM tmp_cross_tab_input;'
cur= plpy.execute(qry_column_header)
nrows= cur.nrows()

headers= []
for i in range(0, nrows):
    headers.append(cur[i]['colheader'])

headers.sort()

## Dictionary with position of each column header
column_dict={}
i= len(ri) ## Start from after the row_headings
for key in headers:
    column_dict[key] = i
    i += 1

## Prepare CREATE TABLE crosstab table

if temp is True:
    istemp= 'TEMP'
elif temp is False:
    istemp= ''
else:
    sys.exit('Unexpected value for arg temp: %s' %(temp))

qry_create_crosstab= 'CREATE ' + istemp + ' TABLE ' + plpy.quote_ident(dest_table) + '(\n  '
for i in ri:
    col= plpy.quote_ident(col_names[i]) ## '"' + col_names[i] + '"'
    var= col_types[i]
    qry_create_crosstab= qry_create_crosstab + col + ' ' + var + ',\n '
qry_create_crosstab= qry_create_crosstab.rstrip(',\n ')

for col in headers:
    col_def=  ',\n  ' +  plpy.quote_ident(col) + ' ' + col_types[vi]
    qry_create_crosstab= qry_create_crosstab + col_def
qry_create_crosstab= qry_create_crosstab + ');'

cur= plpy.execute(qry_create_crosstab)
## cur.execute(qry_create_crosstab)

## Order input query
qry_input_ordered= 'SELECT ' + row_header__col_header__value + ' FROM tmp_cross_tab_input ORDER BY ' + row_header + ', '+ column_header +';'
cur= plpy.execute(qry_input_ordered)
nrows= cur.nrows()
colnames= get_query_colnames(qry_input_ordered)

qry_delete_tmp= 'DROP TABLE tmp_cross_tab_input;'
plpy.execute(qry_delete_tmp)


" --------------------------[ Start cross-tabulation ]----------------------- "
if nrows == 0:
    " This is for when input queries returns zero rows "
    return('Table %s not created: Zero rows returned from input query.' %(dest_table) )
else:
    n= 0 
    line= plpy_get_line(cur, n, colnames)
    n += 1
    current_row_heading= [line[i] for i in ri]
    current_col_heading= line[ci]
    current_value= line[vi]
    outline= [None] * (len(headers)+ri_e)  ## List to hold row heading and crossed values
    for i in ri:
        " Replace in empty outline the row headings "
        outline[i]=current_row_heading[i]
    value_pos= column_dict[current_col_heading]
    outline[value_pos]= current_value 
    
    for n in range(1, nrows):
        line= plpy_get_line(cur, n, colnames)
        check_duplicate()
        next_row_heading= [line[i] for i in ri]
        next_col_heading= line[ci]
        next_value= line[vi]
        if next_row_heading == current_row_heading:
            value_pos= column_dict[next_col_heading]
            outline[value_pos]= next_value
        else:
            write_line(outline)
            current_row_heading = next_row_heading
            current_col_heading = next_col_heading
            outline= [None] * (len(headers)+ri_e)  ## Reset empty list to hold row heading and crossed values
            for i in ri:
                " Replace in empty outline the row headings "
                outline[i]=current_row_heading[i]
            value_pos= column_dict[current_col_heading]
            outline[value_pos]= next_value
write_line(outline)
outfile.close()

qry_copy= 'COPY ' + plpy.quote_ident(dest_table) + ' FROM ' + "E'" + outf + "' WITH CSV DELIMITER E'\t';"
plpy.execute(qry_copy)

os.remove(outf)

qry_comment= 'COMMENT ON TABLE ' + plpy.quote_ident(dest_table) + ' IS ' + "$comment$ Crosstab table generated by cross_tab() from input query: " + sql_query2 + " $comment$;"
plpy.execute(qry_comment)

return('Cross-tab table written to "' + dest_table + 
       '".\nThe following SQL commands have been executed:\n\n' +
       qry_input_table + '\n\n' + qry_names_ord + '\n\n' + 
       qry_column_header + '\n\n' + qry_create_crosstab + '\n\n' + qry_input_ordered +'\n\n' + 
       qry_copy + '\n\n' + qry_comment)

$BODY$
  LANGUAGE plpython3u VOLATILE
  COST 100;
ALTER FUNCTION public.cross_tab(text, text, boolean, boolean, boolean)
  OWNER TO dberaldi;
