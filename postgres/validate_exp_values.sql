-- Function: public.validate_exp_values()

-- DROP FUNCTION public.validate_exp_values();

CREATE OR REPLACE FUNCTION public.validate_exp_values()
  RETURNS trigger AS
$BODY$
DECLARE
    sqlstring text;
    value_type_array text[];

BEGIN
sqlstring := 'SELECT DISTINCT ARRAY[exp_values.s_value, exp_variables.variable_type]
              FROM exp_values INNER JOIN exp_variables ON exp_values.s_variable = exp_variables.s_variable';

FOR value_type_array IN EXECUTE sqlstring
LOOP
    sqlstring := 'select ' || quote_literal(value_type_array[1]) || '::' || value_type_array[2];
    EXECUTE sqlstring;
END LOOP;
RETURN null;  
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.validate_exp_values()
  OWNER TO dberaldi;
