#!/usr/bin/env python3
"""Allocated receiver scope, static selector release and saved caller authority."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_method_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = list(ROWS)
PREP = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_real* false b_base z_call) :: ptask_prep_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if S.CURRENT = (pcallcontext_caller) '
        '-- if $method_capture(S,b_base,z_call) = (S_capture,KNOWN (POBJECT n_selector))')
READY = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready) -- if $target_function(S,pcalltarget_ready) = (pfunction_ready) '
         '-- if $class_method_origin(S.CLASSES,pfunction_ready.ORIGIN) = (pmethoddesc_ready) '
         '-- if pmethoddesc_ready.NAME = $ptascii("capture")')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_send 1 ([KNOWN (PBOOL false)])) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN pvalue_sent -- if S.CURRENT = (pcallcontext_send)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
SHADOW = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_shadow_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_shadow)')
PREFIX = names.PREFIX.replace(names.FRONT, PREP)
for label, front in [('ready', READY), ('producer', PRODUCER), ('send', SEND), ('after', AFTER), ('shadow', SHADOW)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$kwmethod234_' + label + '_')
PREFIX += r'''
dec $kwmethod234_outer_one(ptask) : pmagicmethodcall?
def $kwmethod234_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $kwmethod234_outer_one(ptask) = eps -- otherwise
dec $kwmethod234_outer(ptask*) : pmagicmethodcall?
def $kwmethod234_outer(eps) = eps
def $kwmethod234_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $kwmethod234_outer_one(ptask) = (pmagicmethodcall)
def $kwmethod234_outer(ptask :: ptask_tail*) = $kwmethod234_outer(ptask_tail*) -- if $kwmethod234_outer_one(ptask) = eps
dec $kwmethod234_omit(pcodeexpr, pcpath, bool) : bool
def $kwmethod234_omit(CODECALL_INIT pcpath z, pcpath, true) = true
def $kwmethod234_omit(CODEEXPR pcpath z b_expr, pcpath, false) = true
def $kwmethod234_omit(pcodeexpr, pcpath, b) = false -- otherwise
dec $kwmethod234_cut(pcodeexpr*, pcpath, bool) : pcodeexpr*
def $kwmethod234_cut(eps, pcpath, b) = eps
def $kwmethod234_cut(pcodeexpr :: pcodeexpr_tail*, pcpath, b) = $kwmethod234_cut(pcodeexpr_tail*, pcpath, b)
  -- if $kwmethod234_omit(pcodeexpr, pcpath, b)
def $kwmethod234_cut(pcodeexpr :: pcodeexpr_tail*, pcpath, b) = pcodeexpr :: $kwmethod234_cut(pcodeexpr_tail*, pcpath, b)
  -- if ~$kwmethod234_omit(pcodeexpr, pcpath, b)
'''


def at(front, state):
    return front.replace('S.', state + '.').replace('(S,', '(' + state + ',')


def shadow(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $kwmethod234_shadow_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHADOW,
        'S.ORIGIN = (porigin_outer)',
        '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprMethodCall expression_new (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_real*) metadata_producer',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope234")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild234")) = (porigin_called)',
        'pcallcontext_shadow.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_shadow.CALLED_CLASS = (porigin_called)',
        '$magic_method_keyword_new_class(S,S.CURRENT,porigin_new,expression_new) = (porigin_called)',
        '$magic_method_keyword_new_source(S,S.CURRENT,porigin_new,expression_new)',
        '$method_class_selected(S,porigin_called,$ptascii("capture"),(porigin_scope)) = (pmethoddesc_private)',
        'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
        '$effective_method(S,porigin_called,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_public)',
        'pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_private.FUNCTION.ORIGIN =/= pmethoddesc_public.FUNCTION.ORIGIN',
        '$magic_method_plain_instance_source(S,pmethoddesc_public,phpType7_real*)',
        '~$magic_method_plain_instance_source(S,pmethoddesc_private,phpType7_real*)',
        '$magic_method_context_call(expression_producer)',
        '~$magic_method_context_source(S,S.CURRENT,porigin_producer,expression_producer)',
        '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        'S_done = $drive_steps(S,128)',
        'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    row = ROWS[case['id']]
    if row.get('model_status') == 'unsupported':
        checks = shadow(fixture, filename)
        return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))
    static = case['id'].endswith('parent-static')
    allocated = 'peerbase234' if static else 'peerscope234'
    expected = 'REQUEST-SELECTED' if static else 'REQUEST-OLD'
    prefix = ('CTOR:PeerBase234:PeerChild234:8;CTOR:PeerBase234:' +
              ('PeerBase234' if static else 'PeerScope234') + ':3;')
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PREP,
        '$kwmethod234_outer(ptask_prep_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
        'S.ORIGIN = (porigin_producer)', 'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprMethodCall expression_new (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_real*) metadata_producer',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_instance_producer(S,porigin_producer,expression_producer) = eps',
        '$magic_method_fresh_receiver(S,porigin_new,expression_new) = eps',
        '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$magic_method_argument_source(S,porigin_producer,1,expression_producer)',
        '$class_named(S.CLASSNAMES,$ptascii("' + allocated + '")) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope234")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild234")) = (porigin_called)',
        'porigin_allocated =/= porigin_called',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        'pcallcontext_caller.RECEIVER = (n_caller)', 'n_caller =/= n_selector',
        '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
        '$object_class_origin(S,n_selector) = (porigin_allocated)',
        '$closure_source_class(S,porigin_producer) = (porigin_scope)',
        '$method_class_selected(S,porigin_allocated,$ptascii("capture"),(porigin_scope)) = (pmethoddesc)',
        '$method_class_selected(S,porigin_called,$ptascii("capture"),(porigin_scope)) = (pmethoddesc_wrong)',
        'pmethoddesc_wrong.FUNCTION.ORIGIN =/= pmethoddesc.FUNCTION.ORIGIN',
        'S.CODE = [pcode]', '$code_expression(pcode.EXPRESSIONS,pcpath_producer) = ((z_call,false))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = eps',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_new)',
        '~$magic_method_context_source(S,eps,porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.LEXICAL_CLASS = eps]),porigin_producer,expression_producer)',
        '~$magic_method_context_source(S,(pcallcontext_caller[.CALLED_CLASS = eps]),porigin_producer,expression_producer)',
        '~$magic_method_context_source(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        'pcode_no_method = pcode[.EXPRESSIONS = $kwmethod234_cut(pcode.EXPRESSIONS,pcpath_producer,false)]',
        '~$magic_method_context_source(S[.CODE = [pcode_no_method]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        'pcode_no_new = pcode[.EXPRESSIONS = $kwmethod234_cut(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0],true)]',
        '~$magic_method_context_source(S[.CODE = [pcode_no_new]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$factory182_output(S.EVENTS) = $ptascii("' + prefix + '")',
        '(HOBJECT n_selector) <- S.ALLOCATIONS',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_ready_found = $kwmethod234_ready_seek(S_one[.COMPLETION = NORMAL],2047)',
        'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $kwmethod234_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(READY, 'S_ready'),
        'pcallcontext_ready = pcallcontext_caller', 'porigin_ready = porigin_producer',
        'phpType7_ready* = phpType7_real*', 'pfunction_ready = pmethoddesc.FUNCTION',
        '$target_called_class(S_ready,pcalltarget_ready) = (porigin_allocated)',
        '$target_lexical_class(S_ready,pcalltarget_ready) = (pmethoddesc.OWNER)',
        '$target_instance(pcalltarget_ready) = eps',
    ]
    checks += ([
        'pcalltarget_ready = STATIC_METHOD_TARGET porigin_allocated pmethoddesc.FUNCTION.ORIGIN',
        '$target_nodes(pcalltarget_ready) = eps', '$target_receiver(S_ready,pcalltarget_ready) = eps',
        '~((HOBJECT n_selector) <- S_ready.ALLOCATIONS)',
        '$factory182_output(S_ready.EVENTS) = $ptascii("' + prefix + 'END:3;")',
    ] if static else [
        'pcalltarget_ready = METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN',
        '$target_nodes(pcalltarget_ready) = [HOBJECT n_selector]',
        '$target_receiver(S_ready,pcalltarget_ready) = (n_selector)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 1',
        '$factory182_output(S_ready.EVENTS) = $ptascii("' + prefix + '")',
    ])
    checks += [
        '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_producer_found = $kwmethod234_producer_seek(S_ready,2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
        'pcallcontext_producer.TARGET = pcalltarget_ready',
        'pcallcontext_producer.INSTANCE = eps',
        'pcallcontext_producer.RECEIVER = ' + ('eps' if static else '(n_selector)'),
        '$call_context_roots(S_producer.CURRENT) = ' + ('eps' if static else '[HOBJECT n_selector]'),
        'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
        'S_producer.STORE[n_saved] = DEFINED pvalue_request',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("' + expected + '"))',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)',
        'S_producer.STORE[n_late] = DEFINED (PINT 99)',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner)',
        'S_producer.STORE[n_runner] = DEFINED PNULL',
        '$heap_count(HOBJECT n_caller,$frames_roots(S_producer.FRAMES)) = 1',
        '~$magic_method_context_source(S_producer,S_producer.CURRENT,porigin_producer,expression_producer)',
        '$magic_method_context_source(S_producer,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$call_current_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_send_found = $kwmethod234_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'pvalue_sent = pvalue_request', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller',
        '~((HOBJECT n_selector) <- S_send.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_selector) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = ([PBOOL false,pvalue_request])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_request],eps) = eps',
        'S_after_found = $kwmethod234_after_seek(S_send,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
        'S_after.FRAMES = eps', '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_caller) = 0',
        '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)', 'S_after.STORE[n_kept] = DEFINED pvalue_request',
        '$magic_method_context_source(S_after,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '~$magic_method_context_source(S_after,S_after.CURRENT,porigin_producer,expression_producer)',
        'S_done = $drive_steps(S_after,512)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or CASES)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
