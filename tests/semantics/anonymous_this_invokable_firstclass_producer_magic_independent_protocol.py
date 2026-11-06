#!/usr/bin/env python3
"""An implicit This capture keeps its caller context and permits This to escape."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_invokable_firstclass_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_read_tail* '
        '-- if S.CURRENT = (pcallcontext_caller) -- if S.RESULT = KNOWN (POBJECT n_this) '
        '-- if pcallcontext_caller.RECEIVER = (n_this)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = (pcallcontext_result)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisifcc221_' + label + '_')
PREFIX += r'''
dec $thisifcc221_outer_one(ptask) : pmagicmethodcall?
def $thisifcc221_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $thisifcc221_outer_one(ptask) = eps -- otherwise
dec $thisifcc221_outer(ptask*) : pmagicmethodcall?
def $thisifcc221_outer(eps) = eps
def $thisifcc221_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisifcc221_outer_one(ptask) = (pmagicmethodcall)
def $thisifcc221_outer(ptask :: ptask_tail*) = $thisifcc221_outer(ptask_tail*) -- if $thisifcc221_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        'S_read.ORIGIN = (porigin_capture)', '$firstclass_task_valid(S_read,porigin_capture,z_init,z_capture)',
        '$thisifcc221_outer(ptask_read_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S_read.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall (NExprFuncCall (NExprVariable (BYTES text_this) metadata_this) (SEQUENCE phpType7_capture*) metadata_capture) (SEQUENCE phpType7_real*) metadata_outer',
        '$direct_this(BYTES text_this)', 'phpType7_capture* = [(NVariadicPlaceholder metadata_placeholder)]', '|phpType7_real*| = 2',
        '$magic_method_firstclass_site(S_read,porigin_outer,expression_outer)',
        '$dynamic_operand_valid(S_read,porigin_capture)',
        '~$dynamic_operand_valid(S_read[.RESULT = VARIABLE $ptascii("this") 1],porigin_capture)',
        '$magic_producer_cv_parts(S_read,porigin_outer,expression_outer) = eps',
        '$object_class_origin(S_read,n_this) = (porigin_class)',
        '$magic_method_this_invokable_producer(S_read,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_invokable_producer(S_read,eps,porigin_outer,expression_outer) = eps',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.OWNER =/= porigin_class',
        'pcallcontext_caller.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;")',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'pcalltarget = METHOD_TARGET n_this pfunction.ORIGIN',
        'S_selected.TODO = (METHOD_CONVERT pcalltarget porigin_capture z_capture) :: ptask_read_tail*',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_capture))',
        '$method_capture_current(S_selected,porigin_capture) = eps',
        'n_wrapper = |S_selected.OBJECTS|',
        'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S_read,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [METHODCLOSURE pfunction.ORIGIN porigin_capture porigin_class eps]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = (n_this)', '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
        'S_producer_found = $thisifcc221_producer_seek(S_wrapped[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_this', 'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = (n_this)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_this) = 3',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner_cell)',
        'S_producer.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_result_found = $thisifcc221_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_this', 'pmagicmethodcall_result = pmagicmethodcall', 'pcallcontext_result = pcallcontext_caller',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_this) = 2',
        '$magic_method_context_values(S_result,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_this)],eps) = ([PBOOL false,POBJECT n_this])',
        'S_handler_found = $thisifcc221_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,POBJECT n_this]', 'n_arguments = n_named',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_this))]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED (POBJECT n_this)',
        '$magic_method_context_values(S_handler,S_handler.CURRENT,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_this)],eps) = eps',
        'S_after_found = $thisifcc221_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        'S_after.STORE[n_kept_cell] = DEFINED (POBJECT n_this)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 1',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_this) <- S_done.ALLOCATIONS)',
        '$magic_method_this_invokable_producer(S_done,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
