#!/usr/bin/env python3
"""Reached two-positional-CV reference-call property Warning receivers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import property_reference_named_warning_protocol as named

reference, warning, sources, cross, ROOT = (
    named.reference, named.warning, named.sources, named.cross, named.ROOT)
CASES = {
    'mutation': 'review-property-reference-two-cv-core-first-mutation23',
    'unset': 'review-property-reference-two-cv-core-second-unset23',
    'samecell': 'review-property-reference-two-cv-same-cell23',
    'leave': 'review-property-reference-two-cv-parameter-leave23',
    'sendthrow': 'review-property-reference-two-cv-send-throw23',
    'pending': 'review-property-reference-two-cv-pending23',
}
PREFIX = named.PREFIX.replace('ReferenceNamedPendingNew22', 'ReferenceTwoPendingNew23').replace(
    'def $undefined_warning_phase(S, n) = false -- otherwise', r'''
def $undefined_warning_phase(S, 40) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("first")
def $undefined_warning_phase(S, 41) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("first")
def $undefined_warning_phase(S, 42) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.NAME = $ptascii("first")
def $undefined_warning_phase(S, 44) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("second") \/ perrorread.NAME = $ptascii("argument_two")
def $undefined_warning_phase(S, 45) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("second") \/ perrorread.NAME = $ptascii("argument_two")
def $undefined_warning_phase(S, 46) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.NAME = $ptascii("second") \/ perrorread.NAME = $ptascii("argument_two")
def $undefined_warning_phase(S, 47) = true
  -- if S.CURRENT =/= eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument_two")
def $undefined_warning_phase(S, 48) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument_two")
def $undefined_warning_phase(S, 61) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("ReferenceTwoSendArgument23")
def $undefined_warning_phase(S, 62) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $target_function(S, pcallcontext.TARGET) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_cv_shared23")
  -- if $lookup(S.ENV, $ptascii("first")) = (n)
  -- if $lookup(S.ENV, $ptascii("second")) = (n)
def $undefined_warning_phase(S, 63) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 2 ([REFERENCE n, REFERENCE n]) porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_cv_shared23")
def $undefined_warning_phase(S, n) = false -- otherwise
''')


def start(run, group):
    checks = reference.start(run)
    if group in ('samecell', 'leave'):
        checks = [check.replace('$ptascii("weak")) = POBJECT n_weak',
                                '$ptascii("replacement_weak")) = POBJECT n_weak') for check in checks]
        checks += ['$trace_slot(S_before, S_before.ENV, $ptascii("weak")) = POBJECT n_old_weak',
            '$weakref_get(S_before, n_old_weak) = PNULL']
    return checks + [
        'ppropertywarning.READ.SITE = PORIGIN n_unit pcpath',
        'pcpath_call = pcpath ++ [PCFIELD 0]',
        '$origin_node(S_before.SOURCES, ppropertywarning.READ.SITE) = (NExprPropertyFetch expression_receiver phpType20_name metadata_property)',
        'expression_receiver = NExprFuncCall name (SEQUENCE ([phpType7_first, phpType7_second])) metadata_call',
        'phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_argument_first',
        'phpType7_second = NArg ABSENT expression_second (BOOLEAN false) (BOOLEAN false) metadata_argument_second',
        'expression_first = NExprVariable (BYTES text_first) metadata_first',
        'expression_second = NExprVariable (BYTES text_second) metadata_second',
        'pcpath_first = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
        'pcpath_second = pcpath_call ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1]',
        '$property_undefined_reference_call(S_before, n_unit, pcpath_call, expression_receiver) = (z_call)',
        '$source_emission_echo_call(S_before, n_unit, pcpath_call, expression_receiver) = eps',
        '$source_emission_cv(S_before, n_unit, pcpath_first, expression_first)',
        '$source_emission_cv(S_before, n_unit, pcpath_second, expression_second)',
        '$code_expression_at_source(S_before, PORIGIN n_unit pcpath_call, [PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (z_first)',
        '$code_expression_at_source(S_before, PORIGIN n_unit pcpath_call, [PCFIELD 1, PCINDEX 1, PCFIELD 1]) = (z_second)',
        'z_first_doc = $source_line(metadata_first)', 'z_second_doc = $source_line(metadata_second)',
        '$property_undefined_reference_arguments([phpType7_first, phpType7_second])',
        '$code_at(S_before.CODE, n_unit) = (pcode)', 'S_before.CODE = [pcode]',
        '$code_name(pcode.NAMES, pcpath_call) = ((ptbytes_callee, eps))',
        '$call_target(S_before, ptbytes_callee, eps) = (pfunction)',
        'perrorcall.LINE = z', 'perrorcall.SITE = ppropertywarning.READ.SITE',
        '$error_handler_file(S_invoke, perrorcall) = $call_sourcefile(S_invoke.FILES, ppropertywarning.READ.SITE)']


def image():
    # The local certificate does not invent a universal SEND==CV line rule.
    # Replace exactly one CODEEXPR; the full compiler image rejects its value.
    checks = ['pcunit = S_before.SOURCES[n_unit]',
        'P = $declaration_compiler_state($eval_source_ppstate(S_before, pcunit))',
        'P.COMPLETION = PPCNORMAL', '$compilation_image_valid(S_before, pcunit, P)',
        '$call_unit_names_valid(S_before, P)', '$send_unit_code_valid(P, pcode)']
    for child in ('first', 'second'):
        checks += [f'$call_expr_count(pcode.EXPRESSIONS, pcpath_{child}) = 1',
            f'pcode_send_{child} = pcode[.EXPRESSIONS = $named_send_test_line(pcode.EXPRESSIONS, pcpath_{child}, 999)]',
            f'$call_expr_count(pcode_send_{child}.EXPRESSIONS, pcpath_{child}) = 1',
            f'S_send_{child} = S_before[.CODE = [pcode_send_{child}]]',
            f'$property_undefined_reference_call(S_send_{child}, n_unit, pcpath_call, expression_receiver) = (z_call)',
            f'$property_undefined_reference_source(S_send_{child}, ppropertywarning.READ)',
            f'~$send_unit_code_valid(P, pcode_send_{child})', f'~$call_unit_names_valid(S_send_{child}, P)',
            f'~$compilation_image_valid(S_send_{child}, pcunit, P)', f'~$call_descriptors_valid(S_send_{child})']
    return checks


def admission():
    checks = [*image(),
        '~$property_undefined_reference_arguments([phpType7_first, phpType7_second, phpType7_second])',
        '~$property_undefined_reference_arguments([(NArg (NIdentifier (BYTES "aW5wdXQ=") metadata_argument_first) expression_first (BOOLEAN false) (BOOLEAN false) metadata_argument_first), phpType7_second])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg ABSENT expression_second (BOOLEAN true) (BOOLEAN false) metadata_argument_second)])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg ABSENT expression_second (BOOLEAN false) (BOOLEAN true) metadata_argument_second)])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg ABSENT (NScalarInt (INTEGER 7) metadata_second) (BOOLEAN false) (BOOLEAN false) metadata_argument_second)])',
        'S_effect = S_before[.CODE = [pcode[.EXPRESSIONS = (CODEEFFECT pcpath_second) :: pcode.EXPRESSIONS]]]',
        '~$property_undefined_reference_source(S_effect, ppropertywarning.READ)',
        'S_nonref = S_before[.FUNCTIONS = $reference_test_functions(S_before.FUNCTIONS, pfunction.ORIGIN)]',
        '~$property_undefined_reference_source(S_nonref, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_nonref) = eps',
        'S_fallback = S_before[.CODE = [pcode[.NAMES = (CODENAME pcpath_call ptbytes_callee ($ptascii("fallback23"))) :: pcode.NAMES]]]',
        '~$property_undefined_reference_source(S_fallback, ppropertywarning.READ)',
        # Update both parent/receiver occurrences: this is the excluded dynamic
        # two-CV shape, not merely a parent with a stale receiver occurrence.
        'expression_dynamic = NExprFuncCall (NExprVariable (BYTES "Y2FsbGVlMjM=") metadata_call) (SEQUENCE ([phpType7_first, phpType7_second])) metadata_call',
        'pcnode_dynamic = NExprPropertyFetch expression_dynamic phpType20_name metadata_property',
        'S_dynamic = S_before[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_dynamic) :: (PCOCCURRENCE pcpath_call expression_dynamic) :: pcunit.OCCURRENCES]]',
        '$property_undefined_reference_call(S_dynamic, n_unit, pcpath_call, expression_dynamic) = eps',
        '~$property_undefined_reference_source(S_dynamic, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_dynamic) = eps',
        '$property_undefined_reference_receiver(S_dynamic)',
        'S_duplicate = S_invoke[.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: S_invoke.TODO]',
        '$property_undefined_cell_tasks(S_duplicate.TODO, n_cell, ppropertywarning.READ.SITE) = 2',
        '~$call_descriptors_valid(S_duplicate)',
        '$lookup(S_invoke.ENV, $ptascii("weak")) = (n_wrong)',
        'S_wrong = $reference_cell(S_invoke, n_wrong)', '$property_undefined_cell(S_wrong, n_wrong)',
        '~$error_call_valid(S_wrong, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[.CELL = (n_wrong)]])',
        'S_no_cell = S_invoke[.REFCELLS = eps]', '~$call_descriptors_valid(S_no_cell)',
        *warning.seek('S_invoke', 'S_saved', 4),
        'S_saved.FRAMES = pframe :: pframe_saved_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_saved) :: ptask_saved_tail*',
        'perrorcall_saved.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        'S_scope = $constant_frame_scope(S_saved, pframe, pframe_saved_tail*)',
        '$error_entered_call_valid(S_scope, perrorcall_saved)',
        'S_saved_duplicate = S_saved[.FRAMES = pframe[.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: pframe.TODO] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_duplicate)',
        'S_saved_missing = S_saved[.FRAMES = pframe[.TODO = ptask_saved_tail*] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_missing)']
    for field in ('.CELL = eps', '.CELL = (|S_invoke.STORE|)', '.BORROWED = false',
                  '.FREEING = true', '.READ.LINE = 999', '.READ.NAME = $ptascii("forged23")'):
        checks += [f'~$error_call_valid(S_invoke, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]])',
            f'~$call_descriptors_valid(S_saved[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]]) :: ptask_saved_tail*] :: pframe_saved_tail*])']
    return checks


def argument_warning(parent, tag, name, ordinal, line, document, prefix, mutations, negatives=False):
    prefix_term = '('+prefix+')' if prefix.startswith('[') else prefix
    before, handler, resume, send = ('S_'+tag+suffix for suffix in ('', '_handler', '_resume', '_send'))
    call, read, target, path, unit, tail = ('perrorcall_'+tag, 'perrorread_'+tag, 'pcalltarget_'+tag,
                                         'pcpath_argument_'+tag, 'n_unit_argument_'+tag, 'ptask_'+tag+'_tail*')
    invoke_phase, handler_phase, resume_phase = (40, 41, 42) if ordinal == 0 else (44, 45, 46)
    checks = [*warning.seek(parent, before, invoke_phase),
        f'{before}.TODO = (ERROR_HANDLER_INVOKE {call}) :: {tail}',
        f'{call}.RESUME = ERROR_READ_RESULT {read}', f'{read}.NAME = $ptascii("{name}")',
        f'{call}.LINE = {line}', f'{read}.LINE = {line}',
        f'{read}.INPUT = VARIABLE $ptascii("{name}") {document}',
        f'{read}.RESULT = KNOWN PNULL',
        f'{read}.ORIGINAL = CALL_SEND {target} phpType7_{tag}_tail* {ordinal} {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}',
        f'{read}.TASK = {read}.ORIGINAL',
        f'$call_task_valid({before}, {read}.ORIGINAL)',
        f'$error_read_state_shape({before}, {read}.ORIGINAL, {read}.INPUT, {read}.BASE) = ({read})',
        f'$call_send_line({before}, (PORIGIN {unit} {path}), {ordinal}) = {line}']
    if ordinal == 0 or line == document:
        checks += [f'$property_undefined_positional_send_line({before}, {read}.ORIGINAL) = eps']
    if negatives:
        checks += [f'phpType7_{tag}_tail* = eps',
            f'$property_undefined_positional_send_line({before}, {read}.ORIGINAL) = (23)',
            f'$property_undefined_positional_read_shape({before}, {read}.ORIGINAL, VARIABLE $ptascii("{name}") 999, {read}.BASE, 23) = eps',
            f'$property_undefined_positional_send_line({before}, CALL_SEND {target} eps 0 {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}) = eps',
            f'$property_undefined_positional_send_line({before}, CALL_SEND {target} eps 1 eps (PORIGIN {unit} {path}) z_argument_{tag}) = eps',
            f'$call_argument_source({before}, PORIGIN {unit} {path}) = PCALLARGUMENTS phpType7_{tag}_source* n_{tag}_field',
            f'$property_undefined_positional_send_line({before}, CALL_SEND {target} phpType7_{tag}_source* 1 {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}) = eps',
            f'~$error_call_valid({before}, {call}[.RESUME = ERROR_READ_RESULT {read}[.LINE = 999]])',
            f'~$error_call_valid({before}, {call}[.RESUME = ERROR_READ_RESULT {read}[.INPUT = VARIABLE $ptascii("{name}") 999]])',
            *warning.seek(before, 'S_argument_saved', 47),
            'S_argument_saved.FRAMES = pframe_argument :: pframe_argument_tail*',
            'pframe_argument.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved) :: ptask_argument_saved_tail*',
            f'perrorcall_argument_saved.RESUME = ERROR_READ_RESULT {read}',
            'S_argument_scope = $constant_frame_scope(S_argument_saved, pframe_argument, pframe_argument_tail*)',
            '$error_entered_call_valid(S_argument_scope, perrorcall_argument_saved)',
            f'$target_function({before}, {target}) = (pfunction_argument)',
            f'~$call_task_valid({before}, ERROR_HANDLER_INVOKE {call}[.TARGET = (pfunction_argument.ORIGIN)])',
            '~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.TARGET = (pfunction_argument.ORIGIN)]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])',
            f'~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT {read}[.LINE = 999]]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])',
            f'~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT {read}[.INPUT = VARIABLE $ptascii("{name}") 999]]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])']
        for label, task in (
            ('count', f'CALL_SEND {target} eps 1 eps (PORIGIN {unit} {path}) z_argument_{tag}'),
            ('ordinal', f'CALL_SEND {target} eps 0 {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}'),
            ('tail', f'CALL_SEND {target} phpType7_{tag}_source* 1 {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}'),
            ('target', f'CALL_SEND (PORIGIN {unit} {path}) eps 1 {prefix_term} (PORIGIN {unit} {path}) z_argument_{tag}')):
            checks += [f'ptask_bad_{label} = {task}',
                f'perrorread_{label} = {read}[.ORIGINAL = ptask_bad_{label}][.TASK = ptask_bad_{label}]',
                f'~$error_read_valid({before}, perrorread_{label})',
                f'~$error_call_valid({before}, {call}[.RESUME = ERROR_READ_RESULT perrorread_{label}])',
                f'~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT perrorread_{label}]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])']
    checks += [*warning.seek(before, handler, handler_phase),
        f'{handler}.TODO = (ERROR_HANDLER_RESULT perrorcall_{tag}_entered) :: {tail}',
        f'perrorcall_{tag}_entered.RESUME = ERROR_READ_RESULT {read}',
        f'$error_entered_call_valid({handler}, perrorcall_{tag}_entered)',
        *([f'~$error_entered_call_valid({handler}, perrorcall_{tag}_entered[.TARGET = (pfunction_argument.ORIGIN)])'] if negatives else []),
        *[clause.replace('STATE', handler) for clause in mutations],
        *warning.seek(handler, resume, resume_phase),
        f'{resume}.TODO = (ERROR_READ_RESULT {read}) :: {tail}',
        *warning.step(resume, send),
        f'{send}.TODO = {read}.TASK :: {tail}', f'{send}.RESULT = KNOWN PNULL',
        *warning.step(send, send+'_collected'),
        f'{send}_collected.TODO = (CALL_ARGS {target} phpType7_{tag}_tail* {ordinal+1} ({prefix} ++ [KNOWN PNULL]) (PORIGIN {unit} {path}) z_argument_{tag}) :: {tail}']
    return checks


def live_cleanup(parent, phase, target, weak, pending):
    return [*warning.seek(parent, 'S_cleanup', phase),
        'S_cleanup.CURRENT = (pcallcontext_cleanup)',
        '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
        f'pdestructorcall.OBJECT = {target}', f'(HOBJECT {target}) <- S_cleanup.ALLOCATIONS',
        '$destructor_call_live(S_cleanup, pdestructorcall)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        f'pdestructionoperation.PENDING = ({pending})',
        f'~$instance_storage_freeing(S_cleanup, {target})',
        f'$weakref_get(S_cleanup, {weak}) = POBJECT {target}',
        *warning.seek('S_cleanup', 'S_chained', 22),
        'S_chained.TODO = (THROW_SEARCH n_final) :: ptask_final_tail*',
        f'$throwable_previous_id(S_chained, n_final) = ({pending})']


def send_throw(run, expected):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *warning.seek('S_initial', 'S_argument', 44),
        'S_argument.TODO = (ERROR_HANDLER_INVOKE perrorcall_argument) :: ptask_argument_tail*',
        'perrorcall_argument.RESUME = ERROR_READ_RESULT perrorread_argument',
        'perrorread_argument.ORIGINAL = CALL_SEND pcalltarget_argument eps 1 ([KNOWN (POBJECT n_argument)]) (porigin_argument) z_call_argument',
        'perrorread_argument.TASK = perrorread_argument.ORIGINAL',
        'perrorread_argument.INPUT = VARIABLE $ptascii("argument_two") 20',
        'perrorread_argument.LINE = 20', '$task_nodes(ERROR_READ_RESULT perrorread_argument) = [HOBJECT n_argument]',
        '$heap_owners($heap_graph(S_argument), HOBJECT n_argument) = 2',
        '$trace_slot(S_argument, S_argument.ENV, $ptascii("argument_one_weak")) = POBJECT n_argument_weak',
        '$weakref_get(S_argument, n_argument_weak) = POBJECT n_argument',
        '$trace_slot(S_argument, S_argument.ENV, $ptascii("receiver")) = POBJECT n_receiver',
        '$trace_slot(S_argument, S_argument.ENV, $ptascii("weak")) = POBJECT n_weak',
        '$heap_owners($heap_graph(S_argument), HOBJECT n_receiver) = 1',
        *warning.seek('S_argument', 'S_handler', 48),
        'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_handler_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread_argument',
        '$error_entered_call_valid(S_handler, perrorcall_entered)',
        '$throwable_field(S_handler, n_error, "message") = PSTRING $ptascii("H")',
        '$throwable_previous_id(S_handler, n_error) = eps',
        '$lookup(S_handler.ENV, $ptascii("argument_one")) = eps',
        '$heap_owners($heap_graph(S_handler), HOBJECT n_argument) = 1',
        '$weakref_get(S_handler, n_argument_weak) = POBJECT n_argument',
        '$weakref_get(S_handler, n_weak) = POBJECT n_receiver',
        *live_cleanup('S_handler', 61, 'n_argument', 'n_argument_weak', 'n_error'),
        *warning.finish('S_chained', expected),
        '$weakref_get(S_done, n_argument_weak) = PNULL', '$weakref_get(S_done, n_weak) = PNULL',
        '~((HOBJECT n_argument) <- S_done.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)']


def body(run, expected, group):
    if group == 'sendthrow':
        return send_throw(run, expected)
    checks = start(run, group)
    if group == 'mutation':
        checks += [*admission(), 'z_call = 30', 'z_first = 31', 'z_second = 32', 'z = 33',
            *argument_warning('S_initial', 'first', 'first', 0, 31, 31, 'eps', [
                '$trace_slot(STATE, STATE.ENV, $ptascii("first")) = PINT 99',
                '$trace_slot(STATE, STATE.ENV, $ptascii("second")) = PINT 17']),
            '$trace_slot(S_before, S_before.ENV, $ptascii("first")) = PINT 99',
            '$trace_slot(S_before, S_before.ENV, $ptascii("second")) = PINT 17',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|A@31|F1/17|")']
    if group == 'unset':
        checks += [*argument_warning('S_initial', 'first', 'first', 0, 40, 40, 'eps', [
                '$lookup(STATE.ENV, $ptascii("second")) = eps',
                '$trace_slot(STATE, STATE.ENV, $ptascii("argument_weak")) = POBJECT n_argument_weak',
                '$weakref_get(STATE, n_argument_weak) = PNULL']),
            *argument_warning('S_first_send_collected', 'second', 'second', 1, 41, 41, '[KNOWN PNULL]', [
                '$trace_slot(STATE, STATE.ENV, $ptascii("second")) = PINT 19',
                '$weakref_get(STATE, n_argument_weak) = PNULL']),
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|A1@40|Q|A2@41|1|F1/1|")']
    if group == 'samecell':
        checks += [*reference.default_control(),
            '$base64(text_first) = $ptascii("receiver")', '$base64(text_second) = $ptascii("receiver")',
            '$lookup(S_before.ENV, $ptascii("receiver")) = (n_cell)',
            'pfunction.SIGNATURE.PARAMETERS[0].BYREF', 'pfunction.SIGNATURE.PARAMETERS[1].BYREF',
            *warning.seek('S_initial', 'S_shared_send', 63),
            'S_shared_send.TODO = (CALL_ARGS pfunction.ORIGIN eps 2 ([REFERENCE n_cell, REFERENCE n_cell]) porigin_shared? z_shared) :: ptask_shared_tail*',
            'S_shared_send.STORE[n_cell] = DEFINED (POBJECT n_shared_old)',
            '$heap_owners($heap_graph(S_shared_send), HCELL n_cell) = 3',
            '$heap_owners($heap_graph(S_shared_send), HOBJECT n_shared_old) = 1',
            *warning.seek('S_shared_send', 'S_shared', 62),
            'S_shared.CURRENT = (pcallcontext_shared)',
            'pcallcontext_shared.ARGC = 2',
            '$lookup(S_shared.ENV, $ptascii("first")) = (n_cell)',
            '$lookup(S_shared.ENV, $ptascii("second")) = (n_cell)',
            'S_shared.STORE[n_cell] = DEFINED (POBJECT n_shared_old)',
            '$heap_owners($heap_graph(S_shared), HCELL n_cell) = 3',
            '$heap_owners($heap_graph(S_shared), HOBJECT n_shared_old) = 1',
            '$object_name(S_before, n_receiver) = $ptascii("PropertyTwoCvSharedNew23")',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F1|D|R1|")']
    if group == 'leave':
        checks += ['$lookup(S_before.ENV, $ptascii("argument_one")) = eps',
            '$lookup(S_before.ENV, $ptascii("argument_two")) = eps',
            '$object_name(S_before, n_receiver) = $ptascii("ReferenceTwoLeaveFinal23")',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F|A|D|B|N1|")']
        for weak in ('argument_one_weak', 'argument_two_weak', 'first_weak'):
            checks += [f'$trace_slot(S_before, S_before.ENV, $ptascii("{weak}")) = POBJECT n_{weak}',
                f'$weakref_get(S_before, n_{weak}) = PNULL']
    if group == 'pending':
        checks += [*image(), 'z_call = 22', 'z_first = 23', 'z_second = 23',
            'z_first_doc = 23', 'z_second_doc = 24', 'z = 25', '~pfunction.EARLY',
            *argument_warning('S_initial', 'second', 'argument_two', 1, 23, 24, '[KNOWN (PINT 7)]', [
                '$trace_slot(STATE, STATE.ENV, $ptascii("argument_one")) = PINT 99',
                '$trace_slot(STATE, STATE.ENV, $ptascii("argument_two")) = PINT 19'], negatives=True),
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|H|1|Undefined variable $argument_two@23|F7/1|")',
            *warning.seek('S_invoke', 'S_handler', 10),
            'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$throwable_field(S_handler, n_error, "message") = PSTRING $ptascii("H")',
            '$throwable_previous_id(S_handler, n_error) = eps',
            *reference.retired('S_handler'),
            *live_cleanup('S_handler', 21, 'n_replacement', 'n_replacement_weak', 'n_error'),
            *warning.finish('S_chained', expected), '$weakref_get(S_done, n_replacement_weak) = PNULL']
    else:
        checks += [*warning.seek('S_invoke', 'S_handler', 2),
            'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$error_entered_call_valid(S_handler, perrorcall_entered)',
            '$lookup(S_handler.ENV, $ptascii("receiver")) = eps',
            '$property_undefined_reference_source(S_handler, ppropertywarning.READ)',
            '$property_undefined_read_valid(S_handler, ppropertywarning)',
            '$heap_owners($heap_graph(S_handler), HCELL n_cell) = 1']
        if group == 'samecell':
            checks += ['S_handler.STORE[n_cell] = DEFINED (PINT 17)',
                '~((HOBJECT n_receiver) <- S_handler.ALLOCATIONS)', '$weakref_get(S_handler, n_weak) = PNULL']
        else:
            checks += ['S_handler.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
                '$weakref_get(S_handler, n_weak) = POBJECT n_receiver',
                '$heap_owners($heap_graph(S_handler), HOBJECT n_receiver) = 1']
        checks += [*warning.seek('S_handler', 'S_resume', 3),
            'S_resume.RESULT = KNOWN PNULL', 'S_resume.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph(S_resume), HCELL n_cell) = 1']
        if group == 'samecell':
            # Only the bool changes after genuine same-cell rebind/retirement.
            checks += ['S_false = S_handler[.RESULT = KNOWN (PBOOL false)]', *warning.valid('S_false'),
                *warning.step('S_false', 'S_fallback'),
                'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
                *warning.seek('S_fallback', 'S_false_resume', 3),
                'S_false_resume.RESULT = KNOWN PNULL',
                '$property_undefined_read_valid(S_false_resume, ppropertywarning)',
                '$heap_owners($heap_graph(S_false_resume), HCELL n_cell) = 1',
                'S_false_resume.STORE[n_cell] = DEFINED (PINT 17)']
        checks += [*warning.step('S_resume', 'S_releasing'), *warning.finish('S_releasing', expected)]
    return checks + ['~((HCELL n_cell) <- S_done.ALLOCATIONS)', '$weakref_get(S_done, n_weak) = PNULL']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-reference-two-cv-warning-', dir=ROOT/'.tools'))
    report = {'before':before, 'profile':cross.invoke.types.PROFILE, 'passed':False,
        'native_evaluations':0, 'model_evaluations':0, 'state_assertions_evaluated':0,
        'runner_mode':'SL', 'numeric_cap_seconds':120, 'case':CASES[args.group], 'jobs':1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
