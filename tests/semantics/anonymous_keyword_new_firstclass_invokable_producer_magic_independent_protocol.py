#!/usr/bin/env python3
"""Implicit keyword FCC allocation and owning wrappers preserve an old request."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_firstclass_invokable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CAPTURE = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_capture_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_selector) -- if S.CURRENT = (pcallcontext_caller)')
CONVERT = ('S.TODO = (METHOD_CONVERT pcalltarget_capture porigin_capture z_capture) :: ptask_convert_tail* '
           '-- if S.CURRENT = (pcallcontext_convert)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_send 1 ([KNOWN (PBOOL false)])) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN pvalue_sent -- if S.CURRENT = (pcallcontext_send)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUND = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_bound_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_bound)')
PREFIX = names.PREFIX.replace(names.FRONT, CAPTURE)
for label, front in [('convert', CONVERT), ('ready', READY), ('producer', PRODUCER), ('send', SEND), ('after', AFTER), ('bound', BOUND)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$kwfcc237_' + label + '_')
PREFIX += r'''
dec $kwfcc237_outer_one(ptask) : pmagicmethodcall?
def $kwfcc237_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $kwfcc237_outer_one(ptask) = eps -- otherwise
dec $kwfcc237_outer(ptask*) : pmagicmethodcall?
def $kwfcc237_outer(eps) = eps
def $kwfcc237_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $kwfcc237_outer_one(ptask) = (pmagicmethodcall)
def $kwfcc237_outer(ptask :: ptask_tail*) = $kwfcc237_outer(ptask_tail*) -- if $kwfcc237_outer_one(ptask) = eps
dec $kwfcc237_init_at(pcodeexpr, pcpath) : bool
def $kwfcc237_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $kwfcc237_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $kwfcc237_cut(pcodeexpr*, pcpath) : pcodeexpr*
def $kwfcc237_cut(eps, pcpath) = eps
def $kwfcc237_cut(pcodeexpr :: pcodeexpr_tail*, pcpath) = $kwfcc237_cut(pcodeexpr_tail*, pcpath) -- if $kwfcc237_init_at(pcodeexpr, pcpath)
def $kwfcc237_cut(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $kwfcc237_cut(pcodeexpr_tail*, pcpath) -- if ~$kwfcc237_init_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.').replace('(S,', '(' + state + ',')


def bound(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $kwfcc237_bound_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUND, 'S.ORIGIN = (porigin_outer)',
        '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall (NExprFuncCall expression_new (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_capture) (SEQUENCE phpType7_real*) metadata_producer',
        '|phpType7_real*| = 1',
        'phpType7_real*[0] = NArg (NIdentifier (BYTES text_saved) metadata_saved) expression_saved (BOOLEAN false) (BOOLEAN false) metadata_arg',
        '$base64(text_saved) = $ptascii("saved")',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0])',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope237")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild237")) = (porigin_called)',
        'pcallcontext_bound.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_bound.CALLED_CLASS = (porigin_called)',
        '$magic_method_keyword_new_class(S,S.CURRENT,porigin_new,expression_new) = (porigin_called)',
        '$magic_method_keyword_new_source(S,S.CURRENT,porigin_new,expression_new)',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$effective_method(S,porigin_called,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc)',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_init)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0,PCFIELD 0]) = (z_new)',
        '$ppbuiltin_arguments(phpType7_real*) = eps',
        '~$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_invokable_call(expression_producer)', '$magic_method_context_call(expression_producer)',
        '~$magic_method_context_source(S,S.CURRENT,porigin_producer,expression_producer)',
        '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        'S_done = $drive_steps(S,128)',
        'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"', '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    row = ROWS[case['id']]
    if row.get('model_status') == 'unsupported':
        checks = bound(fixture, filename)
    else:
        parent = case['id'].endswith('parent-instance')
        allocated = 'peerbase237' if parent else 'peerscope237'
        expected = 'REQUEST-OLD'
        prefix = 'CTOR:PeerBase237:PeerChild237:8;CTOR:PeerBase237:' + ('PeerBase237' if parent else 'PeerScope237') + ':3;'
        checks = [
            'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
            r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
            'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
            'S = S_found[.COMPLETION = NORMAL]', CAPTURE,
            '$kwfcc237_outer(ptask_capture_tail*) = (pmagicmethodcall)',
            'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
            '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
            'porigin_producer = PORIGIN n_unit pcpath_producer',
            'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
            'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0])', 'S.ORIGIN = (porigin_capture)',
            '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
            'expression_producer = NExprFuncCall (NExprFuncCall expression_new (SEQUENCE phpType7_capture*) metadata_capture) (SEQUENCE phpType7_real*) metadata_producer',
            'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
            '|phpType7_ctor*| = 1', '|phpType7_real*| = 2', '|phpType7_capture*| = 1', '$ppfirstclass(phpType7_capture*)',
            '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
            '$ordinary_keyword_new_site(S,porigin_new)', '$magic_method_context_call(expression_producer)',
            '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = eps',
            '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            '$class_named(S.CLASSNAMES,$ptascii("' + allocated + '")) = (porigin_allocated)',
            '$class_named(S.CLASSNAMES,$ptascii("peerscope237")) = (porigin_scope)',
            '$class_named(S.CLASSNAMES,$ptascii("peerchild237")) = (porigin_called)', 'porigin_allocated =/= porigin_called',
            'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
            'pcallcontext_caller.RECEIVER = (n_caller)', 'n_caller =/= n_selector',
            '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
            '$object_class_origin(S,n_selector) = (porigin_allocated)',
            '$effective_method(S,porigin_allocated,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc)',
            '$effective_method(S,porigin_called,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc_wrong)',
            'pmethoddesc_wrong.FUNCTION.ORIGIN =/= pmethoddesc.FUNCTION.ORIGIN',
            'S.CODE = [pcode]',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_init)',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0,PCFIELD 0]) = (z_new)',
            '~$magic_method_context_source(S,eps,porigin_producer,expression_producer)',
            '~$magic_method_context_source(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer)',
            '~$magic_method_context_source(S,(pcallcontext_caller[.LEXICAL_CLASS = eps]),porigin_producer,expression_producer)',
            '~$magic_method_context_source(S,(pcallcontext_caller[.CALLED_CLASS = eps]),porigin_producer,expression_producer)',
        ]
        for suffix in ['', ',PCFIELD 0', ',PCFIELD 0,PCFIELD 0']:
            path = 'pcpath_producer' if not suffix else 'pcpath_producer ++ [' + suffix[1:] + ']'
            checks.append('~$magic_method_context_source(S[.CODE = [pcode[.EXPRESSIONS = $kwfcc237_cut(pcode.EXPRESSIONS,' + path + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)')
        checks += [
            '$firstclass_task_valid(S,porigin_capture,z_init,z_capture)',
            '~$firstclass_task_valid(S,porigin_capture,$(z_init + 1),z_capture)',
            '$factory182_output(S.EVENTS) = $ptascii("' + prefix + '")',
            'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
            'S_one.TODO = (METHOD_CONVERT (METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN) porigin_capture z_capture) :: ptask_capture_tail*',
            'S_convert_found = $kwfcc237_convert_seek(S_one,2047)', 'S_convert_found.COMPLETION = BUDGET',
            'S_convert_direct = $kwfcc237_convert_seek(S,2048)', 'S_convert_direct = S_convert_found',
            'S_convert = S_convert_found[.COMPLETION = NORMAL]', at(CONVERT, 'S_convert'),
            'pcallcontext_convert = pcallcontext_caller',
            '$target_called_class(S_convert,pcalltarget_capture) = (porigin_allocated)',
            '$target_lexical_class(S_convert,pcalltarget_capture) = (pmethoddesc.OWNER)',
            'pcalltarget_capture = METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN',
            '$heap_owners($heap_graph(S_convert),HOBJECT n_selector) = 1',
            '$factory182_output(S_convert.EVENTS) = $ptascii("' + prefix + '")',
            'S_zero = $drive_steps(S_convert,0)', 'S_zero = S_convert[.COMPLETION = BUDGET]',
            'n_wrapper = |S_convert.OBJECTS|', 'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)', 'S_wrapped.BASE = BASE_VALUE (KNOWN PNULL)',
            '$object_body(S_wrapped.OBJECTS[n_wrapper]) = METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_capture porigin_allocated pmethodcapture?',
            'S_wrapped_direct = $drive_steps(S,2)', 'S_wrapped_direct = S_wrapped',
            '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
            'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_allocated', 'pclosurescope.CREATION = eps',
            'pclosurescope.RECEIVER = (n_selector)',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_selector]',
            '$heap_owners($heap_graph(S_wrapped),HOBJECT n_wrapper) = 1',
            'S_ready_found = $kwfcc237_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
            'S_ready_direct = $kwfcc237_ready_seek(S_convert,2048)', 'S_ready_direct = S_ready_found',
            'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(READY, 'S_ready'),
            'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
            'pcallcontext_ready = pcallcontext_caller', '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
            '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 1',
            'S_producer_found = $kwfcc237_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
            'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
            'pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)',
            'pcallcontext_producer.RECEIVER = (n_selector)',
            'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)', 'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
            '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
            '$heap_owners($heap_graph(S_producer),HOBJECT n_selector) = 1',
            '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)', 'S_producer.STORE[n_saved] = DEFINED pvalue_request',
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("' + expected + '"))',
            '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)', 'S_producer.STORE[n_late] = DEFINED (PINT 99)',
            '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner)', 'S_producer.STORE[n_runner] = DEFINED PNULL',
            '$heap_count(HOBJECT n_caller,$frames_roots(S_producer.FRAMES)) = 1',
            '~$magic_method_context_source(S_producer,S_producer.CURRENT,porigin_producer,expression_producer)',
            '$magic_method_context_source(S_producer,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            '$call_current_valid(S_producer)', '$closure_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
            'S_send_found = $kwfcc237_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
            'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
            'pvalue_sent = pvalue_request', 'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
            'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)',
            '~((HOBJECT n_selector) <- S_send.ALLOCATIONS)', '$heap_owners($heap_graph(S_send),HOBJECT n_selector) = 0',
            '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = ([PBOOL false,pvalue_request])',
            '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = eps',
            'S_after_found = $kwfcc237_after_seek(S_send,2048)', 'S_after_found.COMPLETION = BUDGET',
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
