#!/usr/bin/env python3
"""Actual all-named argument table retained solely by the native named buffer."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_named_object_cv_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-named-first-object-buffer-last-owner'
FRONT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_tail* '
         '-- if $base64(text_marker) = $ptascii("BUFFER;") '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        'pcallcontext.ARGC = 2',
        '$magic_named_keys(pmagicmethodcall.ARGUMENTS,0,false,eps) = ([KSTRING $ptascii("first"),KSTRING $ptascii("later")])',
        'n_arguments = n_named',
        'pvalue* = [POBJECT n_old,PINT 9]',
        '$magic_named_tables([KSTRING $ptascii("first"),KSTRING $ptascii("later")],pvalue*,$array_empty(),$array_empty()) = (parray_arguments,parray_named)',
        'S.ARRAYS[n_arguments] = parray_arguments',
        'S.ARRAYS[n_named] = parray_named',
        '$magic_named_buffer(S,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '(HARRAY n_named) <- S.ALLOCATIONS',
        '$node_children(S,HARRAY n_named) = [HOBJECT n_old]',
        '$heap_owners($heap_graph(S),HARRAY n_named) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        'S.OBJECTS[n_old] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_old) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S).ENV,$ptascii("payload")) = (n_payload_cell)',
        'S.STORE[n_payload_cell] = DEFINED (POBJECT n_new)',
        'n_old =/= n_new',
        'S.OBJECTS[n_new] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_new) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_new) = 1',
        '$lookup(S.ENV,$ptascii("child")) = (n_child_cell)',
        'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$node_children(S,HOBJECT n_child) = [HARRAY n_empty]',
        'n_empty =/= n_named',
        'S.ARRAYS[n_empty] = $array_empty()',
        '$gc_immutable_array(S,n_empty)',
        '$heap_owners($heap_graph(S),HOBJECT n_child) = 1',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S.CURRENT) = eps',
        '$call_receiver_roots(pcallcontext) = eps',
        '$task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*) = [HARRAY n_named,HOBJECT pmagicmethodcall.OBJECT]',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;MiSsInG|OLD|9|PRIVATE|Base194|Derived194|Base194::__call;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$magic_named_buffer(S,pmagicmethodcall,n_arguments,n_empty,pvalue*)',
        '~$magic_named_frame(S,pcallcontext[.CALLED_CLASS = (pclassdesc_base.ORIGIN)],pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HARRAY n_named) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
