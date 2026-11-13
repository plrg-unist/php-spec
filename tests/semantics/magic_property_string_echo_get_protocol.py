#!/usr/bin/env python3
"""Check canonical-string Get in genuine singleton echo source and continuations."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_string_echo_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
LINE = next(i for i, line in enumerate(ROW['source'].splitlines(), 1)
            if line == 'echo $o->$name;')

CASES = {
    'string-echo-get-entry-and-tail': {
        'source': ROW['source'],
        'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
                  '-- if S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_property) :: '
                  '(DIM_FETCH z_property) :: (ORIGIN_RETURN (porigin_echo)) :: '
                  '(AT porigin_site (EMIT z_echo)) :: ptask_tail*'),
        'checks': [
            'S.ORIGIN = (porigin_site)',
            'S.EVENTS = eps /\\ z_property = ' + str(LINE) + ' /\\ z_echo = ' + str(LINE),
            'porigin_echo = PORIGIN n_unit pcpath_echo',
            'porigin_site = PORIGIN n_unit (pcpath_echo ++ [PCFIELD 0,PCINDEX 0])',
            '$origin_node(S.SOURCES,porigin_site) = (expression)',
            '$origin_node(S.SOURCES,porigin_echo) = (NStmtEcho (SEQUENCE ([expression])) metadata_echo)',
            'z_echo = $echo_expression_line(S,expression)',
            '$property_get_string_echo_site(S,porigin_site) = (porigin_echo)',
            '$property_get_string_consumer_site(S,porigin_site,expression)',
            '~$property_get_string_consumer(NStmtEcho (SEQUENCE ([expression])) metadata_echo,expression)',
            '$property_get_method(S,n_receiver) = (pmethoddesc)',
            'pfunction = pmethoddesc.FUNCTION',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
            '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
            '$property_get_string_method(S,pmethoddesc)',
            'ppropertyget = {SITE porigin_site, NAME $ptascii("12"), LINE z_property, OBJECT n_receiver, CLASS pmethoddesc.OWNER, METHOD pfunction.ORIGIN, DECL eps}',
            '$property_get_string_source(S,ppropertyget) /\\ $property_get_cv_name_source(S,ppropertyget)',
            '$property_get_history(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
            'ptask_echo* = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_site (EMIT z_echo)) :: ptask_tail*',
            '$property_get_string_tail(S,ppropertyget,ptask_echo*)',
            '$property_get_plan(S) = (ppropertyget)',
            '~$property_ref_demand(S)',
            '$property_get_factory(S,ppropertyget) = eps /\\ ~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget)',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
            '$property_get_string_echo_site(S,pfunction.ORIGIN) = eps',
            '~$property_get_string_consumer_site(S,porigin_site,NScalarInt (INTEGER 7) eps)',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_echo),AT porigin_site (EMIT $(z_echo + 1))])',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_echo),AT porigin_echo (EMIT z_echo)])',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_echo),EMIT z_echo])',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_echo),DISCARD])',
            '$property_get_plan(S[.TODO = [PROPERTY_NAME (POBJECT n_receiver) z_property,DIM_FETCH z_property,ORIGIN_RETURN (porigin_echo),AT porigin_site (EMIT $(z_echo + 1))]]) = eps',
            '$source_unit(S.SOURCES,n_unit) = (pcunit)',
            'pcunit.AST = PROGRAM statement_all*',
            'pcpath_echo = [PCINDEX 3]',
            'n_after = $nabs($(|statement_all*| - 4))',
            'pcunit_comma = $pcsource(n_unit,PROGRAM (statement_all*[0:3] ++ [NStmtEcho (SEQUENCE ([expression,expression])) metadata_echo] ++ statement_all*[4:n_after]))',
            'S_comma = S[.SOURCES = [pcunit_comma]]',
            '$property_get_string_echo_site(S_comma,porigin_site) = eps',
            '~$property_get_string_consumer_site(S_comma,porigin_site,expression)',
            '$property_get_plan(S_comma) = eps',
            '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 7))',
            '~$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
            '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
            'PhpStep: S ~> S_call',
            '$property_get_capture_tail(S_call,ppropertyget) = ptask_echo*',
            '$property_get_capture(S_call,ppropertyget) /\\ $property_get_tail_valid(S_call,ppropertyget)',
            '$property_get_pending_call(S_call,PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN,porigin_site)',
            '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S_call) /\\ $property_state_valid(S_call) /\\ $heap_valid($heap_graph(S_call))',
            'S_zero = $drive_steps(S_call,0)',
            'S_zero = S_call[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            'S_one.COMPLETION = BUDGET /\\ S_one.TODO = [TYPE_RECEIVE pfunction.ORIGIN 0]',
            '$typed_receive_valid(S_one,pfunction.ORIGIN,0)',
            '$call_descriptors_valid(S_one) /\\ $property_state_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
            'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("S;"),OUTPUT $ptascii("7"),OUTPUT $ptascii(";"),OUTPUT $ptascii("S;"),OUTPUT $ptascii("7"),OUTPUT $ptascii(";DONE;")]',
            '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
