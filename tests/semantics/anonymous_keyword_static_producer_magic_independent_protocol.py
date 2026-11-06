#!/usr/bin/env python3
"""Saved caller scope selects static:: and survives a mixed CV producer's death."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_static_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
SELECT = ('S.TODO = (CALL_ARGS (SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) '
          'phpType7_inner* 0 eps (porigin_producer) z_call) :: ptask_select_tail* '
          '-- if |phpType7_inner*| = 2 -- if S.CURRENT = (pcallcontext_caller) '
          '-- if pcallcontext_caller.RECEIVER = (n_caller)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = SCOPED_TARGET porigin_requested_producer porigin_method_producer porigin_called_producer eps poperand_selector_producer')
HANDLER = ('S.TODO = (RETURN_VALUE z_handler_return) :: ptask_handler_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_closure) -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_string_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SELECT)
for label, front in [('producer', PRODUCER), ('handler', HANDLER), ('after', AFTER), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$keyword214_' + label + '_')
PREFIX += r'''
dec $keyword214_outer_one(ptask) : pmagicmethodcall?
def $keyword214_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $keyword214_outer_one(ptask) = eps -- otherwise
dec $keyword214_outer(ptask*) : pmagicmethodcall?
def $keyword214_outer(eps) = eps
def $keyword214_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $keyword214_outer_one(ptask) = (pmagicmethodcall)
def $keyword214_outer(ptask :: ptask_tail*) = $keyword214_outer(ptask_tail*) -- if $keyword214_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SELECT,
        '$keyword214_outer(ptask_select_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprStaticCall (NName (BYTES text_keyword) metadata_keyword) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_inner*) metadata_call',
        '$ptlc($base64(text_keyword)) = $ptascii("static")',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_producer) = (($source_line(metadata_call),false))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = eps',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_lexical)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopebase214")) = (porigin_lexical)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopechild214")) = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopemid214")) = (porigin_declaring)',
        'porigin_requested = porigin_called',
        r'porigin_lexical =/= porigin_declaring /\ porigin_declaring =/= porigin_requested',
        '$magic_method_keyword_static_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_declaring', 'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        'pcalltarget = SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector',
        '$call_selected_valid(S,pcalltarget,(porigin_producer))',
        '$target_nodes(pcalltarget) = eps', '$target_receiver(S,pcalltarget) = eps',
        '$target_lexical_class(S,pcalltarget) = (porigin_declaring)',
        '$target_called_class(S,pcalltarget) = (porigin_called)',
        '$lookup(S.ENV,$ptascii("late")) = (n_late_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S.STORE[n_late_cell] = DEFINED pvalue_string',
        '$lookup(S.ENV,$ptascii("probe")) = (n_probe_cell)',
        'S.STORE[n_probe_cell] = DEFINED (POBJECT n_probe)',
        '$object_class_origin(S,n_probe) = (porigin_probe_class)',
        '$magic_method_keyword_static_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_static_producer(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_ready = $drive_steps(S_pause[.COMPLETION = NORMAL],1)', 'S_ready.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_ready',
        'S_producer_found = $keyword214_producer_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = pcalltarget',
        'pcallcontext_producer.INSTANCE = eps', 'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (porigin_declaring)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_called)',
        '$call_context_roots(S_producer.CURRENT) = eps',
        'pvalue_returned = pvalue_string',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_producer.FRAMES = pframe_caller :: pframe_tail*',
        'S_caller = $constant_frame_scope(S_producer,pframe_caller,pframe_tail*)',
        'S_caller.CURRENT = pmagicmethodcall.CALLER',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_caller) = 1',
        '$factory182_output(S_producer.EVENTS) = $ptascii("SHIFT;PRODUCER:PeerScopeMid214:PeerScopeChild214;")',
        'S_handler_found = $keyword214_handler_seek(S_producer,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler.SITE = pmagicmethodcall.SITE',
        'pmagicmethodcall_handler.CALLER = pmagicmethodcall.CALLER',
        'pcallcontext_handler.LEXICAL_CLASS =/= pcallcontext_caller.LEXICAL_CLASS',
        '$call_argument_origin(S_handler,(pmagicmethodcall.SITE),1) = (porigin_probe)',
        '$magic_producer_selected_source(S_handler,porigin_probe,porigin_probe_class) = (pmethoddesc_probe)',
        'pmagicproducerfact_probe = {SITE porigin_probe,CLASS porigin_probe_class,METHOD pmethoddesc_probe.FUNCTION.ORIGIN}',
        'pmagicmethodcall_handler = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_probe]]',
        '~((HOBJECT n_probe) <- S_handler.ALLOCATIONS)',
        'pvalue_items* = [pvalue_string,PBOOL true]', 'n_arguments = n_named',
        '$magic_method_keyword_static_producer(S_handler,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_keyword_static_producer(S_handler,S_handler.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_context_values(S_handler,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PBOOL true)],[pmagicproducerfact_probe]) = ([pvalue_string,PBOOL true])',
        '$magic_method_context_values(S_handler,S_handler.CURRENT,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PBOOL true)],[pmagicproducerfact_probe]) = eps',
        '$magic_method_context_values(S_handler,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PBOOL true)],eps) = eps',
        '$magic_method_fact_values(S_handler,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PBOOL true)],[pmagicproducerfact_probe]) = eps',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT pvalue_string),ENTRY (KSTRING $ptascii("later")) (DIRECT (PBOOL true))]',
        '$node_children(S_handler,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$string_carrier_valid(S_handler,pvalue_string)',
        '$call_descriptors_valid(S_handler)', '$gc_state_valid(S_handler)', '$heap_valid($heap_graph(S_handler))',
        'S_after_found = $keyword214_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
        '$magic_method_keyword_static_producer(S_after,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_keyword_static_producer(S_after,S_after.CURRENT,porigin_producer,expression_producer) = eps',
        '$factory182_output(S_after.EVENTS) = $ptascii("SHIFT;PRODUCER:PeerScopeMid214:PeerScopeChild214;PROBE;PROBE-END;MAGIC;OWNER;SCOPE-END;")',
        'S_child_found = $keyword214_child_seek(S_after,2048)', 'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot_child_items*)',
        '$property_slot_at(ppropertyslot_child_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        'S_child.ARRAYS[n_arguments] = S_handler.ARRAYS[n_arguments]',
        'S_done = $drive_steps(S_child,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
