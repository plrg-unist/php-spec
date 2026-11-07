#!/usr/bin/env python3
"""Keyword NEW returns its allocation while an independent caller can retire."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
START = ('S.TODO = (EVAL (NExprNew (NName (BYTES text_keyword) metadata_name) (SEQUENCE phpType7_ctor*) metadata_new)) :: ptask_start_tail* '
         '-- if $base64(text_keyword) = $ptascii("static") -- if S.ORIGIN = (porigin_new) '
         '-- if S.CURRENT = (pcallcontext_caller)')
CTOR = ('S.TODO = (RETURN_VALUE z_ctor_return) :: ptask_ctor_tail* '
        '-- if S.RESULT = KNOWN (PINT 9) -- if S.CURRENT = (pcallcontext_ctor) '
        '-- if pcallcontext_ctor.TARGET = METHOD_TARGET n_new porigin_ctor')
RESULT = ('S.TODO = (CTOR_RESULT n_result) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (PINT 9) -- if S.CURRENT = (pcallcontext_result)')
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_send 1 ([KNOWN (PBOOL false)])) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_send)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, START)
for label, front in [('ctor', CTOR), ('result', RESULT), ('send', SEND), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$kwnew233_' + label + '_')
PREFIX += r'''
dec $kwnew233_outer_one(ptask) : pmagicmethodcall?
def $kwnew233_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $kwnew233_outer_one(ptask) = eps -- otherwise
dec $kwnew233_outer(ptask*) : pmagicmethodcall?
def $kwnew233_outer(eps) = eps
def $kwnew233_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $kwnew233_outer_one(ptask) = (pmagicmethodcall)
def $kwnew233_outer(ptask :: ptask_tail*) = $kwnew233_outer(ptask_tail*) -- if $kwnew233_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', START,
        '$kwnew233_outer(ptask_start_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_new)',
        'expression_new = NExprNew (NName (BYTES text_keyword) metadata_name) (SEQUENCE phpType7_ctor*) metadata_new',
        '$origin_node(S.SOURCES,porigin_new) = (expression_new)', '|phpType7_ctor*| = 2',
        'porigin_new = PORIGIN n_unit pcpath_new', '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_name(pcode.NAMES,pcpath_new) = (($ptascii("static"),eps))',
        '$code_expression(pcode.EXPRESSIONS,pcpath_new) = ((z_name,false))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = (z_name)', 'z_name = $source_line(metadata_name)',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
        '$magic_method_keyword_new_source(S,pmagicmethodcall.CALLER,porigin_new,expression_new)',
        '$magic_method_constructor_producer(S,porigin_new,expression_new) = eps',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild233")) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("peerbase233")) = (porigin_base)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_base)', 'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)',
        'pcallcontext_caller.RECEIVER = (n_caller)', '$object_class_origin(S,n_caller) = (porigin_allocated)',
        '$magic_method_constructor_source(S,porigin_allocated,phpType7_ctor*) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_base', 'porigin_ctor = pmethoddesc.FUNCTION.ORIGIN',
        'S_ctor_found = $kwnew233_ctor_seek(S,2048)', 'S_ctor_found.COMPLETION = BUDGET',
        'S_ctor = S_ctor_found[.COMPLETION = NORMAL]', CTOR.replace('S.', 'S_ctor.'),
        'n_new =/= n_caller', 'pcallcontext_ctor.RECEIVER = (n_new)', 'pcallcontext_ctor.INSTANCE = eps',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_base)', 'pcallcontext_ctor.CALLED_CLASS = (porigin_allocated)',
        '$object_class_origin(S_ctor,n_new) = (porigin_allocated)',
        '$call_context_roots(S_ctor.CURRENT) = [HOBJECT n_new]',
        '$heap_count(HOBJECT n_caller,$frames_roots(S_ctor.FRAMES)) = 1',
        '$lookup($global_table_view(S_ctor).ENV,$ptascii("runner")) = (n_runner_cell)', 'S_ctor.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S_ctor).ENV,$ptascii("late")) = (n_late_cell)', 'S_ctor.STORE[n_late_cell] = DEFINED (PINT 99)',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        '$lookup(S_ctor.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_ctor.STORE[n_saved_cell] = DEFINED pvalue_request',
        '$objectprops_at(S_ctor.OBJECTPROPS,n_new) = (ppropertyslot_new*)',
        '$property_slot_at(ppropertyslot_new*,$ptascii("text")) = (ppropertyslot_text)',
        'ppropertyslot_text.STATE = PROP_VALUE (DIRECT pvalue_request)',
        '~$magic_method_keyword_new_source(S_ctor,S_ctor.CURRENT,porigin_new,expression_new)',
        '$magic_method_keyword_new_source(S_ctor,pmagicmethodcall.CALLER,porigin_new,expression_new)',
        'S_result_found = $kwnew233_result_seek(S_ctor,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_new', 'pcallcontext_result = pcallcontext_caller', '$ctor_result_valid(S_result,n_new)',
        'S_instance = $drive_steps(S_result,1)', 'S_instance.COMPLETION = BUDGET',
        'S_instance.RESULT = KNOWN (POBJECT n_new)', 'S_instance.TODO = ptask_result_tail*',
        'S_send_found = $kwnew233_send_seek(S_instance[.COMPLETION = NORMAL],2047)', 'S_send_found.COMPLETION = BUDGET',
        'S_direct = $kwnew233_send_seek(S_result,2048)', 'S_direct = S_send_found',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'n_send = n_new', 'pcallcontext_send = pcallcontext_caller', 'pmagicmethodcall_send = pmagicmethodcall',
        '$object_class_origin(S_send,n_new) = (porigin_allocated)', '$magic_method_value(S_send,POBJECT n_new)',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_new)],eps) = ([PBOOL false,POBJECT n_new])',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (PINT 9)],eps) = eps',
        '$magic_method_value(S_send,POBJECT pmagicmethodcall.OBJECT)',
        '$object_class_origin(S_send,pmagicmethodcall.OBJECT) = (porigin_wrong)', 'porigin_wrong =/= porigin_allocated',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT pmagicmethodcall.OBJECT)],eps) = eps',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_new)],eps) = eps',
        'S_handler_found = $kwnew233_handler_seek(S_send,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,POBJECT n_new]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)', 'S_handler.STORE[n_kept_cell] = DEFINED (POBJECT n_new)',
        'S_after_found = $kwnew233_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_new) = 1',
        '$magic_method_keyword_new_class(S_after,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
        '$magic_method_keyword_new_class(S_after,S_after.CURRENT,porigin_new,expression_new) = eps',
        'S_done = $drive_steps(S_after,512)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        '$magic_method_keyword_new_class(S_done,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
        '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
