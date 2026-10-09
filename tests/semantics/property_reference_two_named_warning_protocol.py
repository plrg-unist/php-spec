#!/usr/bin/env python3
"""Reached two-distinct-named-CV reference-call property Warning receivers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import property_reference_two_cv_warning_protocol as positional

named = positional.named
reference, warning, sources, cross, ROOT = (
    positional.reference, positional.warning, positional.sources, positional.cross, positional.ROOT)
CASES = {
    'first': 'review-property-reference-two-named-deferred-first24',
    'samecell': 'review-property-reference-two-named-same-cell24',
    'leave': 'review-property-reference-two-named-parameter-leave24',
    'priority': 'review-property-reference-two-named-unknown24',
    'pending': 'review-property-reference-two-named-pending24',
}
PREFIX = named.PREFIX.replace('ReferenceNamedPendingNew22', 'ReferenceTwoNamedPendingNew24').replace(
    '$throwable_field(S, n, "message") = PSTRING $ptascii("B")',
    '$string_bytes($throwable_field(S, n, "message")) = ($ptascii("B"))').replace(
    'def $undefined_warning_phase(S, n) = false -- otherwise', r'''
def $undefined_warning_phase(S, 70) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("second")
def $undefined_warning_phase(S, 71) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("second")
def $undefined_warning_phase(S, 72) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.NAME = $ptascii("second")
def $undefined_warning_phase(S, 73) = true
  -- if S.CURRENT =/= eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("second")
def $undefined_warning_phase(S, 74) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument_one")
def $undefined_warning_phase(S, 75) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument_one")
def $undefined_warning_phase(S, 76) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.NAME = $ptascii("argument_one")
def $undefined_warning_phase(S, 77) = true
  -- if S.CURRENT =/= eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument_one")
def $undefined_warning_phase(S, 80) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_named_shared24")
def $undefined_warning_phase(S, 81) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $target_function(S, pcallcontext.TARGET) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_named_shared24")
  -- if $lookup(S.ENV, $ptascii("first")) = (n)
  -- if $lookup(S.ENV, $ptascii("second")) = (n)
def $undefined_warning_phase(S, 82) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_named_unknown24")
def $undefined_warning_phase(S, 83) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $target_function(S, pcallcontext.TARGET) = (pfunction)
  -- if pfunction.NAME = $ptascii("invoke_two_named_unknown24")
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask*
  -- if $trace_slot(S, S.ENV, $ptascii("prefix")) = POBJECT n_prefix
  -- if $heap_owners($heap_graph(S), HOBJECT n_prefix) = 1
def $undefined_warning_phase(S, 84) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("PropertyTwoNamedUnknownArgument24")
def $undefined_warning_phase(S, 85) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("reference_two_named_leave24")
def $undefined_warning_phase(S, 88) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("property_two_named_deferred_first24")
def $undefined_warning_phase(S, n) = false -- otherwise
''')


def start(run, group):
    checks = positional.start(run, group)
    checks = [check.replace('NArg ABSENT expression_first',
        'NArg (NIdentifier (BYTES text_label_first) metadata_label_first) expression_first').replace(
        'NArg ABSENT expression_second',
        'NArg (NIdentifier (BYTES text_label_second) metadata_label_second) expression_second') for check in checks]
    return checks + ['$base64(text_label_first) = $ptascii("second")',
        '$base64(text_label_second) = $ptascii("first")',
        'z_label_first = $source_line(metadata_label_first)',
        'z_label_second = $source_line(metadata_label_second)',
        '$named_arg_target(pfunction, phpType7_first, 0) = NAMED_POSITION n_formal_first',
        '$named_arg_target(pfunction, phpType7_second, 1) = NAMED_POSITION 0']


def admission():
    checks = [*positional.image(),
        # Malformed occurrence certificate: broad capture can still classify it,
        # while the full source/compiler image rejects the changed label line.
        'metadata_label_bad = (MstartLine 999) :: metadata_label_first',
        'phpType7_label_bad = NArg (NIdentifier (BYTES text_label_first) metadata_label_bad) expression_first (BOOLEAN false) (BOOLEAN false) metadata_argument_first',
        'expression_label_bad = NExprFuncCall name (SEQUENCE ([phpType7_label_bad, phpType7_second])) metadata_call',
        'pcnode_label_bad = NExprPropertyFetch expression_label_bad phpType20_name metadata_property',
        'pcunit_label_bad = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_label_bad) :: (PCOCCURRENCE pcpath_call expression_label_bad) :: (PCOCCURRENCE (pcpath_call ++ [PCFIELD 1, PCINDEX 0]) phpType7_label_bad) :: (PCOCCURRENCE (pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 0]) (NIdentifier (BYTES text_label_first) metadata_label_bad)) :: pcunit.OCCURRENCES]',
        'S_label = S_before[.SOURCES[n_unit] = pcunit_label_bad]',
        '$property_undefined_reference_call(S_label, n_unit, pcpath_call, expression_label_bad) = (z_call)',
        '$property_undefined_reference_source(S_label, ppropertywarning.READ)',
        '~$compilation_image_valid(S_label, pcunit_label_bad, P)',
        '~$call_descriptors_valid(S_label)',
        '~$property_undefined_reference_arguments([phpType7_first, phpType7_first])',
        '~$property_undefined_reference_arguments([phpType7_first, phpType7_second, phpType7_second])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg ABSENT expression_second (BOOLEAN false) (BOOLEAN false) metadata_argument_second)])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg (NIdentifier (BYTES text_label_second) metadata_label_second) expression_second (BOOLEAN true) (BOOLEAN false) metadata_argument_second)])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg (NIdentifier (BYTES text_label_second) metadata_label_second) expression_second (BOOLEAN false) (BOOLEAN true) metadata_argument_second)])',
        '~$property_undefined_reference_arguments([phpType7_first, (NArg (NIdentifier (BYTES text_label_second) metadata_label_second) (NScalarInt (INTEGER 7) metadata_second) (BOOLEAN false) (BOOLEAN false) metadata_argument_second)])',
        # Distinct decoded parameter bytes are case-sensitive; binding priority
        # for a capitalized unknown name still belongs to named_check.
        '$property_undefined_reference_arguments([phpType7_first, (NArg (NIdentifier (BYTES "U2Vjb25k") metadata_label_second) expression_second (BOOLEAN false) (BOOLEAN false) metadata_argument_second)])',
        'S_effect = S_before[.CODE = [pcode[.EXPRESSIONS = (CODEEFFECT pcpath_second) :: pcode.EXPRESSIONS]]]',
        '~$property_undefined_reference_source(S_effect, ppropertywarning.READ)',
        'S_nonref = S_before[.FUNCTIONS = $reference_test_functions(S_before.FUNCTIONS, pfunction.ORIGIN)]',
        '~$property_undefined_reference_source(S_nonref, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_nonref) = eps',
        'S_fallback_source = S_before[.CODE = [pcode[.NAMES = (CODENAME pcpath_call ptbytes_callee ($ptascii("fallback24"))) :: pcode.NAMES]]]',
        '~$property_undefined_reference_source(S_fallback_source, ppropertywarning.READ)',
        'expression_dynamic = NExprFuncCall (NExprVariable (BYTES "Y2FsbGVlMjQ=") metadata_call) (SEQUENCE ([phpType7_first, phpType7_second])) metadata_call',
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
                  '.FREEING = true', '.READ.LINE = 999', '.READ.NAME = $ptascii("forged24")'):
        checks += [f'~$error_call_valid(S_invoke, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]])',
            f'~$call_descriptors_valid(S_saved[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]]) :: ptask_saved_tail*] :: pframe_saved_tail*])']
    return checks


def argument_warning(ordinal):
    name, line, document = ('second', 33, 34) if ordinal == 0 else ('argument_one', 23, 26)
    invoke, entered, resume, saved = (70, 71, 72, 73) if ordinal == 0 else (74, 75, 76, 77)
    slots = 'eps' if ordinal == 0 else '[NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 7))]'
    collected = '[NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]' if ordinal == 0 else '[NAMED_SENT (KNOWN PNULL), NAMED_HOLE, NAMED_SENT (KNOWN (PINT 7))]'
    checks = [*warning.seek('S_initial', 'S_argument', invoke),
        'S_argument.TODO = (ERROR_HANDLER_INVOKE perrorcall_argument) :: ptask_argument_tail*',
        'perrorcall_argument.RESUME = ERROR_READ_RESULT perrorread_argument',
        f'perrorread_argument.NAME = $ptascii("{name}")',
        f'perrorcall_argument.LINE = {line}', f'perrorread_argument.LINE = {line}',
        f'perrorread_argument.INPUT = VARIABLE $ptascii("{name}") {document}',
        'perrorread_argument.RESULT = KNOWN PNULL',
        f'perrorread_argument.ORIGINAL = NAMED_SEND pcalltarget_argument phpType7_argument_tail* {ordinal} pnamedargs_argument (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call',
        'perrorread_argument.TASK = perrorread_argument.ORIGINAL',
        f'pnamedargs_argument.SLOTS = {slots}', 'pnamedargs_argument.NAMED = eps',
        '$call_argument_source(S_argument, PORIGIN n_unit_argument pcpath_argument_call) = PCALLARGUMENTS phpType7_argument_source* n_argument_field',
        '|phpType7_argument_source*| = 2', f'phpType7_argument_tail* = phpType7_argument_source*[{ordinal+1}:{1-ordinal}]',
        f'$named_source(S_argument, (PORIGIN n_unit_argument pcpath_argument_call), {ordinal}) = phpType7_argument_source*[{ordinal}]',
        f'phpType7_argument_source*[{ordinal}] = NArg (NIdentifier (BYTES text_argument_label) metadata_argument_label) (NExprVariable (BYTES text_argument_cv) metadata_argument_cv) (BOOLEAN false) (BOOLEAN false) metadata_argument',
        f'$base64(text_argument_cv) = $ptascii("{name}")', f'$source_line(metadata_argument_cv) = {document}',
        '$target_function(S_argument, pcalltarget_argument) = (pfunction_argument)',
        f'$named_arg_target(pfunction_argument, phpType7_argument_source*[{ordinal}], {ordinal}) = NAMED_POSITION {1 if ordinal == 0 else 0}',
        f'$code_expression_at_source(S_argument, PORIGIN n_unit_argument pcpath_argument_call, [PCFIELD 1, PCINDEX {ordinal}, PCFIELD 1]) = ({line})',
        '$call_task_valid(S_argument, perrorread_argument.ORIGINAL)',
        '$error_read_state_shape(S_argument, perrorread_argument.ORIGINAL, perrorread_argument.INPUT, perrorread_argument.BASE) = (perrorread_argument)',
        f'$property_undefined_two_named_send_line(S_argument, perrorread_argument.ORIGINAL) = ({line})',
        f'$property_undefined_two_named_read_shape(S_argument, perrorread_argument.ORIGINAL, VARIABLE $ptascii("{name}") 999, perrorread_argument.BASE, {line}) = eps',
        f'$property_undefined_two_named_send_line(S_argument, NAMED_SEND pcalltarget_argument eps 2 pnamedargs_argument (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call) = eps',
        f'S_equal_line = S_argument[.CODE = [pcode[.EXPRESSIONS = $named_send_test_line(pcode.EXPRESSIONS, pcpath_argument_call ++ [PCFIELD 1, PCINDEX {ordinal}, PCFIELD 1], {document})]]]',
        '$property_undefined_two_named_send_line(S_equal_line, perrorread_argument.ORIGINAL) = eps',
        '~$error_call_valid(S_argument, perrorcall_argument[.RESUME = ERROR_READ_RESULT perrorread_argument[.LINE = 999]])',
        f'~$error_call_valid(S_argument, perrorcall_argument[.RESUME = ERROR_READ_RESULT perrorread_argument[.INPUT = VARIABLE $ptascii("{name}") 999]])',
        *warning.seek('S_argument', 'S_argument_saved', saved),
        'S_argument_saved.FRAMES = pframe_argument :: pframe_argument_tail*',
        'pframe_argument.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved) :: ptask_argument_saved_tail*',
        'perrorcall_argument_saved.RESUME = ERROR_READ_RESULT perrorread_argument',
        'S_argument_scope = $constant_frame_scope(S_argument_saved, pframe_argument, pframe_argument_tail*)',
        '$error_entered_call_valid(S_argument_scope, perrorcall_argument_saved)',
        '~$call_task_valid(S_argument, ERROR_HANDLER_INVOKE perrorcall_argument[.TARGET = (pfunction_argument.ORIGIN)])',
        '~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.TARGET = (pfunction_argument.ORIGIN)]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])']
    for field in ('.LINE = 999', f'.INPUT = VARIABLE $ptascii("{name}") 999'):
        checks += [f'~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT perrorread_argument[{field}]]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])']
    checks += ['pnamedargs_bad_shape = pnamedargs_argument[.SLOTS = [NAMED_SENT (KNOWN PNULL)]]']
    for label, task in (
        ('shape', f'NAMED_SEND pcalltarget_argument phpType7_argument_tail* {ordinal} pnamedargs_bad_shape (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call'),
        ('ordinal', f'NAMED_SEND pcalltarget_argument phpType7_argument_tail* {1-ordinal} pnamedargs_argument (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call'),
        ('tail', f'NAMED_SEND pcalltarget_argument phpType7_argument_source* {ordinal} pnamedargs_argument (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call'),
        ('target', f'NAMED_SEND (PORIGIN n_unit_argument pcpath_argument_call) phpType7_argument_tail* {ordinal} pnamedargs_argument (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call')):
        checks += [f'ptask_bad_{label} = {task}',
            f'$property_undefined_two_named_send_line(S_argument, ptask_bad_{label}) = eps',
            f'perrorread_{label} = perrorread_argument[.ORIGINAL = ptask_bad_{label}][.TASK = ptask_bad_{label}]',
            f'~$error_read_valid(S_argument, perrorread_{label})',
            f'~$error_call_valid(S_argument, perrorcall_argument[.RESUME = ERROR_READ_RESULT perrorread_{label}])',
            f'~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT perrorread_{label}]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])']
    checks += [*warning.seek('S_argument', 'S_argument_handler', entered),
        'S_argument_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_entered) :: ptask_argument_tail*',
        'perrorcall_argument_entered.RESUME = ERROR_READ_RESULT perrorread_argument',
        '$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered)',
        '~$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered[.TARGET = (pfunction_argument.ORIGIN)])',
        f'~$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered[.RESUME = ERROR_READ_RESULT perrorread_argument[.LINE = 999]])',
        f'~$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered[.RESUME = ERROR_READ_RESULT perrorread_argument[.INPUT = VARIABLE $ptascii("{name}") 999]])']
    values = (('second', 99), ('first', 17)) if ordinal == 0 else (('argument_two', 99), ('argument_one', 19))
    checks += [f'$trace_slot(S_argument_handler, S_argument_handler.ENV, $ptascii("{cv}")) = PINT {value}' for cv, value in values]
    return checks + [*warning.seek('S_argument_handler', 'S_argument_resume', resume),
        'S_argument_resume.TODO = (ERROR_READ_RESULT perrorread_argument) :: ptask_argument_tail*',
        *warning.step('S_argument_resume', 'S_argument_send'),
        'S_argument_send.TODO = perrorread_argument.TASK :: ptask_argument_tail*',
        'S_argument_send.RESULT = KNOWN PNULL',
        *warning.step('S_argument_send', 'S_argument_collected'),
        f'S_argument_collected.TODO = (NAMED_ARGS pcalltarget_argument phpType7_argument_tail* {ordinal+1} pnamedargs_collected (PORIGIN n_unit_argument pcpath_argument_call) z_argument_call) :: ptask_argument_tail*',
        f'pnamedargs_collected.SLOTS = {collected}', 'pnamedargs_collected.NAMED = eps']


def priority(run, expected):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *warning.seek('S_initial', 'S_argument', 82),
        'S_argument.TODO = (NAMED_SEND pcalltarget_argument eps 1 pnamedargs_argument (porigin_argument) z_call_argument) :: ptask_argument_tail*',
        'pnamedargs_argument.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_argument))]', 'pnamedargs_argument.NAMED = eps',
        '$trace_slot(S_argument, S_argument.ENV, $ptascii("prefix")) = POBJECT n_argument',
        '$heap_owners($heap_graph(S_argument), HOBJECT n_argument) = 2',
        '$trace_slot(S_argument, S_argument.ENV, $ptascii("argument_weak")) = POBJECT n_argument_weak',
        '$weakref_get(S_argument, n_argument_weak) = POBJECT n_argument',
        'S_global = $global_table_view(S_argument)',
        '$trace_slot(S_global, S_global.ENV, $ptascii("receiver")) = POBJECT n_receiver',
        '$trace_slot(S_global, S_global.ENV, $ptascii("weak")) = POBJECT n_weak',
        '$lookup(S_argument.ENV, $ptascii("missing")) = eps',
        '$error_read_plan(S_argument) = eps',
        *warning.seek('S_argument', 'S_unwind', 83),
        'S_unwind.TODO = (THROW_SEARCH n_error) :: ptask_unwind_tail*',
        '$throwable_field(S_unwind, n_error, "message") = PSTRING $ptascii("Unknown named parameter $unexpected")',
        '$throwable_previous_id(S_unwind, n_error) = eps',
        '$trace_slot(S_unwind, S_unwind.ENV, $ptascii("prefix")) = POBJECT n_argument',
        '$heap_owners($heap_graph(S_unwind), HOBJECT n_argument) = 1',
        '$weakref_get(S_unwind, n_argument_weak) = POBJECT n_argument',
        '$instance_test_output(S_unwind.EVENTS) = $ptascii("C|O|")',
        *warning.seek('S_unwind', 'S_cleanup', 84),
        'S_cleanup.CURRENT = (pcallcontext_cleanup)',
        '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_argument', '(HOBJECT n_argument) <- S_cleanup.ALLOCATIONS',
        '$destructor_call_live(S_cleanup, pdestructorcall)',
        'pdestructorcall.FRAME = (pdestructionframe)', 'pdestructorcall.OPERATION = eps',
        'pdestructorcall.PENDING = (n_error)', 'pdestructionframe.PENDING = (n_error)',
        '$destructor_call_pending_valid(S_cleanup, pdestructorcall)',
        '~$instance_storage_freeing(S_cleanup, n_argument)',
        '$weakref_get(S_cleanup, n_argument_weak) = POBJECT n_argument',
        *warning.seek('S_cleanup', 'S_chained', 22),
        'S_chained.TODO = (THROW_SEARCH n_final) :: ptask_final_tail*',
        '$throwable_previous_id(S_chained, n_final) = (n_error)',
        *warning.finish('S_chained', expected), '$weakref_get(S_done, n_argument_weak) = PNULL',
        '$weakref_get(S_done, n_weak) = PNULL',
        '~((HOBJECT n_argument) <- S_done.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)']


def body(run, expected, group):
    if group == 'priority':
        return priority(run, expected)
    checks = start(run, group)
    if group == 'first':
        checks += [*admission(), *argument_warning(0),
            'z_call = 32', 'z_label_first = 33', 'z_first_doc = 34',
            'z_label_second = 35', 'z_second_doc = 36', 'z_first = 33', 'z_second = 33', 'z = 37',
            '~pfunction.EARLY', 'n_formal_first = 1',
            *warning.seek('S_argument_collected', 'S_arguments_done', 88),
            'S_arguments_done.TODO = (NAMED_ARGS pfunction.ORIGIN eps 2 pnamedargs_done porigin_done? z_done) :: ptask_done_tail*',
            'pnamedargs_done.SLOTS = [NAMED_SENT (KNOWN (PINT 17)), NAMED_SENT (KNOWN PNULL)]', 'pnamedargs_done.NAMED = eps',
            '$trace_slot(S_before, S_before.ENV, $ptascii("second")) = PINT 99',
            '$trace_slot(S_before, S_before.ENV, $ptascii("first")) = PINT 17',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|A@33|1|F17/1|")']
    if group == 'samecell':
        checks += [*reference.default_control(), *admission(), 'n_formal_first = 1',
            '$base64(text_first) = $ptascii("receiver")', '$base64(text_second) = $ptascii("receiver")',
            '$lookup(S_before.ENV, $ptascii("receiver")) = (n_cell)',
            'pfunction.SIGNATURE.PARAMETERS[0].BYREF', 'pfunction.SIGNATURE.PARAMETERS[1].BYREF',
            *warning.seek('S_initial', 'S_shared_send', 80),
            'S_shared_send.TODO = (NAMED_ARGS pfunction.ORIGIN eps 2 pnamedargs_shared porigin_shared? z_shared) :: ptask_shared_tail*',
            'pnamedargs_shared.SLOTS = [NAMED_SENT (REFERENCE n_cell), NAMED_SENT (REFERENCE n_cell)]', 'pnamedargs_shared.NAMED = eps',
            'S_shared_send.STORE[n_cell] = DEFINED (POBJECT n_shared_old)',
            '$heap_owners($heap_graph(S_shared_send), HCELL n_cell) = 3',
            '$heap_owners($heap_graph(S_shared_send), HOBJECT n_shared_old) = 1',
            *warning.seek('S_shared_send', 'S_shared', 81),
            'S_shared.CURRENT = (pcallcontext_shared)', 'pcallcontext_shared.ARGC = 2',
            '$lookup(S_shared.ENV, $ptascii("first")) = (n_cell)',
            '$lookup(S_shared.ENV, $ptascii("second")) = (n_cell)',
            'S_shared.STORE[n_cell] = DEFINED (POBJECT n_shared_old)',
            '$heap_owners($heap_graph(S_shared), HCELL n_cell) = 3',
            '$heap_owners($heap_graph(S_shared), HOBJECT n_shared_old) = 1',
            '$object_name(S_before, n_receiver) = $ptascii("PropertyTwoNamedSharedNew24")',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F1|D|R1|")']
    if group == 'leave':
        checks += [*positional.image(), 'n_formal_first = 2',
            *warning.seek('S_initial', 'S_named', 85),
            'S_named.TODO = (NAMED_ARGS pfunction.ORIGIN eps 2 pnamedargs_named porigin_named? z_named) :: ptask_named_tail*',
            'pnamedargs_named.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_first_parameter)), NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_second_parameter))]', 'pnamedargs_named.NAMED = eps',
            '$trace_slot(S_named, S_named.ENV, $ptascii("argument_one")) = POBJECT n_first_parameter',
            '$trace_slot(S_named, S_named.ENV, $ptascii("argument_two")) = POBJECT n_second_parameter',
            '$lookup(S_before.ENV, $ptascii("argument_one")) = eps',
            '$lookup(S_before.ENV, $ptascii("argument_two")) = eps',
            '$object_name(S_before, n_receiver) = $ptascii("ReferenceTwoNamedLeaveFinal24")',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F|A|D|M|N1|B|NM|")']
        for weak in ('argument_one_weak', 'default_weak', 'argument_two_weak', 'first_weak', 'middle_weak'):
            checks += [f'$trace_slot(S_before, S_before.ENV, $ptascii("{weak}")) = POBJECT n_{weak}',
                f'$weakref_get(S_before, n_{weak}) = PNULL']
    if group == 'pending':
        checks += [*positional.image(), *argument_warning(1), 'n_formal_first = 2',
            'z_call = 22', 'z_label_first = 23', 'z_first_doc = 24',
            'z_label_second = 25', 'z_second_doc = 26', 'z_first = 23', 'z_second = 23', 'z = 27',
            '~pfunction.EARLY',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|H|1|Undefined variable $argument_one@23|F1/3/7|")',
            *warning.seek('S_invoke', 'S_handler', 10),
            'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$string_bytes($throwable_field(S_handler, n_error, "message")) = ($ptascii("H"))',
            '$throwable_previous_id(S_handler, n_error) = eps',
            *reference.retired('S_handler'),
            *positional.live_cleanup('S_handler', 21, 'n_replacement', 'n_replacement_weak', 'n_error'),
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
            # Constructed false boolean after genuine rebind/retirement effects.
            checks += ['S_false = S_handler[.RESULT = KNOWN (PBOOL false)]', *warning.valid('S_false'),
                *warning.step('S_false', 'S_fallback'),
                'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
                *warning.seek('S_fallback', 'S_false_resume', 3), 'S_false_resume.RESULT = KNOWN PNULL',
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
    out = Path(tempfile.mkdtemp(prefix='property-reference-two-named-warning-', dir=ROOT/'.tools'))
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
        report['failure'] = {'type':type(error).__name__, 'message':str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
