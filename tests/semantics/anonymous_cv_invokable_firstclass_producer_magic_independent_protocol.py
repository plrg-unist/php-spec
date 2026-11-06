#!/usr/bin/env python3
"""An actual reference-CV capture mints one outer receipt before name retirement."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_invokable_firstclass_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_read_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("receiver")) z_cv -- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvifcc220_' + label + '_')
PREFIX += r'''
dec $cvifcc220_outer_one(ptask) : pmagicmethodcall?
def $cvifcc220_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cvifcc220_outer_one(ptask) = eps -- otherwise
dec $cvifcc220_outer(ptask*) : pmagicmethodcall?
def $cvifcc220_outer(eps) = eps
def $cvifcc220_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvifcc220_outer_one(ptask) = (pmagicmethodcall)
def $cvifcc220_outer(ptask :: ptask_tail*) = $cvifcc220_outer(ptask_tail*) -- if $cvifcc220_outer_one(ptask) = eps
dec $cvifcc220_bad_one(ptask) : ptask
def $cvifcc220_bad_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 eps
def $cvifcc220_bad_one(ptask) = ptask -- otherwise
dec $cvifcc220_bad(ptask*) : ptask*
def $cvifcc220_bad(eps) = eps
def $cvifcc220_bad(ptask :: ptask_tail*) = $cvifcc220_bad_one(ptask) :: $cvifcc220_bad(ptask_tail*)
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        'S_read.ORIGIN = (porigin_capture)', '$firstclass_task_valid(S_read,porigin_capture,z_init,z_capture)',
        '$cvifcc220_outer(ptask_read_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S_read.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall (NExprFuncCall (NExprVariable (BYTES text_cv) metadata_cv) (SEQUENCE phpType7_capture*) metadata_capture) (SEQUENCE phpType7_real*) metadata_outer',
        'phpType7_capture* = [(NVariadicPlaceholder metadata_placeholder)]', '|phpType7_real*| = 2',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)',
        '$magic_method_firstclass_site(S_read,porigin_outer,expression_outer)',
        '$magic_producer_cv_parts(S_read,porigin_outer,expression_outer) = ((porigin_capture,VARIABLE ($ptascii("receiver")) z_cv,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
        '$magic_producer_argument_site(S_read,porigin_capture) = (porigin_outer)',
        '$magic_producer_index(S_read,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,porigin_capture,0) = eps',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_outer) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
        '$lookup(S_read.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        '$lookup(S_read.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'n_receiver_cell <- S_read.REFCELLS', 'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S_read,$ptascii("receiver")) = (n_receiver)',
        '$object_class_origin(S_read,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_outer,porigin_class) = (pmethoddesc)',
        '$object_invoke_method(S_read,n_receiver) = (pmethoddesc)', 'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER =/= porigin_class',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;INSTALL;")',
        'S_bad = S_read[.TODO = $cvifcc220_bad(S_read.TODO)]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_outer)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_outer) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'pcalltarget = METHOD_TARGET n_receiver pfunction.ORIGIN',
        'S_selected.TODO = (METHOD_CONVERT pcalltarget porigin_capture z_capture) :: ptask_selected_tail*',
        '$cvifcc220_outer(ptask_selected_tail*) = (pmagicmethodcall_selected)',
        'pmagicproducerfact_selected = {SITE porigin_outer,CLASS porigin_class,METHOD pfunction.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_selected]]',
        '$magic_producer_fact_at(pmagicmethodcall_selected.PRODUCERS,porigin_capture) = eps',
        '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[{SITE porigin_capture,CLASS porigin_class,METHOD pfunction.ORIGIN}])',
        '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],1)',
        '$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],2)',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_capture))',
        '$target_nodes(pcalltarget) = [HOBJECT n_receiver]',
        'n_wrapper = |S_selected.OBJECTS|',
        'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S_read,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [METHODCLOSURE pfunction.ORIGIN porigin_capture porigin_class eps]',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        'S_producer_found = $cvifcc220_producer_seek(S_wrapped[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_receiver', 'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = (n_receiver)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("receiver")) = eps',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'S_producer.STORE[n_receiver_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_result_found = $cvifcc220_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_receiver', 'pmagicmethodcall_result = pmagicmethodcall_selected',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],[pmagicproducerfact_selected]) = ([PBOOL false,POBJECT n_receiver])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],eps) = eps',
        'S_handler_found = $cvifcc220_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall_selected',
        'pvalue_items* = [PBOOL false,POBJECT n_receiver]', 'n_arguments = n_named',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_receiver))]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED (POBJECT n_receiver)',
        'S_after_found = $cvifcc220_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_receiver) = 1',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_done,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
