-- Function: public.get_library_id(text)

-- DROP FUNCTION public.get_library_id(text);

CREATE OR REPLACE FUNCTION public.get_library_id(x text)
  RETURNS text AS
$BODY$
""" Get the library ID from the string x. The library ID is extracted by:
- Split x at each '.' (lib IDs can't contain dots)
- Match each item against the list of library IDs in libraries.library_id
- Return the resulting item or NULL if no match is found or more than one match is found

EXAMPLE
select get_library_id('ds019_ctrl_24h.slx-5010') => ds019_ctrl_24h
select get_library_id('nonsense.ds019_ctrl_24h.fq.gz') => ds019_ctrl_24h
select get_library_id('ds019_ctrl_24h.ds020_ctrl_24h') => NULL (More than one lib id found)
select get_library_id('nonsense') => NULL
"""

xlist= set(x.split('.'))

" Get all library IDs"
cur= plpy.execute('select library_id from libraries')
libids= []
for i in range(0, cur.nrows()):
    libids.append(cur[i]['library_id'])

xmatch= []
for m in xlist:
    " Match each item in xlist against all lib IDs"
    if m in libids:
        xmatch.append(m)
        
if xmatch == [] or len(xmatch) > 1:
    return(None)
if len(xmatch) == 1:
    return(xmatch[0])

$BODY$
  LANGUAGE plpython3u IMMUTABLE
  COST 100;
ALTER FUNCTION public.get_library_id(text)
  OWNER TO dberaldi;
