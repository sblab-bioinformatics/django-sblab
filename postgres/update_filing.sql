-- Function: public.update_filing_order()

-- DROP FUNCTION public.update_filing_order();

CREATE OR REPLACE FUNCTION public.update_filing_order()
  RETURNS text AS
$BODY$

"""
Remove rows in filing_order not prepsent in pg_tables and insert rows in filing_order found 
in pg_tables.

In other words, makes sure that filing_order contains all and only the table names in the 
main schema.

Column "filing_order" gets NULL value when rows are inserted

"""

USE_SCHEMA= 'main' ## schemaname in pg_tables to query 

deleted_rows= []
inserted_rows= []


missing_row= plpy.execute("""
    select tablename 
    from pg_tables left join filing_order on 
        pg_tables.tablename = filing_order.table_name
    where filing_order.table_name is null and
    pg_tables.schemaname = %s 
    """ %(plpy.quote_literal(USE_SCHEMA) ))
if missing_row.nrows() > 0:
    for i in range(0, missing_row.nrows()):
        xrow= missing_row[i]['tablename']
        plpy.execute("""
            insert into filing_order values (null, %s)
            """ %( plpy.quote_literal(xrow) )
            )
        inserted_rows.append(xrow)
extra_row= plpy.execute("""
    select table_name 
    from filing_order left join pg_tables on 
        filing_order.table_name = pg_tables.tablename
    where pg_tables.tablename is null
    """)
    
if extra_row.nrows() > 0:
    for i in range(0, extra_row.nrows()):
        xrow= extra_row[i]['table_name']
        plpy.execute("""
            delete from filing_order where table_name = %s
        """ %( plpy.quote_literal(xrow) )
        )
        deleted_rows.append(xrow)
return('Rows deleted: %s; Rows inserted: %s' %('; '.join(deleted_rows), ', '.join(inserted_rows)))
$BODY$
  LANGUAGE plpython3u VOLATILE
  COST 100;
ALTER FUNCTION public.update_filing_order()
  OWNER TO dberaldi;
