-- Function: create_crosstab_project_designs()

-- DROP FUNCTION create_crosstab_project_designs();

CREATE OR REPLACE FUNCTION create_crosstab_project_designs()
  RETURNS trigger AS
$BODY$
    declare 
        sqlstring text;
        sqlcounter text;
        nrows int;
        row_project projects%ROWTYPE; -- Name of the project
        ct_project text; -- Name of cross tab table produced from exp_design
        view_project text; -- Name for final view
    begin
    set search_path to materialized_views, main, public, django_admin; -- This will create the matview in the proper schema
    for row_project in select distinct project from projects where is_deprecated is False
        loop
        /* MEMO: Each table joined in triggered function must have a trigger associated 
         otherwise the cross-tabs will be outdated !!*/
            ct_project := 'exp_design_' || row_project.project;
            view_project := 'view_' || row_project.project;
            sqlstring := 'select distinct 
                                 project_samples.project,
                                 exp_design.sample_id,
                                 exp_design.s_variable, -- For cross_tab: This must be second last column 
                                 exp_design.s_value     -- For cross_tab: This must be last column
                          from exp_design inner join project_samples on exp_design.sample_id = project_samples.sample_id 
                          where project_samples.project = ' || quote_literal(row_project.project);
            sqlcounter := 'select count(*) from (' || sqlstring || ') as t';
            execute sqlcounter into nrows;
            if nrows > 0 then
                perform cross_tab(sqlstring, ct_project, False, True, cascade := True);
                execute 'alter table ' || quote_ident(ct_project) || ' add column id serial';
                execute 'comment on table ' || quote_ident(ct_project) || $$ is 'Table created by create_crosstab_project_designs() triggered by changes on exp_design (and possibly ther tables)'$$;
                execute 'drop view if exists ' || quote_ident(view_project) || ' cascade;';
                execute 'create view ' || quote_ident(view_project) || ' as(
                     select distinct ' || quote_ident(ct_project) || '.*,
                         samples.organism,
                         samples.source_name,
                         samples.molecule,
                         libraries.library_id,
                         libraries.library_type
                     from ' || quote_ident(ct_project) || ' inner join samples on samples.sample_id = ' || quote_ident(ct_project) || '.sample_id
                     left join libraries on libraries.sample_id = samples.sample_id)';
                execute 'comment on view ' || quote_ident(view_project) || $$ is 'Table created by create_crosstab_project_designs() triggered by changes on exp_design (and possibly ther tables)'$$;
            end if;
         end loop;
    return null;
    end;
    $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION create_crosstab_project_designs()
  OWNER TO dberaldi;
