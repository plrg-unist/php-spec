#!/usr/bin/env python3
"""Reach ordinary scoped lookup with its selected class string and source."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enuma_front(pstate) : bool
def $enuma_front(S) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_SCOPED_CLASS porigin pvalue z
def $enuma_front(S) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_SCOPED_SELECTED porigin poperand ptbytes z
def $enuma_front(S) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_CLASS_CONST_CLASS porigin pvalue z
def $enuma_front(S) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_CLASS_CONST_SELECTED porigin poperand ptbytes z
def $enuma_front(S) = false -- otherwise
dec $enuma_seek(pstate, nat) : pstate
def $enuma_seek(S, 0) = S
def $enuma_seek(S, n) = S
  -- if $(n > 0)
  -- if $enuma_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enuma_seek(S, n) = $enuma_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enuma_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
dec $enuma_seek_other(pstate, porigin, nat) : pstate
def $enuma_seek_other(S, porigin_previous, 0) = S
def $enuma_seek_other(S, porigin_previous, n) = S
  -- if $(n > 0)
  -- if ($enuma_front(S) /\ S.ORIGIN =/= (porigin_previous)) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enuma_seek_other(S, porigin_previous, n) = $enuma_seek_other($drive_steps($enumr_running(S),1),porigin_previous,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enuma_front(S) \/ S.ORIGIN = (porigin_previous)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
dec $enuma_stage(pstate, porigin, nat) : bool
def $enuma_stage(S, porigin, 0) = true
  -- if S.TODO = (AUTO_SCOPED_CLASS porigin pvalue z) :: ptask_tail*
def $enuma_stage(S, porigin, 0) = true
  -- if S.TODO = (AUTO_SCOPED_SELECTED porigin poperand ptbytes z) :: ptask_tail*
def $enuma_stage(S, porigin, 0) = true
  -- if S.TODO = (AUTO_CLASS_CONST_CLASS porigin pvalue z) :: ptask_tail*
def $enuma_stage(S, porigin, 0) = true
  -- if S.TODO = (AUTO_CLASS_CONST_SELECTED porigin poperand ptbytes z) :: ptask_tail*
def $enuma_stage(S, porigin, 1) = true
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* 0 eps (porigin) z) :: ptask_tail*
def $enuma_stage(S, porigin, 1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = porigin
  -- if pconfigcall.INDEX = 0 /\ pconfigcall.SENT = eps
def $enuma_stage(S, porigin, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 ([KNOWN (PINT 7)]) (porigin) z) :: ptask_tail*
def $enuma_stage(S, porigin, 3) = true
  -- if S.ORIGIN = (porigin)
  -- if S.TODO = (CLASS_CONST_MEMBER phpType19 poperand z) :: ptask_tail*
def $enuma_stage(S, porigin, n_phase) = false -- otherwise
dec $enuma_seek_stage(pstate, porigin, nat, nat) : pstate
def $enuma_seek_stage(S, porigin, n_phase, 0) = S
def $enuma_seek_stage(S, porigin, n_phase, n) = S
  -- if $(n > 0)
  -- if $enuma_stage(S, porigin, n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enuma_seek_stage(S, porigin, n_phase, n) = $enuma_seek_stage($drive_steps($enumr_running(S),1),porigin,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enuma_stage(S, porigin, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
dec $enuma_compiled_front(pstate) : bool
def $enuma_compiled_front(S) = true
  -- if S.TODO = (SCOPED_NAME phpType19 (KNOWN (PSTRING ptbytes)) phpType7* z) :: ptask_tail*
  -- if ~$ppscoped_named(phpType19)
  -- if $origin_child(S.ORIGIN,[PCFIELD 0]) = (porigin)
  -- if $compiled_read(S,porigin) = (PSTRING ptbytes_raw)
def $enuma_compiled_front(S) = false -- otherwise
dec $enuma_seek_compiled(pstate, nat) : pstate
def $enuma_seek_compiled(S, 0) = S
def $enuma_seek_compiled(S, n) = S
  -- if $(n > 0)
  -- if $enuma_compiled_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enuma_seek_compiled(S, n) = $enuma_seek_compiled($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enuma_compiled_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def assertions(case_id, main_fixture, source_path, expected_bytes, eval_response=None):
    if case_id == 'compiled-class-target-negative':
        return target_negative_assertions(main_fixture, source_path, expected_bytes, eval_response)
    if case_id == 'compiler-folded-static-keyword-scopes':
        return keyword_assertions(main_fixture, source_path, expected_bytes)
    if case_id == 'literal-slash-missing-diagnostics':
        return slash_assertions(main_fixture, source_path, expected_bytes)
    if case_id == 'named-class-computed-constant':
        return selected_constant_assertions(main_fixture, source_path, expected_bytes, eval_response)
    if case_id == 'literal-and-folded-class-method-order':
        return folded_assertions(main_fixture, source_path, expected_bytes, eval_response)
    if case_id == 'dynamic-class-computed-constant':
        return constant_assertions(main_fixture, source_path, expected_bytes, eval_response)
    if case_id != 'static-loader-cv-order-start':
        return complete_assertions(case_id, main_fixture, source_path, expected_bytes, eval_response)
    return start_assertions(main_fixture, source_path)


def start_assertions(main_fixture, source_path):
    return ['S_initial = $php_run(' + main_fixture + ',0,' +
            json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_begin_found = $enuma_seek(S_initial,3000)',
        r'S_begin_found.COMPLETION = NORMAL \/ S_begin_found.COMPLETION = BUDGET',
        'S_begin = $enumr_running(S_begin_found)', '$enuma_front(S_begin)',
        '$call_descriptors_valid(S_begin)',
        'S_begin.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        'pautoloadcall.RESUME = AUTO_SCOPED_CLASS porigin pvalue_class z',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin',
        'pautoloadcall.LINE = z',
        'pvalue_class = PSTRING_CARRIER pstringidentity ptbytes_class',
        'ptbytes_class = $ptascii("ReviewCvAcquisitionClass")',
        'pautoloadcall.NAME = ptbytes_class', 'pautoloadcall.KEY = $ptlc(ptbytes_class)',
        '$string_carrier_valid(S_begin,pvalue_class)',
        '$value_nodes(pvalue_class) = eps', '$task_nodes(pautoloadcall.RESUME) = eps',
        '$lookup(S_begin.ENV,$ptascii("class")) = (n_class_cell)',
        'S_begin.STORE[n_class_cell] = DEFINED pvalue_class',
        '$autoload_call_valid(S_begin,pautoloadcall)',
        '$autoload_scoped_class_site(S_begin,porigin,pvalue_class,z)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S_begin.STRINGDATA|)) ptbytes_class',
        '~$string_carrier_valid(S_begin,pvalue_bad)',
        '~$autoload_scoped_class_site(S_begin,porigin,pvalue_bad,z)',
        '~$autoload_call_valid(S_begin,pautoloadcall[.RESUME = AUTO_SCOPED_CLASS porigin pvalue_bad z])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.KEY = $ptascii("wrong")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.NAME = $ptascii("WrongClass")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.LINE = $(z + 1)])',
        '~$autoload_scoped_class_site(S_begin,porigin,PNULL,z)',
        'S_zero = $drive_steps(S_begin,0)', 'S_zero = S_begin[.COMPLETION = BUDGET]',
        'S_one = $enumr_running($drive_steps($enumr_running(S_zero),1))',
        '$call_descriptors_valid(S_one)',
        '$enumr_output(S_one.EVENTS) = eps']


def reach(label, prior, phase):
    return [label + '_found = $enuma_seek_stage(' + prior + ',porigin,' + str(phase) + ',3000)',
            label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
            label + ' = $enumr_running(' + label + '_found)',
            '$enuma_stage(' + label + ',porigin,' + str(phase) + ')',
            '$call_descriptors_valid(' + label + ')']


def complete_assertions(case_id, main_fixture, source_path, expected_bytes, eval_response):
    if case_id not in ('static-loader-cv-order', 'named-static-computed-method', 'static-first-use'):
        raise ValueError(case_id)
    dynamic = case_id == 'static-loader-cv-order'
    generated = case_id == 'static-first-use'
    owner, method, before, loaded = {
        'static-loader-cv-order': (b'ReviewCvAcquisitionClass', b'afterLoad', b'', b'L:ReviewCvAcquisitionClass|'),
        'named-static-computed-method': (b'ReviewNamedMethodAcquisition', b'selected', b'R:METHOD|', b'R:METHOD|L:ReviewNamedMethodAcquisition|'),
        'static-first-use': (b'ReviewStaticFirstEnum', b'cases', b'', b'L:ReviewStaticFirstEnum|'),
    }[case_id]
    checks = ['S_initial = $php_run(' + main_fixture + ',0,' +
            json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_begin_found = $enuma_seek(S_initial,3000)',
        r'S_begin_found.COMPLETION = NORMAL \/ S_begin_found.COMPLETION = BUDGET',
        'S_begin = $enumr_running(S_begin_found)', '$enuma_front(S_begin)',
        '$call_descriptors_valid(S_begin)',
        'S_begin.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        ('pautoloadcall.RESUME = AUTO_SCOPED_CLASS porigin pvalue_class z' if dynamic else
         'pautoloadcall.RESUME = AUTO_SCOPED_SELECTED porigin (KNOWN (PSTRING ptbytes_class)) ptbytes_method z'),
        'ptbytes_class = ' + term(owner),
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin',
        'pautoloadcall.LINE = z',
        'pautoloadcall.NAME = ptbytes_class', 'pautoloadcall.KEY = $ptlc(ptbytes_class)',
        '$task_nodes(pautoloadcall.RESUME) = eps',
        '$autoload_call_valid(S_begin,pautoloadcall)',
        '~$autoload_call_valid(S_begin,pautoloadcall[.KEY = $ptascii("wrong")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.NAME = $ptascii("WrongClass")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.LINE = $(z + 1)])',
        '$enumr_output(S_begin.EVENTS) = ' + term(before),
        'S_zero = $drive_steps(S_begin,0)', 'S_zero = S_begin[.COMPLETION = BUDGET]',
        'S_wait = $drive_steps($enumr_running(S_zero),5000)',
        'S_wait.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_wait)',
        '$enumr_output(S_wait.EVENTS) = ' + term(loaded),
        'S_wait.FRAMES = pframe_loader :: pframe_tail*',
        'pframe_loader.TODO = (AUTO_RESULT pautoloadcall_entered pautoloadentry poperand_sent) :: ptask_loader*',
        'pautoloadcall_entered.RESUME = pautoloadcall.RESUME',
        'pautoloadcall_entered.SITE = porigin',
        'pautoloadcall_entered.BIRTH =/= eps',
        'S_saved = $constant_frame_scope(S_wait,pframe_loader,pframe_tail*)',
        '$autoload_selected_valid(S_saved,pautoloadcall_entered,pautoloadentry)',
        '$autoload_declaration_resume(S_wait,pautoloadcall_entered)',
        '~$autoload_declaration_resume(S_wait,pautoloadcall_entered[.LINE = $(z + 1)])',
        '$eval_response_valid(S_wait,' + eval_response + ')',
        'S_body = $eval_resume(S_wait,' + eval_response + ')',
        'S_body.COMPLETION = NORMAL', '$call_descriptors_valid(S_body)',
        *reach('S_resume', 'S_body', 0),
        'S_resume.TODO = pautoloadcall.RESUME :: ptask_resume*',
        'S_resume.ORIGIN = (porigin)',
        'S_resume.FRAMES = eps',
        '$call_task_valid(S_resume,pautoloadcall.RESUME)',
        '$class_named(S_resume.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_class)',
        '$class_at(S_resume.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = ptbytes_class',
        '$enumr_output(S_resume.EVENTS) = ' + term(loaded),
    ]
    if dynamic:
        checks += [
            '$string_bytes(pvalue_class) = (ptbytes_class)',
            '$lookup(S_begin.ENV,$ptascii("class")) = (n_class_cell)',
            '$lookup(S_begin.ENV,$ptascii("method")) = (n_method_cell)',
            'S_begin.STORE[n_class_cell] = DEFINED pvalue_class',
            'S_resume.STORE[n_class_cell] = DEFINED pvalue_rebound_class',
            '$string_bytes(pvalue_rebound_class) = ($ptascii("ChangedDuringLoader"))',
            'S_resume.STORE[n_method_cell] = DEFINED pvalue_rebound_method',
            '$string_bytes(pvalue_rebound_method) = ($ptascii("afterLoad"))',
            'pvalue_rebound_class =/= pvalue_class',
        ]
    else:
        checks += ['ptbytes_method = ' + term(method)]
    checks += [*reach('S_target', 'S_resume', 1),
               '$enumr_output(S_target.EVENTS) = ' + term(loaded)]
    if generated:
        checks += [
            'pclassdesc.KIND = "enum"',
            'S_target.TODO = (CONFIG_ARGS pconfigcall) :: ptask_target*',
            'pconfigcall.KIND = INTRINSIC_ENUM porigin_class ptbytes_class "cases"',
            'pconfigcall.SITE = porigin', 'pconfigcall.LINE = z',
            'pconfigcall.OWNER = eps', 'pconfigcall.SENT = eps',
            '$enum_call_site(S_target,porigin,pconfigcall.KIND)',
            '$class_constant_lookup(S_target,porigin_class,$ptascii("Only"),|S_target.CLASSES|) = (pclassconstantdesc_case)',
            '$default_cache_at(S_target.CLASSCONSTANTCACHE,pclassconstantdesc_case.ORIGIN) = eps',
        ]
    else:
        checks += [
            'S_target.TODO = (CALL_ARGS pcalltarget phpType7* 0 eps (porigin) z) :: ptask_target*',
            'pcalltarget = SCOPED_TARGET porigin_class porigin_method porigin_class eps poperand_selector',
            'poperand_selector = KNOWN (PSTRING ptbytes_class)',
            '$target_function(S_target,pcalltarget) = (pfunction)',
            '$class_method_origin(S_target.CLASSES,porigin_method) = (pmethoddesc)',
            'pfunction = pmethoddesc.FUNCTION',
            'pmethoddesc.NAME = ' + term(method),
            '$target_nodes(pcalltarget) = eps',
            *reach('S_arguments', 'S_target', 2),
            'S_arguments.TODO = (CALL_ARGS pcalltarget eps 1 ([KNOWN (PINT 7)]) (porigin) z) :: ptask_target*',
            '$target_function(S_arguments,pcalltarget) = (pfunction)',
            '$enumr_output(S_arguments.EVENTS) = ' + term(loaded + b'ARG|'),
        ]
        if dynamic:
            checks += [
                'S_arguments.STORE[n_class_cell] = DEFINED pvalue_argument_class',
                '$string_bytes(pvalue_argument_class) = ($ptascii("ChangedAfterArgument"))',
                'S_arguments.STORE[n_method_cell] = DEFINED pvalue_argument_method',
                '$string_bytes(pvalue_argument_method) = ($ptascii("afterArgument"))',
                'pvalue_argument_class =/= pvalue_class',
            ]
    finish_from = 'S_target' if generated else 'S_arguments'
    return checks + [
        'S_finish = $drive_steps(' + finish_from + ',5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def constant_assertions(main_fixture, source_path, expected_bytes, eval_response):
    raw = b'\\rEvIeWdYnAmIcCoNsTaNtAcQuIsItIoN'
    loaded = b'R:CLASS|L:rEvIeWdYnAmIcCoNsTaNtAcQuIsItIoN|'
    return [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin_found = $enuma_seek(S_initial,3000)',
        r'S_begin_found.COMPLETION = NORMAL \/ S_begin_found.COMPLETION = BUDGET',
        'S_begin = $enumr_running(S_begin_found)', '$enuma_front(S_begin)',
        '$call_descriptors_valid(S_begin)',
        'S_begin.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        'pautoloadcall.RESUME = AUTO_CLASS_CONST_CLASS porigin pvalue_class z',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin',
        'pautoloadcall.LINE = z', '$string_bytes(pvalue_class) = (ptbytes_raw)',
        'ptbytes_raw = ' + term(raw),
        'pautoloadcall.NAME = $ppcall_literal_name(ptbytes_raw)',
        'pautoloadcall.KEY = $ptlc(pautoloadcall.NAME)',
        '$autoload_call_valid(S_begin,pautoloadcall)',
        '$task_nodes(pautoloadcall.RESUME) = eps',
        '$autoload_class_constant_class_site(S_begin,porigin,pvalue_class,z)',
        '~$autoload_class_constant_selected_site(S_begin,porigin,KNOWN (PSTRING ptbytes_raw),$ptascii("AfterLoad"),z)',
        '~$autoload_scoped_class_site(S_begin,porigin,pvalue_class,z)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S_begin.STRINGDATA|)) ptbytes_raw',
        '~$autoload_class_constant_class_site(S_begin,porigin,pvalue_bad,z)',
        '~$autoload_call_valid(S_begin,pautoloadcall[.RESUME = AUTO_CLASS_CONST_CLASS porigin pvalue_bad z])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.KEY = $ptascii("wrong")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.LINE = $(z + 1)])',
        '$lookup(S_begin.ENV,$ptascii("class")) = (n_class_cell)',
        '$lookup(S_begin.ENV,$ptascii("member")) = (n_member_cell)',
        'S_begin.STORE[n_class_cell] = DEFINED pvalue_class',
        '$enumr_output(S_begin.EVENTS) = ' + term(b'R:CLASS|'),
        'S_zero = $drive_steps(S_begin,0)', 'S_zero = S_begin[.COMPLETION = BUDGET]',
        'S_wait = $drive_steps($enumr_running(S_zero),5000)',
        'S_wait.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_wait)',
        '$enumr_output(S_wait.EVENTS) = ' + term(loaded),
        'S_wait.FRAMES = pframe_loader :: pframe_tail*',
        'pframe_loader.TODO = (AUTO_RESULT pautoloadcall_entered pautoloadentry poperand_sent) :: ptask_loader*',
        'pautoloadcall_entered.RESUME = pautoloadcall.RESUME',
        'S_saved = $constant_frame_scope(S_wait,pframe_loader,pframe_tail*)',
        '$autoload_selected_valid(S_saved,pautoloadcall_entered,pautoloadentry)',
        '$autoload_declaration_resume(S_wait,pautoloadcall_entered)',
        '~$autoload_declaration_resume(S_wait,pautoloadcall_entered[.LINE = $(z + 1)])',
        '$eval_response_valid(S_wait,' + eval_response + ')',
        'S_body = $eval_resume(S_wait,' + eval_response + ')',
        'S_body.COMPLETION = NORMAL', '$call_descriptors_valid(S_body)',
        *reach('S_resume', 'S_body', 0),
        'S_resume.TODO = (AUTO_CLASS_CONST_CLASS porigin pvalue_class z) :: ptask_resume*',
        '$call_task_valid(S_resume,pautoloadcall.RESUME)',
        '~$call_task_valid(S_resume,AUTO_CLASS_CONST_CLASS porigin pvalue_bad z)',
        'S_resume.STORE[n_class_cell] = DEFINED pvalue_rebound_class',
        '$string_bytes(pvalue_rebound_class) = ($ptascii("ChangedDuringLoader"))',
        'S_resume.STORE[n_member_cell] = DEFINED pvalue_rebound_member',
        '$string_bytes(pvalue_rebound_member) = ($ptascii("AfterLoad"))',
        '$class_named(S_resume.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_raw))) = (porigin_class)',
        '$class_at(S_resume.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = $ptascii("ReviewDynamicConstantAcquisition")',
        '$origin_node(S_resume.SOURCES,porigin) = (NExprClassConstFetch expression_class expression_member metadata)',
        'PhpStep: S_resume ~> S_member_start',
        'S_member_start.COMPLETION = NORMAL', '$call_descriptors_valid(S_member_start)',
        'ptask_member = $at_task($origin_child((porigin),[PCFIELD 1]),EVAL expression_member)',
        'S_member_start.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING pclassdesc.NAME)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING pclassdesc.NAME)) z) :: ptask_resume*',
        '$enumr_output(S_member_start.EVENTS) = ' + term(loaded),
        *reach('S_member', 'S_member_start', 3),
        'S_member.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING pclassdesc.NAME)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING pclassdesc.NAME)) z) :: ptask_resume*',
        'S_member.RESULT = KNOWN pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("AfterLoad"))',
        'S_member.STORE[n_class_cell] = DEFINED pvalue_after_class',
        '$string_bytes(pvalue_after_class) = ($ptascii("ChangedAfterMember"))',
        'S_member.STORE[n_member_cell] = DEFINED pvalue_after_member',
        '$string_bytes(pvalue_after_member) = ($ptascii("afterMember"))',
        '$class_constant_member_task_valid(S_member,expression_class,KNOWN (PSTRING pclassdesc.NAME),z)',
        '~$class_constant_member_task_valid(S_member,expression_class,KNOWN (PSTRING ($ptascii("ChangedAfterMember"))),z)',
        '$enumr_output(S_member.EVENTS) = ' + term(loaded + b'MEMBER|'),
        'S_finish = $drive_steps(S_member,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def folded_assertions(main_fixture, source_path, expected_bytes, eval_responses):
    assert len(eval_responses) == 2
    checks = [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    prior = 'S_initial'
    for label, owner, before, response in (
        ('lit', b'ReviewLiteralStringClass', b'LIT:METHOD|', eval_responses[0]),
        ('fold', b'ReviewFoldedStringClass', b'LIT:METHOD|L:ReviewLiteralStringClass|BEFORE|FOLD:METHOD|', eval_responses[1]),
    ):
        loaded = before + b'L:' + owner + b'|'
        checks += [
            f'S_{label}_pre_found = $enuma_seek_compiled({prior},3000)',
            rf'S_{label}_pre_found.COMPLETION = NORMAL \/ S_{label}_pre_found.COMPLETION = BUDGET',
            f'S_{label}_pre = $enumr_running(S_{label}_pre_found)',
            f'$enuma_compiled_front(S_{label}_pre)',
            f'$call_descriptors_valid(S_{label}_pre)',
            f'S_{label}_pre.ORIGIN = (porigin_{label})',
            f'S_{label}_pre.TODO = (SCOPED_NAME phpType19_{label} (KNOWN (PSTRING ptbytes_{label})) phpType7_{label}* z_{label}) :: ptask_{label}_tail*',
            f'ptbytes_{label} = ' + term(owner),
            f'$origin_child((porigin_{label}),[PCFIELD 0]) = (porigin_{label}_child)',
            f'$compiled_read(S_{label}_pre,porigin_{label}_child) = (PSTRING ptbytes_{label})',
            f'~$ppscoped_named(phpType19_{label})',
            f'$scoped_class_literal(S_{label}_pre,phpType19_{label})',
            f'$class_named(S_{label}_pre.CLASSNAMES,$ptlc(ptbytes_{label})) = eps',
            f'$scoped_name_task(S_{label}_pre,phpType19_{label},KNOWN (PSTRING ptbytes_{label}),phpType7_{label}*,z_{label})',
            f'~$scoped_name_task(S_{label}_pre,phpType19_{label},KNOWN (PSTRING ($ptascii("WrongClass"))),phpType7_{label}*,z_{label})',
            f'~$autoload_scoped_class_site(S_{label}_pre,porigin_{label},PSTRING ptbytes_{label},z_{label})',
            f'~$autoload_scoped_selected_site(S_{label}_pre,porigin_{label}_child,KNOWN (PSTRING ptbytes_{label}),$ptascii("before"),z_{label})',
            f'S_{label}_pre.RESULT = KNOWN pvalue_{label}_method',
            f'$string_bytes(pvalue_{label}_method) = ($ptascii("before"))',
            f'$enumr_output(S_{label}_pre.EVENTS) = ' + term(before),
            f'$lookup(S_{label}_pre.ENV,$ptascii("method")) = (n_{label}_method)',
            f'S_{label}_zero = $drive_steps(S_{label}_pre,0)',
            f'S_{label}_zero = S_{label}_pre[.COMPLETION = BUDGET]',
            f'PhpStep: S_{label}_pre ~> S_{label}_begin',
            f'S_{label}_begin.COMPLETION = NORMAL',
            f'$call_descriptors_valid(S_{label}_begin)',
            f'S_{label}_begin.TODO = (AUTO_NEXT pautoloadcall_{label}) :: ptask_{label}_begin*',
            f'pautoloadcall_{label}.RESUME = AUTO_SCOPED_SELECTED porigin_{label} (KNOWN (PSTRING ptbytes_{label})) ($ptascii("before")) z_{label}',
            f'pautoloadcall_{label}.NAME = ptbytes_{label}',
            f'$autoload_call_valid(S_{label}_begin,pautoloadcall_{label})',
            f'~$autoload_scoped_selected_site(S_{label}_begin,porigin_{label},KNOWN (PSTRING ($ptascii("WrongClass"))),$ptascii("before"),z_{label})',
            f'~$autoload_call_valid(S_{label}_begin,pautoloadcall_{label}[.LINE = $(z_{label} + 1)])',
            f'S_{label}_one = $enumr_running($drive_steps($enumr_running(S_{label}_zero),1))',
            f'S_{label}_one.TODO = S_{label}_begin.TODO',
            f'S_{label}_one.AUTOLOAD = S_{label}_begin.AUTOLOAD',
            f'$call_descriptors_valid(S_{label}_one)',
            f'S_{label}_wait = $drive_steps(S_{label}_begin,5000)',
            f'S_{label}_wait.COMPLETION = SOURCE_PENDING',
            f'$call_descriptors_valid(S_{label}_wait)',
            f'$enumr_output(S_{label}_wait.EVENTS) = ' + term(loaded),
            f'$eval_response_valid(S_{label}_wait,{response})',
            f'S_{label}_body = $eval_resume(S_{label}_wait,{response})',
            f'S_{label}_resume_found = $enuma_seek_stage(S_{label}_body,porigin_{label},0,3000)',
            rf'S_{label}_resume_found.COMPLETION = NORMAL \/ S_{label}_resume_found.COMPLETION = BUDGET',
            f'S_{label}_resume = $enumr_running(S_{label}_resume_found)',
            f'$call_descriptors_valid(S_{label}_resume)',
            f'S_{label}_resume.TODO = (AUTO_SCOPED_SELECTED porigin_{label} (KNOWN (PSTRING ptbytes_{label})) ($ptascii("before")) z_{label}) :: ptask_{label}_resume*',
            f'S_{label}_resume.STORE[n_{label}_method] = DEFINED pvalue_{label}_rebound',
            f'$string_bytes(pvalue_{label}_rebound) = ($ptascii("after"))',
            f'$class_named(S_{label}_resume.CLASSNAMES,$ptlc(ptbytes_{label})) = (porigin_{label}_class)',
        ]
        prior = f'S_{label}_resume'
    return checks + [
        f'S_finish = $drive_steps({prior},5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def selected_constant_assertions(main_fixture, source_path, expected_bytes, eval_response):
    return [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin_found = $enuma_seek(S_initial,3000)',
        r'S_begin_found.COMPLETION = NORMAL \/ S_begin_found.COMPLETION = BUDGET',
        'S_begin = $enumr_running(S_begin_found)', '$enuma_front(S_begin)',
        '$call_descriptors_valid(S_begin)',
        'S_begin.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        'pautoloadcall.RESUME = AUTO_CLASS_CONST_SELECTED porigin poperand_class ptbytes_member z',
        'poperand_class = KNOWN (PSTRING ptbytes_class)',
        'ptbytes_class = $ptascii("ReviewNamedConstantAcquisition")',
        'ptbytes_member = $ptascii("Choice")',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin',
        'pautoloadcall.LINE = z', 'pautoloadcall.NAME = ptbytes_class',
        'pautoloadcall.KEY = $ptlc(ptbytes_class)',
        '$autoload_call_valid(S_begin,pautoloadcall)',
        '$task_nodes(pautoloadcall.RESUME) = eps',
        '$class_named(S_begin.CLASSNAMES,$ptlc(ptbytes_class)) = eps',
        '$origin_node(S_begin.SOURCES,porigin) = (NExprClassConstFetch phpType19 expression_member metadata)',
        '$class_constant_literal(S_begin,phpType19)',
        '$autoload_class_constant_literal_name(S_begin,porigin,phpType19) = (ptbytes_class)',
        '$autoload_class_constant_selected_site(S_begin,porigin,poperand_class,ptbytes_member,z)',
        '~$autoload_class_constant_selected_site(S_begin,porigin,KNOWN (PSTRING ($ptascii("WrongClass"))),ptbytes_member,z)',
        '~$autoload_class_constant_class_site(S_begin,porigin,PSTRING ptbytes_class,z)',
        '~$autoload_scoped_selected_site(S_begin,porigin,poperand_class,ptbytes_member,z)',
        '~$autoload_call_valid(S_begin,pautoloadcall[.KEY = $ptascii("wrong")])',
        '~$autoload_call_valid(S_begin,pautoloadcall[.LINE = $(z + 1)])',
        '$enumr_output(S_begin.EVENTS) = ' + term(b'K:MEMBER|'),
        'S_zero = $drive_steps(S_begin,0)', 'S_zero = S_begin[.COMPLETION = BUDGET]',
        'S_wait = $drive_steps($enumr_running(S_zero),5000)',
        'S_wait.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_wait)',
        '$enumr_output(S_wait.EVENTS) = ' + term(b'K:MEMBER|L:ReviewNamedConstantAcquisition|'),
        'S_wait.FRAMES = pframe_loader :: pframe_tail*',
        'pframe_loader.TODO = (AUTO_RESULT pautoloadcall_entered pautoloadentry poperand_sent) :: ptask_loader*',
        'pautoloadcall_entered.RESUME = pautoloadcall.RESUME',
        'S_saved = $constant_frame_scope(S_wait,pframe_loader,pframe_tail*)',
        '$autoload_selected_valid(S_saved,pautoloadcall_entered,pautoloadentry)',
        '$autoload_declaration_resume(S_wait,pautoloadcall_entered)',
        '$autoload_class_constant_selected_site(S_wait,porigin,poperand_class,ptbytes_member,z)',
        '~$autoload_declaration_resume(S_wait,pautoloadcall_entered[.LINE = $(z + 1)])',
        '$eval_response_valid(S_wait,' + eval_response + ')',
        'S_body = $eval_resume(S_wait,' + eval_response + ')',
        'S_body.COMPLETION = NORMAL', '$call_descriptors_valid(S_body)',
        *reach('S_resume', 'S_body', 0),
        'S_resume.TODO = (AUTO_CLASS_CONST_SELECTED porigin poperand_class ptbytes_member z) :: ptask_resume*',
        'S_resume.ORIGIN = (porigin)', '$call_task_valid(S_resume,pautoloadcall.RESUME)',
        '~$call_task_valid(S_resume,AUTO_CLASS_CONST_SELECTED porigin poperand_class ptbytes_member $(z + 1))',
        '$class_named(S_resume.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_class)',
        '$class_constant_lookup(S_resume,porigin_class,ptbytes_member,|S_resume.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.FOLDED',
        '$compiled_read(S_resume,pclassconstantdesc.INITIALIZER) = (PINT 23)',
        '$enumr_output(S_resume.EVENTS) = ' + term(b'K:MEMBER|L:ReviewNamedConstantAcquisition|'),
        'S_finish = $drive_steps(S_resume,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def slash_assertions(main_fixture, source_path, expected_bytes):
    checks = [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    prior = 'S_initial'
    for label, owner, constructor, member, before in (
        ('static', b'ReviewLiteralMissingStatic', 'AUTO_SCOPED_SELECTED', b'missing', b''),
        ('constant', b'ReviewLiteralMissingConstant', 'AUTO_CLASS_CONST_SELECTED', b'Choice', b'L:ReviewLiteralMissingStatic|S:Class "ReviewLiteralMissingStatic" not found|'),
    ):
        checks += [
            (f'S_{label}_found = $enuma_seek({prior},3000)' if label == 'static' else
             f'S_{label}_found = $enuma_seek_other({prior},porigin_static,3000)'),
            rf'S_{label}_found.COMPLETION = NORMAL \/ S_{label}_found.COMPLETION = BUDGET',
            f'S_{label} = $enumr_running(S_{label}_found)',
            f'$call_descriptors_valid(S_{label})',
            f'S_{label}.TODO = (AUTO_NEXT pautoloadcall_{label}) :: ptask_{label}_tail*',
            f'pautoloadcall_{label}.RESUME = {constructor} porigin_{label} (KNOWN (PSTRING ptbytes_{label})) ptbytes_{label}_member z_{label}',
            f'ptbytes_{label} = ' + term(owner),
            f'ptbytes_{label}_member = ' + term(member),
            f'pautoloadcall_{label}.NAME = ptbytes_{label}',
            f'$autoload_call_valid(S_{label},pautoloadcall_{label})',
            f'$origin_child((porigin_{label}),[PCFIELD 0]) = (porigin_{label}_child)',
            f'$compiled_read(S_{label},porigin_{label}_child) = (PSTRING ptbytes_{label}_raw)',
            f'ptbytes_{label}_raw = ' + term(b'\\' + owner),
            f'ptbytes_{label} =/= ptbytes_{label}_raw',
            f'~$autoload_call_valid(S_{label},pautoloadcall_{label}[.RESUME = {constructor} porigin_{label} (KNOWN (PSTRING ptbytes_{label}_raw)) ptbytes_{label}_member z_{label}])',
            f'$enumr_output(S_{label}.EVENTS) = ' + term(before),
            f'S_{label}_zero = $drive_steps(S_{label},0)',
            f'S_{label}_zero = S_{label}[.COMPLETION = BUDGET]',
            f'S_{label}_one = $enumr_running($drive_steps($enumr_running(S_{label}_zero),1))',
            f'$call_descriptors_valid(S_{label}_one)',
        ]
        if label == 'constant':
            checks += [
                '$origin_node(S_constant.SOURCES,porigin_constant) = (NExprClassConstFetch phpType19 phpType20 metadata)',
                '$class_constant_selected_valid(S_constant,phpType19,KNOWN (PSTRING ptbytes_constant))',
                '~$class_constant_selected_valid(S_constant,phpType19,KNOWN (PSTRING ptbytes_constant_raw))',
            ]
        prior = f'S_{label}_one'
    return checks + [
        f'S_finish = $drive_steps({prior},5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def keyword_assertions(main_fixture, source_path, expected_bytes):
    checks = [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    prior = 'S_initial'
    emitted = b''
    for label, requested, owner, body in (
        ('self', b'ReviewKeywordChild', b'ReviewKeywordChild', b'CHILD:ReviewKeywordLeaf:7|'),
        ('parent', b'ReviewKeywordBase', b'ReviewKeywordBase', b'BASE:ReviewKeywordLeaf:7|'),
        ('static', b'ReviewKeywordLeaf', b'ReviewKeywordChild', b'CHILD:ReviewKeywordLeaf:7|'),
    ):
        before = emitted + b'METHOD|'
        checks += [
            f'S_{label}_pre_found = $enuma_seek_compiled({prior},3000)',
            rf'S_{label}_pre_found.COMPLETION = NORMAL \/ S_{label}_pre_found.COMPLETION = BUDGET',
            f'S_{label}_pre = $enumr_running(S_{label}_pre_found)',
            f'$enuma_compiled_front(S_{label}_pre)',
            f'$call_descriptors_valid(S_{label}_pre)',
            f'S_{label}_pre.ORIGIN = (porigin_{label})',
            f'S_{label}_pre.TODO = (SCOPED_NAME phpType19_{label} (KNOWN (PSTRING ptbytes_{label})) phpType7_{label}* z_{label}) :: ptask_{label}_tail*',
            f'ptbytes_{label} = ' + term(requested),
            f'$origin_child((porigin_{label}),[PCFIELD 0]) = (porigin_{label}_child)',
            f'$origin_node(S_{label}_pre.SOURCES,porigin_{label}_child) = (expression_{label})',
            f'$parser_literal(expression_{label}) = eps',
            f'$compiled_read(S_{label}_pre,porigin_{label}_child) = (PSTRING ptbytes_{label}_keyword)',
            f'ptbytes_{label}_keyword = ' + term(label.encode()),
            f'S_{label}_pre.CURRENT = (pcallcontext_{label})',
            f'pcallcontext_{label}.LEXICAL_CLASS = (porigin_{label}_lexical)',
            f'$class_at(S_{label}_pre.CLASSES,porigin_{label}_lexical) = (pclassdesc_{label}_lexical)',
            f'pclassdesc_{label}_lexical.NAME = $ptascii("ReviewKeywordChild")',
            f'pcallcontext_{label}.CALLED_CLASS = (porigin_{label}_called)',
            f'$class_at(S_{label}_pre.CLASSES,porigin_{label}_called) = (pclassdesc_{label}_called)',
            f'pclassdesc_{label}_called.NAME = $ptascii("ReviewKeywordLeaf")',
            f'$scoped_name_task(S_{label}_pre,phpType19_{label},KNOWN (PSTRING ptbytes_{label}),phpType7_{label}*,z_{label})',
            f'~$scoped_name_task(S_{label}_pre,phpType19_{label},KNOWN (PSTRING ptbytes_{label}_keyword),phpType7_{label}*,z_{label})',
            f'~$scoped_name_task(S_{label}_pre[.ORIGIN = (porigin_{label}_child)],phpType19_{label},KNOWN (PSTRING ptbytes_{label}),phpType7_{label}*,z_{label})',
            f'~$autoload_scoped_class_site(S_{label}_pre,porigin_{label},PSTRING ptbytes_{label}_keyword,z_{label})',
            f'~$autoload_scoped_selected_site(S_{label}_pre,porigin_{label},KNOWN (PSTRING ptbytes_{label}_keyword),$ptascii("body"),z_{label})',
            f'~$autoload_scoped_selected_site(S_{label}_pre,porigin_{label},KNOWN (PSTRING ptbytes_{label}),$ptascii("body"),z_{label})',
            f'$enumr_output(S_{label}_pre.EVENTS) = ' + term(before),
            f'S_{label}_zero = $drive_steps(S_{label}_pre,0)',
            f'S_{label}_zero = S_{label}_pre[.COMPLETION = BUDGET]',
            f'PhpStep: S_{label}_pre ~> S_{label}_target',
            f'S_{label}_target.COMPLETION = NORMAL',
            f'$call_descriptors_valid(S_{label}_target)',
            f'S_{label}_target.TODO = (CALL_ARGS pcalltarget_{label} phpType7_{label}* 0 eps (porigin_{label}) z_{label}) :: ptask_{label}_target*',
            f'pcalltarget_{label} = SCOPED_TARGET porigin_{label}_requested porigin_{label}_method porigin_{label}_called eps (KNOWN (PSTRING ptbytes_{label}))',
            f'$class_at(S_{label}_target.CLASSES,porigin_{label}_requested) = (pclassdesc_{label}_requested)',
            f'pclassdesc_{label}_requested.NAME = ptbytes_{label}',
            f'$target_function(S_{label}_target,pcalltarget_{label}) = (pfunction_{label})',
            f'$class_method_origin(S_{label}_target.CLASSES,porigin_{label}_method) = (pmethoddesc_{label})',
            f'pmethoddesc_{label}.FUNCTION = pfunction_{label}',
            f'pmethoddesc_{label}.NAME = $ptascii("body")',
            f'$target_lexical_class(S_{label}_target,pcalltarget_{label}) = (porigin_{label}_owner)',
            f'$class_at(S_{label}_target.CLASSES,porigin_{label}_owner) = (pclassdesc_{label}_owner)',
            f'pclassdesc_{label}_owner.NAME = ' + term(owner),
            f'$target_called_class(S_{label}_target,pcalltarget_{label}) = (porigin_{label}_called)',
            f'$target_nodes(pcalltarget_{label}) = eps',
            f'$enumr_output(S_{label}_target.EVENTS) = ' + term(before),
            f'S_{label}_one = $enumr_running($drive_steps($enumr_running(S_{label}_zero),1))',
            f'S_{label}_one.TODO = S_{label}_target.TODO',
            f'$call_descriptors_valid(S_{label}_one)',
            f'S_{label}_args_found = $enuma_seek_stage(S_{label}_target,porigin_{label},2,3000)',
            rf'S_{label}_args_found.COMPLETION = NORMAL \/ S_{label}_args_found.COMPLETION = BUDGET',
            f'S_{label}_args = $enumr_running(S_{label}_args_found)',
            f'$call_descriptors_valid(S_{label}_args)',
            f'S_{label}_args.TODO = (CALL_ARGS pcalltarget_{label} eps 1 ([KNOWN (PINT 7)]) (porigin_{label}) z_{label}) :: ptask_{label}_target*',
            f'PhpStep: S_{label}_args ~> S_{label}_entered',
            f'S_{label}_entered.COMPLETION = NORMAL',
            f'S_{label}_entered.ORIGIN =/= (porigin_{label})',
            f'S_{label}_entered.CURRENT = (pcallcontext_{label}_body)',
            f'pcallcontext_{label}_body.TARGET = pcalltarget_{label}',
            f'pcallcontext_{label}_body.CALLSITE = (porigin_{label})',
            f'pcallcontext_{label}_body.LEXICAL_CLASS = (porigin_{label}_owner)',
            f'pcallcontext_{label}_body.CALLED_CLASS = (porigin_{label}_called)',
            f'$scoped_call_selected(S_{label}_entered,pcalltarget_{label},porigin_{label})',
            f'$call_descriptors_valid(S_{label}_entered)',
            f'$enumr_output(S_{label}_entered.EVENTS) = ' + term(before + b'ARG|'),
        ]
        prior = f'S_{label}_entered'
        emitted = before + b'ARG|' + body
    return checks + [
        f'S_finish = $drive_steps({prior},5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def target_negative_assertions(main_fixture, source_path, expected_bytes, eval_responses):
    checks = folded_assertions(main_fixture, source_path, expected_bytes, eval_responses)
    checks = checks[:checks.index('S_finish = $drive_steps(S_fold_resume,5000)')]
    return checks + [
        'PhpStep: S_fold_resume ~> S_target',
        'S_target.COMPLETION = NORMAL',
        'S_target.TODO = (CALL_ARGS pcalltarget_actual eps 0 eps (porigin_fold) z_fold) :: ptask_target*',
        '$call_descriptors_valid(S_target)',
        '$class_at(S_target.CLASSES,porigin_lit_class) = (pclassdesc_wrong)',
        '$effective_method(S_target,porigin_lit_class,$ptascii("before"),|S_target.CLASSES|) = (pmethoddesc_wrong)',
        'porigin_lit_class =/= porigin_fold_class',
        'pcalltarget_wrong = SCOPED_TARGET porigin_lit_class pmethoddesc_wrong.FUNCTION.ORIGIN porigin_lit_class eps (KNOWN (PSTRING pclassdesc_wrong.NAME))',
        '$target_function(S_target,pcalltarget_wrong) = (pmethoddesc_wrong.FUNCTION)',
        '~$scoped_requested_site(S_target,porigin_fold,phpType19_fold,porigin_lit_class,eps)',
        '~$scoped_call_selected(S_target,pcalltarget_wrong,porigin_fold)',
        'S_forged = S_target[.TODO = (CALL_ARGS pcalltarget_wrong eps 0 eps (porigin_fold) z_fold) :: ptask_target*]',
        '~$call_task_valid(S_forged,CALL_ARGS pcalltarget_wrong eps 0 eps (porigin_fold) z_fold)',
        '~$call_descriptors_valid(S_forged)',
        'S_finish = $drive_steps(S_target,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]
