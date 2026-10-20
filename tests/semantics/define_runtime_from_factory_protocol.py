#!/usr/bin/env python3
"""Reached factory publication separates creation from invocation USER scope."""
import argparse
from pathlib import Path
import sys

import define_runtime_closure_protocol as runtime
import define_scoped_runtime_closure_protocol as scoped
import define_stdclass_array_duplicate_protocol as prior
import define_runtime_from_factory_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = runtime.PREFIX + r'''
dec $test_factory_value_front(pstate, nat, nat) : bool
def $test_factory_value_front(S,n_factory,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY /\ pconfigcall.OWNER = (n_factory)
  -- if S.CURRENT = eps
def $test_factory_value_front(S,n_factory,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY /\ pconfigcall.OWNER = (n_factory)
  -- if S.CURRENT = (pcallcontext)
def $test_factory_value_front(S,n_factory,2) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $test_factory_value_front(S,n_factory,n_phase) = false -- otherwise
dec $test_factory_value_seek(pstate, nat, nat, nat) : pstate
def $test_factory_value_seek(S,n_factory,n_phase,0) = S
def $test_factory_value_seek(S,n_factory,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_factory_value_front(S,n_factory,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_factory_value_seek(S,n_factory,n_phase,n) = $test_factory_value_seek($drive_steps($test_running(S),1),n_factory,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_factory_value_front(S,n_factory,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, factory, phase):
    return [f'{state}_found = $test_factory_value_seek({start},{factory},{phase},1000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_factory_value_front({state},{factory},{phase})', *common.public(state)]


def factory(state, obj, label):
    return [f'{state}.OBJECTS[{obj}] = FROMCALLABLEFACTORY porigin_{label}',
        f'$from_factory_site({state},porigin_{label})',
        f'$from_factory_saved({state},{obj})', f'$from_factory_live({state},{obj})',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$node_children({state},HOBJECT {obj}) = eps',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def counter(state, value):
    return [f'{state}.STATICS = [pstaticcell_count]',
        f'$static_at({state}.STATICS,pstaticcell_count.ORIGIN) = (n_count)',
        'pstaticcell_count.CELL = n_count',
        f'n_count <- {state}.REFCELLS', f'HCELL n_count <- {state}.ALLOCATIONS',
        f'{state}.STORE[n_count] = DEFINED (PINT {value})',
        f'$heap_owners($heap_graph({state}),HCELL n_count) = 1']


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$global_constant_class_supported(PVARRAY false ([(KSTRING ($ptascii("edge")),PVOBJECT)]))',
        '~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_left pconfigcall.SITE)',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$from_factory_saved(S_dead,n_left)', '~$from_factory_live(S_dead,n_left)',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        'S_wrong_site = S[.OBJECTS[n_left] = FROMCALLABLEFACTORY pconfigcall.SITE]',
        '~$from_factory_saved(S_wrong_site,n_left)',
        '$dynamic_define_value_class(S_wrong_site,POBJECT n_left) = eps',
        'pclosurescope_bad = {OBJECT n_left,LEXICAL porigin_base,CALLED porigin_child,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_left)', '$closure_live_object_valid(S_scope,n_left)',
        '~$dynamic_runtime_object(S_scope,n_left)',
        'pclosurebinding_bad = {OBJECT n_left,SITE pconfigcall.SITE,SOURCE n_left,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_left)', '$closure_live_object_valid(S_binding,n_left)',
        '~$dynamic_runtime_object(S_binding,n_left)',
        'S_wrapped = S[.OBJECTS[n_left] = CONSTANTCLOSURE pconfigcall.SITE (S.OBJECTS[n_left])]',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_left) = eps',
        'S_internal = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_left)',
        'pconstantclosure_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_bad_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '$dynamic_define_value_class(S_bad_record,POBJECT n_left) = eps']


def direct(initial, stdout):
    before_query = stdout.split(b'F|null|', 1)[0] + b'F|null|'
    values = [*initial, *define.reach('S','S_initial',0,'V92_FACTORY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V92_FACTORY"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', 'pconfigcall.NAMED',
        'S.USERCONSTANTS = eps', 'S.CONSTANTCLOSURES = eps', 'S.STATICS = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_left_cv)',
        '$lookup(S.ENV,$ptascii("right")) = (n_right_cv)',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_right_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)', 'n_left =/= n_right',
        *scoped.classes('S','V92Base','V92Child'),
        *factory('S','n_left','left_create'), *factory('S','n_right','right_create'),
        '$closure_source_class(S,porigin_left_create) = (porigin_base)',
        '$closure_source_class(S,porigin_right_create) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','CLOSURESCOPES','CLOSUREBINDINGS','CONSTANTCLOSURES']]
    values += ['puserconstant_bad = puserconstant_row[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V92_FACTORY")) = eps',
        *common.reach('S_query','S_row',0,'V92_FACTORY'),
        '$dynamic_global_constant_value(S_query,$ptascii("V92_FACTORY")) = (POBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 3',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.OBJECTS = S_query.OBJECTS',
        *reach('S_denial','S_value','n_left',0),
        'S_denial.TODO = (CONFIG_INVOKE pconfigcall_denial) :: ptask_denial*',
        '$config_invoke_valid(S_denial,pconfigcall_denial)',
        'pconfigcall_denial.SENT = [NAMED_SENT (KNOWN (PARRAY n_denial_callback))]',
        'S_denial.ARRAYS[n_denial_callback].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_denial_class),ENTRY (KINT 1) (DIRECT pvalue_denial_method)]',
        '$string_bytes(pvalue_denial_class) = ($ptascii("V92Base"))',
        '$string_bytes(pvalue_denial_method) = ($ptascii("read"))',
        'S_denial.CURRENT = eps', 'S_denial.STATICS = eps',
        *reach('S_denied','S_denial','n_left',2),
        'S_denied.TODO = (THROW_SEARCH n_error) :: ptask_denied*',
        'S_denied.OBJECTS[n_error] = THROWABLE pthrowable_denied',
        'pthrowable_denied.KIND = "TypeError"',
        'pthrowable_denied.ORIGIN = (pconfigcall_denial.SITE)',
        '$throwable_field(S_denied,n_error,"previous") = PNULL',
        'S_denied.STATICS = eps', 'S_denied.USERCONSTANTS = S_row.USERCONSTANTS',
        *reach('S_user','S_denied','n_left',1),
        'S_user.TODO = (CONFIG_INVOKE pconfigcall_user) :: ptask_user*',
        '$config_invoke_valid(S_user,pconfigcall_user)',
        'S_user.CURRENT = (pcallcontext_user)',
        'pcallcontext_user.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_user.CALLED_CLASS = (porigin_child)',
        'pconfigcall_user.SENT = [NAMED_SENT (KNOWN (PARRAY n_user_callback))]',
        'S_user.ARRAYS[n_user_callback].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_user_class),ENTRY (KINT 1) (DIRECT pvalue_user_method)]',
        '$string_bytes(pvalue_user_class) = ($ptascii("V92Child"))',
        '$string_bytes(pvalue_user_method) = ($ptascii("read"))',
        'n_first_read = |S_user.OBJECTS|',
        *common.step('S_selecting','S_user'), *common.public('S_selecting'),
        'S_selecting.TODO = (API_CALLABLE_RESULT papiquery_select 0) :: ptask_user*',
        'S_selecting.RESULT = KNOWN PNULL',
        'papiquery_select.SOURCE = CONFIG_INVOKE pconfigcall_user',
        'papiquery_select.SCOPE = (porigin_base)',
        *common.step('S_selected','S_selecting','POBJECT n_first_read'),
        'S_selected.OBJECTS[n_first_read] = FROMCALLABLECLOSURE pfrommethod_first',
        'pfrommethod_first.FACTORY = (n_left)', 'pfrommethod_first.SCOPE = (porigin_base)',
        'pfrommethod_first.CLASS.CALLED = porigin_child', 'pfrommethod_first.STATIC',
        '$from_valid(S_selected,pfrommethod_first)',
        '$from_selected(S_selected,pfrommethod_first) = (pmethoddesc_read)',
        'pmethoddesc_read.OWNER = porigin_base', 'pmethoddesc_read.VISIBILITY = PROPERTY_PRIVATE',
        'pmethoddesc_read.FUNCTION.ORIGIN = porigin_body',
        '$node_children(S_selected,HOBJECT n_first_read) = eps',
        *define.reach('S_dup','S_selected',1,'V92_FACTORY'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V92_FACTORY"),POBJECT n_right))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        '$lookup(S_dup.ENV,$ptascii("right")) = eps', '~(HCELL n_right_cv <- S_dup.ALLOCATIONS)',
        '~(HOBJECT n_first_read <- S_dup.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 2',
        *counter('S_dup',1),
        '$static_function_at($class_method_functions(S_dup.CLASSES),pstaticcell_count.ORIGIN) = (pfunction_count)',
        'pfunction_count.ORIGIN = porigin_body', '$static_cells_valid(S_dup,S_dup.STATICS)',
        *common.step('S_warning','S_dup'), *common.public('S_warning'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        *define.reach('S_resume','S_warning',4,'V92_FACTORY'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED PNULL', 'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_resume.ENV,$ptascii("made")) = (n_made_cv)',
        'S_resume.STORE[n_made_cv] = DEFINED (POBJECT n_made)',
        'S_resume.OBJECTS[n_made] = FROMCALLABLECLOSURE pfrommethod_made',
        'pfrommethod_made.FACTORY = (n_right)', 'pfrommethod_made.SCOPE = (porigin_base)',
        'pfrommethod_made.FUNCTION = porigin_body', '$from_valid(S_resume,pfrommethod_made)',
        '$node_children(S_resume,HOBJECT n_made) = eps',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_right) = 1', *counter('S_resume',2),
        *common.reach('S_again_query','S_resume',0,'V92_FACTORY'), *common.public('S_again_query'),
        '~(HOBJECT n_right <- S_again_query.ALLOCATIONS)',
        '$from_factory_saved(S_again_query,n_right)', '~$from_factory_live(S_again_query,n_right)',
        '$from_valid(S_again_query,pfrommethod_made)',
        '$dynamic_define_value_class(S_again_query,POBJECT n_right) = eps',
        'S_again_query.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_again_query.EVENTS) = ' + term(before_query),
        *define.finish('S_again_query',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', *counter('S_final',4),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$node_children(S_final,HOBJECT n_left) = eps',
        '$from_factory_live(S_final,n_left)', '~$from_factory_live(S_final,n_right)',
        '~(HOBJECT n_made <- S_final.ALLOCATIONS)',
        '$heap_edge_owners(HCELL n_count,$heap_graph(S_final).EDGES,[HOBJECT n_left,HOBJECT n_right]) = 0']
    return values


def array(initial, stdout):
    edge = text('edge')
    before = stdout.removesuffix(b'after|S|41|V92ArrayChild|3|A|'); assert before != stdout
    return [*initial, *define.reach('S','S_initial',0,'V92_FACTORY_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V92_FACTORY_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)', 'S.USERCONSTANTS = eps', 'S.STATICS = eps',
        '$lookup(S.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_slot] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_slot)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        *scoped.classes('S','V92ArrayBase','V92ArrayChild'),
        *factory('S','n_closure','global_create'),
        '$closure_source_class(S,porigin_global_create) = eps', *scoped.static_values('S',23),
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'), '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.ARRAYS = S_validation.ARRAYS',
        'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE', 'S_row.CLOSURESCOPES = S.CLOSURESCOPES',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V92_FACTORY_ARRAY")) = (PARRAY n_root)',
        '$heap_owners($heap_graph(S_row),HOBJECT n_closure) = 2',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0', '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        *runtime.unset('S_observed','S_row','bucket'),
        '$lookup(S_observed.ENV,$ptascii("copy")) = (n_copy_cv)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_observed.ENV,$ptascii("bucket")) = (n_bucket)',
        '$lookup(S_observed.ENV,$ptascii("read")) = (n_read_cv)',
        'S_observed.STORE[n_copy_cv] = DEFINED (PARRAY n_copy)',
        'S_observed.STORE[n_again_cv] = DEFINED (PARRAY n_root)', 'n_copy =/= n_root',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (ALIAS n_bucket)',
        'S_observed.STORE[n_bucket] = DEFINED PNULL', 'S_observed.STORE[n_slot] = DEFINED PNULL',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 53))',
        'S_observed.ARRAYS[n_copy].NEXT = 1', 'S_observed.ARRAYS[n_root] = parray_root',
        'S_observed.STORE[n_read_cv] = DEFINED (POBJECT n_read)',
        'S_observed.OBJECTS[n_read] = FROMCALLABLECLOSURE pfrommethod_read',
        'pfrommethod_read.FACTORY = (n_closure)', 'pfrommethod_read.SCOPE = (porigin_base)',
        'pfrommethod_read.CLASS.CALLED = porigin_child', 'pfrommethod_read.STATIC',
        '$from_valid(S_observed,pfrommethod_read)', '$node_children(S_observed,HOBJECT n_read) = eps',
        *counter('S_observed',2),
        '$static_function_at($class_method_functions(S_observed.CLASSES),pstaticcell_count.ORIGIN) = (pfunction_count)',
        'pfunction_count.ORIGIN = pfrommethod_read.FUNCTION', '$static_cells_valid(S_observed,S_observed.STATICS)',
        *scoped.static_values('S_observed',41),
        '$node_children(S_observed,HOBJECT n_closure) = eps',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_closure) = 3',
        'S_observed.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.ARRAYS[n_root] = parray_root',
        *counter('S_final',3), '$node_children(S_final,HOBJECT n_closure) = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '~(HOBJECT n_read <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)', '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)', '~(HCELL n_bucket <- S_final.ALLOCATIONS)']


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 300 if directory.parent.name == DIRECT else 180
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
