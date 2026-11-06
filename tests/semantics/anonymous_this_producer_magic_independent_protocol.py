#!/usr/bin/env python3
"""Caller-held This escapes through a real captured producer and argument table."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
CONVERT = ('S.TODO = (METHOD_CONVERT (METHOD_TARGET n_this porigin_method) porigin_capture z_capture) :: ptask_convert_tail* '
           '-- if S.CURRENT = (pcallcontext_caller) -- if pcallcontext_caller.RECEIVER = (n_this)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_outer_ready) z_outer) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, CONVERT)
for label, front in [('ready', READY), ('producer', PRODUCER), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$this216_' + label + '_')
PREFIX += r'''
dec $this216_outer_one(ptask) : pmagicmethodcall?
def $this216_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $this216_outer_one(ptask) = eps -- otherwise
dec $this216_outer(ptask*) : pmagicmethodcall?
def $this216_outer(eps) = eps
def $this216_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $this216_outer_one(ptask) = (pmagicmethodcall)
def $this216_outer(ptask :: ptask_tail*) = $this216_outer(ptask_tail*) -- if $this216_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CONVERT,
        '$this216_outer(ptask_convert_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_outer',
        'expression_capture = NExprMethodCall (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
        '$direct_this(BYTES text_this)', '|phpType7_real*| = 2',
        '$magic_method_firstclass_site(S,porigin_outer,expression_outer)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_init_capture)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopebase216")) = (porigin_lexical)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopechild216")) = (porigin_class)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopemid216")) = (porigin_declaring)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_lexical)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        r'porigin_lexical =/= porigin_declaring /\ porigin_declaring =/= porigin_class',
        '$magic_method_this_producer(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_declaring', 'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$magic_method_this_producer(S,eps,porigin_outer,expression_outer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.RECEIVER = eps]),porigin_outer,expression_outer) = eps',
        '$call_selected_valid(S,METHOD_TARGET n_this porigin_method,(porigin_capture))',
        '$method_capture_current(S,porigin_capture) = eps',
        'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_class eps]',
        'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_declaring', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = (n_this)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
        'S_ready_found = $this216_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)',
        'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $this216_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'pcallcontext_ready = pcallcontext_caller',
        'porigin_outer_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '$target_receiver(S_ready,CLOSURE_TARGET n_wrapper) = (n_this)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        'S_producer_found = $this216_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_this', 'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = (n_this)',
        'pcallcontext_producer.LEXICAL_CLASS = (porigin_declaring)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_this) = 3',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner_cell)',
        'S_producer.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$objectprops_at(S_producer.OBJECTPROPS,n_this) = (ppropertyslot_this*)',
        '$property_slot_at(ppropertyslot_this*,$ptascii("text")) = (ppropertyslot_text)',
        'ppropertyslot_text.STATE = PROP_VALUE (DIRECT pvalue_string)',
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;SHIFT;PRODUCER:PeerScopeMid216:PeerScopeChild216;")',
        'S_handler_found = $this216_handler_seek(S_producer,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall',
        'pvalue_items* = [POBJECT n_this,PBOOL false]', 'n_arguments = n_named',
        '~((HOBJECT n_wrapper) <- S_handler.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_handler),HOBJECT n_this) = 2',
        '$magic_method_context_values(S_handler,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this),KNOWN (PBOOL false)],eps) = ([POBJECT n_this,PBOOL false])',
        '$magic_method_context_values(S_handler,S_handler.CURRENT,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this),KNOWN (PBOOL false)],eps) = eps',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (POBJECT n_this)),ENTRY (KSTRING $ptascii("later")) (DIRECT (PBOOL false))]',
        'S_after_found = $this216_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 1',
        '$lookup(S_after.ENV,$ptascii("child")) = (n_child_cell)',
        'S_after.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_after.OBJECTPROPS,n_child) = (ppropertyslot_child*)',
        '$property_slot_at(ppropertyslot_child*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_after,HARRAY n_arguments) = [HOBJECT n_this]',
        '$magic_method_this_producer(S_after,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$string_carrier_valid(S_after,pvalue_string)',
        'S_done = $drive_steps(S_after,2048)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_this) <- S_done.ALLOCATIONS)', '~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '$magic_method_this_producer(S_done,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
