#!/usr/bin/env python3
"""Check genuine Arrow admission, implicit capture disposal and receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning
import magic_property_realclosure_quiet_get_review_protocol as literal

CATALOGUE = Path(__file__).with_name('magic_property_arrow_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = [
    ('$origin_node(S.SOURCES,porigin_closure) = (NExprArrowFunction phpType14 '
     'phpType4_static phpType4_ref phpType16 phpType18 expression_arrow metadata_closure)')
    if check.startswith('$origin_node(S.SOURCES,porigin_closure) = ') else check
    for check in literal.FRONT
] + r'''
pfunction_closure.BODY = pcpath_closure ++ [PCFIELD 5]
$pparrow_template(pfunction_closure)
$arrow_line(pfunction_closure.CODE.EXPRESSIONS,pfunction_closure.BODY) = (z_arrow)
$origin_node(S.SOURCES,PORIGIN n_unit_closure pfunction_closure.BODY) = (expression_arrow)
expression_arrow = NExprVariable (BYTES text_payload) metadata_payload
ptbytes_payload = $base64(text_payload)
ptbytes_payload = $ptascii("payload")
$closure_lexicals(pfunction_closure.CODE.EXPRESSIONS) = [IMPLICIT ptbytes_payload z_implicit]
$pparrow_remove($pparrow_discover(expression_arrow),$pparrow_param_names(phpType16)) = [ptbytes_payload]
~$property_magic_cv_realclosure(S,n_closure)
'''.strip().splitlines()

AUTHORITY = r'''
$property_magic_cv_arrow(S,n_closure)
~$property_magic_cv_arrow(S,|S.OBJECTS|)
~$property_magic_cv_arrow(S[.SOURCES = eps],n_closure)
~$property_magic_cv_arrow(S[.CLOSURETEMPLATES = eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_closure],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps)],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure eps eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload),DIRECT (POBJECT n_payload)]) eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([ALIAS n_payload_cell]) eps],n_closure)
$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([UNINITIALIZED]) eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) ([{ORIGIN porigin_closure,CELL n_payload_cell}])],n_closure)
~$property_magic_cv_arrow(S[.TODO = (AT porigin_closure (CLOSURE_CAPTURE n_closure 1)) :: S.TODO],n_closure)
pframe_capture = {SILENCES eps,LOCALS eps,TODO ([CLOSURE_CAPTURE n_closure 1]),ORIGIN (porigin_closure),HELD eps,CONTEXT eps,RETIREDOWNERS eps,BORROWEDREAD eps,OBJECTCAST eps,CONSTCONTEXT eps}
~$property_magic_cv_arrow(S[.FRAMES = [pframe_capture]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURESCOPES = [{OBJECT n_closure,LEXICAL pmethoddesc.OWNER,CALLED pmethoddesc.OWNER,RECEIVER eps,CREATION eps}]],n_closure)
~$property_magic_cv_arrow(S[.CLOSUREBINDINGS = [{OBJECT n_closure,SITE ppropertyempty.SITE,SOURCE n_receiver,LEXICAL eps,CALLED eps,RECEIVER eps}]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = eps],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache,pclosurecache]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.OBJECT = n_receiver]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.SOURCE = (n_receiver)]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.SCOPE = eps]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.CACHE = eps]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]],n_closure)
S_badbody = S[.CLOSURETEMPLATES = [pfunction_closure[.BODY = pcpath_closure ++ [PCFIELD 6]]]]
~$property_magic_cv_arrow(S_badbody,n_closure)
S_nomarker = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = [CODEIMPLICIT pfunction_closure.BODY ptbytes_payload z_implicit]]]]
$closure_live_object_valid(S_nomarker,n_closure) /\ ~$property_magic_cv_arrow(S_nomarker,n_closure)
S_explicit = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = [CODELEXICAL pfunction_closure.BODY ptbytes_payload false z_implicit,CODEARROW pfunction_closure.BODY z_arrow]]]]
$closure_live_object_valid(S_explicit,n_closure) /\ $pparrow_template(S_explicit.CLOSURETEMPLATES[0])
~$property_magic_cv_arrow(S_explicit,n_closure)
S_badname = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = [CODEIMPLICIT pfunction_closure.BODY $ptascii("different") z_implicit,CODEARROW pfunction_closure.BODY z_arrow]]]]
$closure_live_object_valid(S_badname,n_closure) /\ $pparrow_template(S_badname.CLOSURETEMPLATES[0])
~$property_magic_cv_arrow(S_badname,n_closure)
S_generator = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_closure,NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 (NExprYield ABSENT (NExprVariable (BYTES text_payload) metadata_payload) metadata_closure) metadata_closure)]]]
$function_generator(S_generator,pfunction_closure) /\ ~$property_magic_cv_arrow(S_generator,n_closure)
'''.strip().splitlines()

CV_FRONT = r'''
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_empty_capture(S,ppropertyempty)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S_badbody,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_nomarker,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_explicit,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_badname,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_generator,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_closure)')
CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + CV_FRONT + literal.LIFETIME + literal.NORMAL + literal.DONE + [
            'S_done.STORE[n_destination] = DEFINED (PBOOL false)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;FALSE;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + literal.LITERAL_FRONT + literal.LIFETIME + literal.THROW + literal.DONE + [
            r'S_done.STORE[n_destination] = DEFINED (PINT 42) /\ $lookup(S_done.ENV,$ptascii("failure")) = eps',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(owning.__file__), owning.CATALOGUE,
                  Path(literal.__file__), literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=literal.render)
