#!/usr/bin/env python3
"""Reach enum magic dispatch, authentic source headers and named-buffer ownership."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enumm_class(pclassdesc*, pclassdesc) : pclassdesc*
def $enumm_class(eps, pclassdesc) = eps
def $enumm_class(pclassdesc_old :: pclassdesc*, pclassdesc_new) = pclassdesc_new :: pclassdesc*
  -- if pclassdesc_old.ORIGIN = pclassdesc_new.ORIGIN
def $enumm_class(pclassdesc_old :: pclassdesc*, pclassdesc_new) = pclassdesc_old :: $enumm_class(pclassdesc*,pclassdesc_new)
  -- if pclassdesc_old.ORIGIN =/= pclassdesc_new.ORIGIN
dec $enumm_method(pmethoddesc*, pmethoddesc) : pmethoddesc*
def $enumm_method(eps, pmethoddesc) = eps
def $enumm_method(pmethoddesc_old :: pmethoddesc*, pmethoddesc_new) = pmethoddesc_new :: pmethoddesc*
  -- if pmethoddesc_old.FUNCTION.ORIGIN = pmethoddesc_new.FUNCTION.ORIGIN
def $enumm_method(pmethoddesc_old :: pmethoddesc*, pmethoddesc_new) = pmethoddesc_old :: $enumm_method(pmethoddesc*,pmethoddesc_new)
  -- if pmethoddesc_old.FUNCTION.ORIGIN =/= pmethoddesc_new.FUNCTION.ORIGIN
dec $enumm_occurrence(pcoccurrence*, pcpath, pcnode) : pcoccurrence*
def $enumm_occurrence(eps, pcpath, pcnode) = eps
def $enumm_occurrence((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $enumm_occurrence((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $enumm_occurrence(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
dec $enumm_front(pstate, nat) : bool
def $enumm_front(S, 0) = true
  -- if S.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 0 eps) :: ptask_tail*
def $enumm_front(S, 1) = true
  -- if S.TODO = (CALL_ARGS (MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*) eps 2 poperand* porigin? z) :: ptask_tail*
def $enumm_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*
def $enumm_front(S, n) = false -- otherwise
dec $enumm_seek(pstate, nat, nat) : pstate
def $enumm_seek(S, n_phase, 0) = S
def $enumm_seek(S, n_phase, n) = S
  -- if $(n > 0)
  -- if $enumm_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumm_seek(S, n_phase, n) = $enumm_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumm_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def reach(label, prior, phase):
    return [label + '_found = $enumm_seek(' + prior + ',' + str(phase) + ',3000)',
            label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
            label + ' = $enumr_running(' + label + '_found)',
            '$enumm_front(' + label + ',' + str(phase) + ')',
            '$call_descriptors_valid(' + label + ')']


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id != 'user-magic-protocols':
        raise ValueError(case_id)
    checks = ['S_initial = $php_run(' + main_fixture + ',0,' +
              json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        *reach('S_named', 'S_initial', 0),
        'S_named.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 0 eps) :: ptask_named*',
        '$magic_method_caller(S_named,pmagicmethodcall)',
        '$magic_method_descriptor(S_named,pmagicmethodcall)',
        'n_case = pmagicmethodcall.OBJECT',
        '$enum_case_object(S_named,n_case) = (pclassconstantdesc_case)',
        'porigin_owner = pmagicmethodcall.CLASS',
        'porigin_owner = pclassconstantdesc_case.OWNER',
        '$class_at(S_named.CLASSES,porigin_owner) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "enum"',
        '$method_origin(pclassdesc_owner.METHODS,pmagicmethodcall.METHOD) = (pmethoddesc_call)',
        '$enum_magic_source(S_named,pmethoddesc_call,false)',
        '~$enum_magic_source(S_named,pmethoddesc_call,true)',
        'pmethoddesc_call.FUNCTION.SIGNATURE.PARAMETERS = [psparam_name,psparam_arguments]',
        'pmethoddesc_name = pmethoddesc_call[.FUNCTION = pmethoddesc_call.FUNCTION[.SIGNATURE = pmethoddesc_call.FUNCTION.SIGNATURE[.PARAMETERS = [psparam_name[.NAME = $ptascii("changed")],psparam_arguments]]]]',
        'S_name = S_named[.CLASSES = $enumm_class(S_named.CLASSES,pclassdesc_owner[.METHODS = $enumm_method(pclassdesc_owner.METHODS,pmethoddesc_name)])]',
        '~$enum_magic_source(S_name,pmethoddesc_name,false)',
        'pmethoddesc_ref = pmethoddesc_call[.FUNCTION = pmethoddesc_call.FUNCTION[.SIGNATURE = pmethoddesc_call.FUNCTION.SIGNATURE[.BYREF = true]]]',
        'S_ref = S_named[.CLASSES = $enumm_class(S_named.CLASSES,pclassdesc_owner[.METHODS = $enumm_method(pclassdesc_owner.METHODS,pmethoddesc_ref)])]',
        '~$enum_magic_source(S_ref,pmethoddesc_ref,false)',
        'pmethoddesc_return = pmethoddesc_call[.FUNCTION = pmethoddesc_call.FUNCTION[.SIGNATURE = pmethoddesc_call.FUNCTION.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]]]]',
        'S_return = S_named[.CLASSES = $enumm_class(S_named.CLASSES,pclassdesc_owner[.METHODS = $enumm_method(pclassdesc_owner.METHODS,pmethoddesc_return)])]',
        '~$enum_magic_source(S_return,pmethoddesc_return,false)',
        '~$enum_magic_source(S_named,pmethoddesc_call[.FUNCTION = pmethoddesc_call.FUNCTION[.ORIGIN = porigin_owner]],false)',
        'S_named.SOURCES = [pcunit_source]',
        'pmethoddesc_call.FUNCTION.ORIGIN = PORIGIN n_unit pcpath_method',
        'porigin_owner = PORIGIN n_unit pcpath_owner',
        '$origin_node(S_named.SOURCES,porigin_owner) = (NStmtEnum phpType14_owner phpType3_owner phpType50_owner phpType42_owner (SEQUENCE statement_owner*) metadata_owner)',
        '$origin_node(S_named.SOURCES,pmethoddesc_call.FUNCTION.ORIGIN) = (NStmtClassMethod phpType14_call (INTEGER flags_call) phpType4_call phpType11_call phpType16_call phpType18_call phpType47_call metadata_call)',
        'PCINDEX n_method = pcpath_method[$nabs($(|pcpath_method| - 1))]',
        'statement_badflags = NStmtClassMethod phpType14_call (INTEGER $(flags_call + 8)) phpType4_call phpType11_call phpType16_call phpType18_call phpType47_call metadata_call',
        'statement_badmembers* = statement_owner*[0:n_method] ++ [statement_badflags] ++ statement_owner*[$nabs($(n_method + 1)):$nabs($(|statement_owner*| - n_method - 1))]',
        'statement_badowner = NStmtEnum phpType14_owner phpType3_owner phpType50_owner phpType42_owner (SEQUENCE statement_badmembers*) metadata_owner',
        'S_flags = S_named[.SOURCES = [pcunit_source[.OCCURRENCES = $enumm_occurrence($enumm_occurrence(pcunit_source.OCCURRENCES,pcpath_owner,statement_badowner),pcpath_method,statement_badflags)]]]',
        '~$enum_magic_source(S_flags,pmethoddesc_call,false)',
        'S_zero = $drive_steps(S_named,0)',
        'S_zero = S_named[.COMPLETION = BUDGET]',
        *reach('S_pack', '$drive_steps($enumr_running(S_zero),1)', 1),
        'S_pack.TODO = (CALL_ARGS (MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*) eps 2 poperand* porigin? z) :: (MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*) :: METHOD_RESULT :: pmagicmethodcall.TAIL',
        'n_arguments = n_named',
        'pvalue* = [PINT 7]',
        '$magic_named_pending(S_pack,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S_pack,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$entry_lookup(S_pack.ARRAYS[n_named].ITEMS,KSTRING $ptascii("value")) = (DIRECT (PINT 7))',
        '(HARRAY n_named) <- S_pack.ALLOCATIONS',
        '(HARRAY n_named) <- $machine_roots(S_pack)',
        '(HOBJECT n_case) <- $task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*)',
        'S_without_marker = S_pack[.TODO = (CALL_ARGS (MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*) eps 2 poperand* porigin? z) :: METHOD_RESULT :: pmagicmethodcall.TAIL]',
        '~$magic_named_pending(S_without_marker,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        *reach('S_entered', '$drive_steps(S_pack,1)', 2),
        'S_entered.CURRENT = (pcallcontext_call)',
        'pcallcontext_call.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*',
        'pcallcontext_call.RECEIVER = (n_case)',
        'pcallcontext_call.INSTANCE = eps',
        'pcallcontext_call.CALLED_CLASS = (porigin_owner)',
        '$magic_named_entered(S_entered,S_entered.CURRENT,S_entered.FRAMES,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$lookup(S_entered.ENV,psparam_arguments.NAME) = (n_formal_cell)',
        'S_entered.STORE[n_formal_cell] = DEFINED (PARRAY n_formal)',
        '$entry_lookup(S_entered.ARRAYS[n_formal].ITEMS,KSTRING $ptascii("value")) = (DIRECT (PINT 7))',
        '(HARRAY n_named) <- $machine_roots(S_entered)',
        '(HOBJECT n_case) <- $class_constant_roots(S_entered.CLASSCONSTANTCACHE)',
        'S_finish = $drive_steps(S_entered,5000)',
        'S_finish.COMPLETION = NORMAL',
        'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '~((HARRAY n_named) <- S_finish.ALLOCATIONS)',
        '~((HARRAY n_formal) <- S_finish.ALLOCATIONS)',
        '(HOBJECT n_case) <- $class_constant_roots(S_finish.CLASSCONSTANTCACHE)',
        '$call_descriptors_valid(S_finish)',
    ]
    return checks
