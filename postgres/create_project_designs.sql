-- Function: public.create_project_designs()

-- DROP FUNCTION public.create_project_designs();

CREATE OR REPLACE FUNCTION public.create_project_designs()
  RETURNS text AS
$BODY$
    declare 
        sqlstring text;
        sqlcounter text;
        nrows int;
        row_project projects%ROWTYPE;

    begin
    set search_path to materialized_views, main, public, django_admin; -- This will create the matview in the proper schema
    for row_project in select distinct project from projects where is_deprecated is False limit 3
        loop
            sqlstring := 'select project_samples.project, exp_design.sample_id, s_variable, s_value 
                          from exp_design 
                          left join project_samples on exp_design.sample_id = project_samples.sample_id
                          where project_samples.project = ' || quote_literal(row_project.project);

            sqlcounter := 'select count(*) from (' || sqlstring || ') as t';
            execute sqlcounter into nrows;
            if nrows > 0 then
                perform cross_tab(sqlstring, row_project.project, False, True);
            end if;
         end loop;
    return nrows;
    end;
    $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.create_project_designs()
  OWNER TO dberaldi;
