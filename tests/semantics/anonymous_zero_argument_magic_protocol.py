#!/usr/bin/env python3
"""Real zero-send capture, empty argument packing, method frame and retirement."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_zero_argument_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-call-zero-send-inherited-child'
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'MAGIC_METHOD_TARGET pmagicmethodcall n_arguments pvalue*')
RAW = ('S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin_site? z) :: ptask_rawtail*')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $zero192_raw_front(pstate) : bool
def $zero192_raw_front(S) = true -- if RAW
def $zero192_raw_front(S) = false -- otherwise
dec $zero192_raw_seek(pstate, nat) : pstate
def $zero192_raw_seek(S, 0) = S
def $zero192_raw_seek(S, n) = S -- if $(n > 0) /\ $zero192_raw_front(S)
def $zero192_raw_seek(S, n) = $zero192_raw_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$zero192_raw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $zero192_raw_seek(S, n) = S -- otherwise
'''.replace('RAW', RAW)


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_raw_found = $zero192_raw_seek(S_initial,2048)',
        'S_raw_found.COMPLETION = BUDGET', 'S_raw = S_raw_found[.COMPLETION = NORMAL]',
        RAW.replace('S.TODO', 'S_raw.TODO'),
        r'porigin_site? = (pmagicmethodcall.SITE) /\ z = pmagicmethodcall.LINE',
        'ptask_rawtail* = METHOD_RESULT :: pmagicmethodcall.TAIL',
        'pmagicmethodcall.ARGUMENTS = eps',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        '$magic_method_capture(S_raw,pmagicmethodcall)',
        '$magic_method_raw_valid(S_raw,pmagicmethodcall)',
        '$call_arguments_valid(S_raw,(pmagicmethodcall.SITE),0,eps,eps,0)',
        '$target_nodes(MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        '~$call_task_valid(S_raw,CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE)',
        'S_packed_found = $drive_steps(S_raw,1)',
        'S_packed_found.COMPLETION = BUDGET',
        'S_packed = S_packed_found[.COMPLETION = NORMAL]',
        'S_packed.TODO = (CALL_ARGS (MAGIC_METHOD_TARGET pmagicmethodcall n_arguments eps) eps 2 ([KNOWN (PSTRING pmagicmethodcall.NAME),KNOWN (PARRAY n_arguments)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: pmagicmethodcall.TAIL',
        'n_arguments = |S_raw.ARRAYS|',
        '|S_packed.ARRAYS| = $(|S_raw.ARRAYS| + 1)',
        'S_packed.ARRAYS[n_arguments] = $array_empty()',
        '(HARRAY n_arguments) <- S_packed.ALLOCATIONS',
        '$node_children(S_packed,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_packed),HARRAY n_arguments) = 1',
        '$magic_method_pending(S_packed,pmagicmethodcall,n_arguments,eps)',
        '$target_function(S_packed,MAGIC_METHOD_TARGET pmagicmethodcall n_arguments eps) = (pmethoddesc.FUNCTION)',
        '$call_descriptors_valid(S_packed)', '$heap_valid($heap_graph(S_packed))',
        'S_found = $factory182_seek(S_packed,2048)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pvalue* = eps', 'pcallcontext.FUNCTION = pmagicmethodcall.METHOD',
        'pcallcontext.ARGC = 2',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S.ARRAYS[n_arguments] = $array_empty()',
        '$node_children(S,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 1',
        '$call_receiver_roots(pcallcontext) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_method_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,eps)',
        '$factory182_output(S.EVENTS) = $ptascii("MAGIC;1;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$magic_method_frame(S,pcallcontext[.CALLED_CLASS = (pclassdesc_base.ORIGIN)],pframe,pframe_tail*,pmagicmethodcall,n_arguments,eps)',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
