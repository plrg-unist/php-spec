#!/usr/bin/env python3
"""Implicit This call selects an ordinary inherited invoke target before args."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_invokable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (CALL_DYNAMIC porigin_producer z_init z_call) :: ptask_read_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_this) -- if S.CURRENT = (pcallcontext_caller) '
        '-- if $dynamic_this_site(S,porigin_producer)')
READY = ('S.TODO = (CALL_ARGS (METHOD_TARGET n_this_ready porigin_method_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = METHOD_TARGET n_this_producer porigin_method_producer')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_magic) metadata_magic) :: expression_echo_tail*)) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC:") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('ready', READY), ('producer', PRODUCER), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisinvoke218_' + label + '_')
PREFIX += r'''
dec $thisinvoke218_outer_one(ptask) : pmagicmethodcall?
def $thisinvoke218_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $thisinvoke218_outer_one(ptask) = eps -- otherwise
dec $thisinvoke218_outer(ptask*) : pmagicmethodcall?
def $thisinvoke218_outer(eps) = eps
def $thisinvoke218_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisinvoke218_outer_one(ptask) = (pmagicmethodcall)
def $thisinvoke218_outer(ptask :: ptask_tail*) = $thisinvoke218_outer(ptask_tail*) -- if $thisinvoke218_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$thisinvoke218_outer(ptask_read_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        'pcallcontext_caller.RECEIVER = (n_this)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall (NExprVariable (BYTES text_this) metadata_this) (SEQUENCE phpType7_real*) metadata_producer',
        '$direct_this(BYTES text_this)', '|phpType7_real*| = 2',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init)',
        '$dynamic_fixed_name(S,porigin_producer) = eps',
        '$dynamic_operand_valid(S,porigin_producer)',
        '~$dynamic_operand_valid(S[.RESULT = VARIABLE ($ptascii("this")) $variable_line(BYTES text_this,metadata_this)],porigin_producer)',
        '$magic_producer_cv_parts(S,porigin_producer,expression_producer) = eps',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopebase218")) = (porigin_lexical)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopechild218")) = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscopemid218")) = (porigin_declaring)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_lexical)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        '$magic_method_this_invokable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((n_this,porigin_called,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_declaring', 'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$object_invoke_method(S,n_this) = (pmethoddesc)',
        '$magic_method_this_invokable_producer(S,(pcallcontext_caller[.RECEIVER = eps]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_invokable_producer(S,(pcallcontext_caller[.CALLED_CLASS = (porigin_lexical)]),porigin_producer,expression_producer) = eps',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_ready_found = $thisinvoke218_ready_seek(S_one[.COMPLETION = NORMAL],2047)',
        'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $thisinvoke218_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_this_ready = n_this', 'porigin_method_ready = porigin_method',
        'pcallcontext_ready = pcallcontext_caller', 'porigin_ready = porigin_producer',
        'phpType7_ready* = phpType7_real*',
        '$call_selected_valid(S_ready,METHOD_TARGET n_this porigin_method,(porigin_producer))',
        '$target_nodes(METHOD_TARGET n_this porigin_method) = [HOBJECT n_this]',
        '$target_instance(METHOD_TARGET n_this porigin_method) = eps',
        'S_producer_found = $thisinvoke218_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_this', 'n_this_producer = n_this', 'porigin_method_producer = porigin_method',
        'pcallcontext_producer.INSTANCE = eps', 'pcallcontext_producer.RECEIVER = (n_this)',
        'pcallcontext_producer.LEXICAL_CLASS = (porigin_declaring)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_called)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_this]',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner_cell)',
        'S_producer.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;SHIFT;INVOKE:PeerScopeMid218:PeerScopeChild218;")',
        'S_handler_found = $thisinvoke218_handler_seek(S_producer,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall',
        'pvalue_items* = [POBJECT n_this,PBOOL false]', 'n_arguments = n_named',
        '$magic_method_context_values(S_handler,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this),KNOWN (PBOOL false)],eps) = ([POBJECT n_this,PBOOL false])',
        '$magic_method_fact_values(S_handler,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this),KNOWN (PBOOL false)],eps) = eps',
        '$magic_method_this_invokable_producer(S_handler,S_handler.CURRENT,porigin_producer,expression_producer) = eps',
        'S_after_found = $thisinvoke218_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HOBJECT n_this) <- S_after.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        '$magic_method_this_invokable_producer(S_after,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((n_this,porigin_called,pmethoddesc))',
        'S_done = $drive_steps(S_after,128)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        'S_done.NATIVEEXCESS = eps',
        '$call_descriptors_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
