#!/usr/bin/env python3
"""A copied request string outlives its real caller cell and named table owners."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_primitive_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'named-request-string-refcell-closure-detachment'
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext) '
          '-- if pcallcontext.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*')
HELD = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_held_tail* '
        '-- if $base64(text_marker) = $ptascii("DETACHED;") '
        '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, RETURN)
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, HELD).replace('$factory182_', '$primitive200_held_')


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_return_found = $factory182_seek(S_initial,4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S = S_return_found[.COMPLETION = NORMAL]', RETURN,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pvalue* = [pvalue_string,PNULL]',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING n_string) $ptascii("REQUEST-OLD")',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_later]',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN PNULL]) = (pvalue*)',
        '$string_carrier_valid(S,pvalue_string)',
        'S.STRINGDATA[n_string] = $ptascii("REQUEST-OLD")',
        '$value_nodes(pvalue_string) = eps',
        'n_arguments = n_named',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_keys(pmagicmethodcall.ARGUMENTS,0,false,eps) = ([KSTRING $ptascii("first"),KSTRING $ptascii("later")])',
        'S.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT pvalue_string),ENTRY (KSTRING $ptascii("later")) (DIRECT PNULL)]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        '$node_children(S,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 3',
        '$object_body(S.OBJECTS[n_closure]) = REALCLOSURE pfunction_closure.ORIGIN ([DIRECT (PARRAY n_arguments),DIRECT (PSTRING $ptascii("MiSsInG"))]) eps',
        '$node_children(S,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_base.ORIGIN',
        'pclosurescope.CALLED = pclassdesc_called.ORIGIN',
        'pclosurescope.RECEIVER = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_original_cell)',
        '$lookup($global_table_view(S).ENV,$ptascii("alias")) = (n_original_cell)',
        'n_original_cell <- S.REFCELLS',
        '(HCELL n_original_cell) <- S.ALLOCATIONS',
        'S.STORE[n_original_cell] = DEFINED (PINT 99)',
        '$node_children(S,HCELL n_original_cell) = eps',
        '$task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*) = [HARRAY n_named,HOBJECT pmagicmethodcall.OBJECT]',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S.CURRENT) = eps',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;MAGIC;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$closure_state_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_held_found = $primitive200_held_seek(S,4096)',
        'S_held_found.COMPLETION = BUDGET',
        'S_held = S_held_found[.COMPLETION = NORMAL]', HELD.replace('S.', 'S_held.'),
        'S_held.FRAMES = eps',
        '$lookup(S_held.ENV,$ptascii("factory")) = (n_factory_cell)',
        'S_held.STORE[n_factory_cell] = DEFINED (POBJECT n_closure)',
        '$lookup(S_held.ENV,$ptascii("alias")) = eps',
        '$lookup(S_held.ENV,$ptascii("argument")) = (n_slot)',
        '$lookup(S_held.ENV,$ptascii("slot")) = (n_slot)',
        'n_slot =/= n_original_cell',
        'S_held.STORE[n_slot] = DEFINED PNULL',
        '~((HCELL n_original_cell) <- S_held.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_held.ALLOCATIONS)',
        '(HARRAY n_arguments) <- S_held.ALLOCATIONS',
        '$node_children(S_held,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$node_children(S_held,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_held),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_held),HARRAY n_arguments) = 1',
        'S_held.ARRAYS[n_arguments] = S.ARRAYS[n_arguments]',
        'S_held.STRINGDATA[n_string] = $ptascii("REQUEST-OLD")',
        '$string_carrier_valid(S_held,pvalue_string)',
        '$factory182_output(S_held.EVENTS) = $ptascii("SHIFT;MAGIC;OWNER;RETURN;")',
        '$call_descriptors_valid(S_held)', '$closure_state_valid(S_held)',
        '$class_state_valid(S_held)', '$gc_state_valid(S_held)', '$heap_valid($heap_graph(S_held))',
        '~$magic_method_cv_capture(S_held,n_original_cell)',
        '~$magic_method_value(S,pvalue_string)',
        '~$magic_method_flat_array(S,n_arguments)',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PSTRING $ptascii("REQUEST-OLD")),KNOWN PNULL]) = eps',
        '$magic_method_collected_values(S[.STRINGDATA = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN PNULL]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[REFERENCE n_original_cell,KNOWN PNULL]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,[phpType7_later,phpType7_first],[KNOWN pvalue_string,KNOWN PNULL]) = eps',
        'S_split = $drive_steps(S_held,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_held,8194)', 'S_full = S_done',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
