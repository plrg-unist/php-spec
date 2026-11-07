#!/usr/bin/env python3
"""Keyword invocation selects a real receiver and preserves an old request value."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_invokable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
DYNAMIC = ('S.TODO = (CALL_DYNAMIC porigin_producer z_init z_call) :: ptask_dynamic_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_selector) -- if S.CURRENT = (pcallcontext_caller)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_send 1 ([KNOWN (PBOOL false)])) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN pvalue_sent -- if S.CURRENT = (pcallcontext_send)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, DYNAMIC)
for label, front in [('producer', PRODUCER), ('send', SEND), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$kwinvoke236_' + label + '_')
PREFIX += r'''
dec $kwinvoke236_outer_one(ptask) : pmagicmethodcall?
def $kwinvoke236_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $kwinvoke236_outer_one(ptask) = eps -- otherwise
dec $kwinvoke236_outer(ptask*) : pmagicmethodcall?
def $kwinvoke236_outer(eps) = eps
def $kwinvoke236_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $kwinvoke236_outer_one(ptask) = (pmagicmethodcall)
def $kwinvoke236_outer(ptask :: ptask_tail*) = $kwinvoke236_outer(ptask_tail*) -- if $kwinvoke236_outer_one(ptask) = eps
dec $kwinvoke236_init_at(pcodeexpr, pcpath) : bool
def $kwinvoke236_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $kwinvoke236_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $kwinvoke236_cut(pcodeexpr*, pcpath) : pcodeexpr*
def $kwinvoke236_cut(eps, pcpath) = eps
def $kwinvoke236_cut(pcodeexpr :: pcodeexpr_tail*, pcpath) = $kwinvoke236_cut(pcodeexpr_tail*, pcpath) -- if $kwinvoke236_init_at(pcodeexpr, pcpath)
def $kwinvoke236_cut(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $kwinvoke236_cut(pcodeexpr_tail*, pcpath) -- if ~$kwinvoke236_init_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    row = ROWS[case['id']]
    parent = case['id'].endswith('parent-instance')
    allocated = 'peerbase236' if parent else 'peerscope236'
    prefix = 'CTOR:PeerBase236:PeerChild236:8;CTOR:PeerBase236:' + ('PeerBase236' if parent else 'PeerScope236') + ':3;'
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', DYNAMIC,
        '$kwinvoke236_outer(ptask_dynamic_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer', 'S.ORIGIN = (porigin_producer)',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_new (SEQUENCE phpType7_real*) metadata_producer',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$magic_method_keyword_new_invokable_call(expression_producer)', '$magic_method_context_call(expression_producer)',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = eps',
        '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$class_named(S.CLASSNAMES,$ptascii("' + allocated + '")) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope236")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild236")) = (porigin_called)', 'porigin_allocated =/= porigin_called',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        'pcallcontext_caller.RECEIVER = (n_caller)', 'n_caller =/= n_selector',
        '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
        '$object_class_origin(S,n_selector) = (porigin_allocated)',
        '$effective_method(S,porigin_allocated,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc)',
        '$effective_method(S,porigin_called,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc_wrong)',
        'pmethoddesc_wrong.FUNCTION.ORIGIN =/= pmethoddesc.FUNCTION.ORIGIN',
        '$object_invoke_method(S,n_selector) = (pmethoddesc)',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '~$magic_method_plain_instance_source(S,pmethoddesc,phpType7_real*)',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        'S.CODE = [pcode]', '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_new)',
        '$call_task_valid(S,CALL_DYNAMIC porigin_producer z_init z_call)',
        '~$call_task_valid(S,CALL_DYNAMIC porigin_producer $(z_init + 1) z_call)',
        '~$magic_method_context_source(S,eps,porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.LEXICAL_CLASS = eps]),porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.CALLED_CLASS = eps]),porigin_producer,expression_producer)',
    ]
    for path in ['pcpath_producer', 'pcpath_producer ++ [PCFIELD 0]']:
        checks.append('~$magic_method_context_source(S[.CODE = [pcode[.EXPRESSIONS = $kwinvoke236_cut(pcode.EXPRESSIONS,' + path + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)')
    checks += [
        '$factory182_output(S.EVENTS) = $ptascii("' + prefix + '")',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'pcalltarget = METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT pcalltarget (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_producer) z_call)) :: ptask_dynamic_tail*',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_selected.OBJECTS = S.OBJECTS', '$target_instance(pcalltarget) = eps',
        '$target_receiver(S_selected,pcalltarget) = (n_selector)',
        '$target_lexical_class(S_selected,pcalltarget) = (pmethoddesc.OWNER)',
        '$target_called_class(S_selected,pcalltarget) = (porigin_allocated)',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_producer))',
        '$task_nodes(S_selected.TODO[0]) = [HOBJECT n_selector]',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_selector) = 1',
        'S_ready = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_ready.COMPLETION = BUDGET',
        'S_ready.TODO = (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_producer) z_call) :: ptask_dynamic_tail*',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_ready',
        '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_producer_found = $kwinvoke236_producer_seek(S_ready[.COMPLETION = NORMAL],2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
        'pcallcontext_producer.TARGET = pcalltarget', 'pcallcontext_producer.INSTANCE = eps',
        'pcallcontext_producer.RECEIVER = (n_selector)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)', 'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_selector]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_selector) = 1',
        '|S_producer.OBJECTS| = |S.OBJECTS|',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)', 'S_producer.STORE[n_saved] = DEFINED pvalue_request',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("REQUEST-OLD"))',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)', 'S_producer.STORE[n_late] = DEFINED (PINT 99)',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner)', 'S_producer.STORE[n_runner] = DEFINED PNULL',
        '$heap_count(HOBJECT n_caller,$frames_roots(S_producer.FRAMES)) = 1',
        '~$magic_method_context_source(S_producer,S_producer.CURRENT,porigin_producer,expression_producer)',
        '$magic_method_context_source(S_producer,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$call_current_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_send_found = $kwinvoke236_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'pvalue_sent = pvalue_request', 'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)',
        '~((HOBJECT n_selector) <- S_send.ALLOCATIONS)', '$heap_owners($heap_graph(S_send),HOBJECT n_selector) = 0',
        '|S_send.OBJECTS| = |S.OBJECTS|',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = ([PBOOL false,pvalue_request])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = eps',
        'S_after_found = $kwinvoke236_after_seek(S_send,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'), 'S_after.FRAMES = eps',
        '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_caller) = 0',
        '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)', 'S_after.STORE[n_kept] = DEFINED pvalue_request',
        '$string_carrier_valid(S_after,pvalue_request)',
        '$magic_method_context_source(S_after,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '~$magic_method_context_source(S_after,S_after.CURRENT,porigin_producer,expression_producer)',
        '$factory182_output(S_after.EVENTS) = ' + names.term(base64.b64decode(row['stdout_template_base64']).split(b'RETURN;', 1)[0]),
        '$heap_valid($heap_graph(S_after))',
    ]
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=list(ROWS))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or ROWS)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
