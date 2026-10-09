#!/usr/bin/env python3
"""Reached one-named-CV reference-call property Warning receivers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import property_reference_argument_warning_protocol as argument

reference = argument.reference
warning, sources, cross, ROOT = argument.warning, argument.sources, argument.cross, argument.ROOT
CASES = {
    'samecell': 'review-property-reference-named-argument-same-cell22',
    'quiet': 'review-property-reference-named-argument-quiet22',
    'warning': 'review-property-reference-named-argument-warning-line22',
    'default': 'review-property-reference-named-argument-default-cleanup22',
    'pending': 'review-property-reference-named-argument-pending22',
}
PREFIX = argument.PREFIX.replace('ReferenceCvPendingNew21', 'ReferenceNamedPendingNew22').replace(
    'def $undefined_warning_phase(S, n) = false -- otherwise', r'''
def $undefined_warning_phase(S, 31) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument")
def $undefined_warning_phase(S, 32) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.NAME = $ptascii("argument")
def $undefined_warning_phase(S, 34) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument")
def $undefined_warning_phase(S, 35) = true
  -- if S.CURRENT =/= eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.NAME = $ptascii("argument")
def $undefined_warning_phase(S, n) = false -- otherwise
''') + r'''
dec $named_send_test_line(pcodeexpr*, pcpath, int) : pcodeexpr*
def $named_send_test_line(eps, pcpath, z) = eps
def $named_send_test_line((CODEEXPR pcpath z_old b) :: pcodeexpr_tail*, pcpath, z) = (CODEEXPR pcpath z b) :: pcodeexpr_tail*
def $named_send_test_line(pcodeexpr :: pcodeexpr_tail*, pcpath, z) = pcodeexpr :: $named_send_test_line(pcodeexpr_tail*, pcpath, z)
  -- if $call_expr_match(pcodeexpr, pcpath) = 0
'''


def start(run, group):
    checks = reference.start(run)
    if group == 'default':
        checks = [check.replace('$ptascii("weak")) = POBJECT n_weak',
                                '$ptascii("replacement_weak")) = POBJECT n_weak') for check in checks]
        checks += ['$trace_slot(S_before, S_before.ENV, $ptascii("weak")) = POBJECT n_old_weak',
            '$weakref_get(S_before, n_old_weak) = PNULL',
            '$trace_slot(S_before, S_before.ENV, $ptascii("default_weak")) = POBJECT n_default_weak',
            '$weakref_get(S_before, n_default_weak) = PNULL',
            '$lookup(S_before.ENV, $ptascii("argument")) = eps',
            '$object_name(S_before, n_receiver) = $ptascii("ReferenceNamedDefaultNew22")',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F7|A|D|")']
    return checks + [
        'ppropertywarning.READ.SITE = PORIGIN n_unit pcpath',
        'pcpath_call = pcpath ++ [PCFIELD 0]',
        '$origin_node(S_before.SOURCES, ppropertywarning.READ.SITE) = (NExprPropertyFetch expression_receiver phpType20_name metadata_property)',
        'expression_receiver = NExprFuncCall name (SEQUENCE ([phpType7_argument])) metadata_call',
        'phpType7_argument = NArg (NIdentifier (BYTES text_parameter) metadata_parameter) expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument',
        'expression_argument = NExprVariable (BYTES text_argument) metadata_value',
        'pcpath_argument = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
        '$source_emission_echo_call(S_before, n_unit, pcpath_call, expression_receiver) = (z_init)',
        '$source_emission_cv(S_before, n_unit, pcpath_argument, expression_argument)',
        '$code_expression_at_source(S_before, PORIGIN n_unit pcpath_call, [PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (z_send)',
        'z_label = $source_line(metadata_parameter)', 'z_value = $source_line(metadata_value)',
        '$property_undefined_reference_arguments([phpType7_argument])',
        '$property_undefined_reference_name(name)',
        '$code_at(S_before.CODE, n_unit) = (pcode)', 'S_before.CODE = [pcode]',
        '$code_name(pcode.NAMES, pcpath_call) = ((ptbytes_callee, eps))',
        '$call_target(S_before, ptbytes_callee, eps) = (pfunction)',
        '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $base64(text_parameter)) = (1)',
        '$named_arg_target(pfunction, phpType7_argument, 0) = NAMED_POSITION 1',
        'pnamedargs_shape = $named_shape(pfunction.SIGNATURE.PARAMETERS, [phpType7_argument], 0, {SLOTS eps, NAMED eps})',
        'pnamedargs_shape.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]',
        'pnamedargs_shape.NAMED = eps',
        '$default_at(pfunction.DEFAULTS, 0) = (pdefault_first)',
        'pcunit = S_before.SOURCES[n_unit]',
        'P = $declaration_compiler_state($eval_source_ppstate(S_before, pcunit))',
        'P.COMPLETION = PPCNORMAL', '$compilation_image_valid(S_before, pcunit, P)',
        '$call_unit_names_valid(S_before, P)', '$send_unit_code_valid(P, pcode)',
        'perrorcall.LINE = z', 'perrorcall.SITE = ppropertywarning.READ.SITE',
        '$error_handler_file(S_invoke, perrorcall) = $call_sourcefile(S_invoke.FILES, ppropertywarning.READ.SITE)']


def line_admission():
    # The broad named helper permits differing CV/SEND lines; the complete
    # compilation image still authenticates the exact emitted descriptor.
    return [
        '$call_expr_count(pcode.EXPRESSIONS, pcpath_argument) = 1',
        'pcode_send = pcode[.EXPRESSIONS = $named_send_test_line(pcode.EXPRESSIONS, pcpath_argument, 999)]',
        '$call_expr_count(pcode_send.EXPRESSIONS, pcpath_argument) = 1',
        'S_send = S_before[.CODE = [pcode_send]]',
        '$source_emission_echo_call(S_send, n_unit, pcpath_call, expression_receiver) = (z_init)',
        '$property_undefined_reference_source(S_send, ppropertywarning.READ)',
        '~$send_unit_code_valid(P, pcode_send)', '~$call_unit_names_valid(S_send, P)',
        '~$compilation_image_valid(S_send, pcunit, P)', '~$call_descriptors_valid(S_send)',
        # This is malformed occurrence-certificate corruption, not a new AST.
        'metadata_label_bad = (MstartLine 999) :: metadata_parameter',
        'phpType7_label_bad = NArg (NIdentifier (BYTES text_parameter) metadata_label_bad) expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument',
        'expression_label_bad = NExprFuncCall name (SEQUENCE ([phpType7_label_bad])) metadata_call',
        'pcnode_label_bad = NExprPropertyFetch expression_label_bad phpType20_name metadata_property',
        'pcunit_label_bad = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_label_bad) :: (PCOCCURRENCE pcpath_call expression_label_bad) :: (PCOCCURRENCE (pcpath_call ++ [PCFIELD 1, PCINDEX 0]) phpType7_label_bad) :: (PCOCCURRENCE (pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 0]) (NIdentifier (BYTES text_parameter) metadata_label_bad)) :: pcunit.OCCURRENCES]',
        'S_label = S_before[.SOURCES[n_unit] = pcunit_label_bad]',
        '$source_emission_echo_call(S_label, n_unit, pcpath_call, expression_label_bad) = (z_init)',
        '$property_undefined_reference_source(S_label, ppropertywarning.READ)',
        '~$compilation_image_valid(S_label, pcunit_label_bad, P)',
        '~$call_descriptors_valid(S_label)']


def carrier_admission():
    checks = [
        'S_nonref = S_before[.FUNCTIONS = $reference_test_functions(S_before.FUNCTIONS, pfunction.ORIGIN)]',
        '~$property_undefined_reference_source(S_nonref, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_nonref) = eps',
        'expression_callee = NExprVariable (BYTES "Y2FsbGVlMjI=") metadata_call',
        'metadata_dynamic = (McallableExprLine z_init) :: metadata_call',
        '$callable_line(metadata_dynamic) = z_init',
        'expression_dynamic = NExprFuncCall expression_callee (SEQUENCE ([phpType7_argument])) metadata_dynamic',
        'pcnode_dynamic = NExprPropertyFetch expression_dynamic phpType20_name metadata_property',
        'pcode_dynamic = pcode[.NAMES = $reference_argument_names(pcode.NAMES, pcpath_call)][.EXPRESSIONS = (CODECALL_INIT pcpath_call z_init) :: (CODEEXPR (pcpath_call ++ [PCFIELD 0]) z_init false) :: pcode.EXPRESSIONS]',
        'S_dynamic = S_before[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_dynamic) :: (PCOCCURRENCE pcpath_call expression_dynamic) :: (PCOCCURRENCE (pcpath_call ++ [PCFIELD 0]) expression_callee) :: pcunit.OCCURRENCES]][.CODE = [pcode_dynamic]]',
        '$source_emission_echo_call(S_dynamic, n_unit, pcpath_call, expression_dynamic) = (z_init)',
        '~$property_undefined_reference_source(S_dynamic, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_dynamic) = eps',
        '$property_undefined_reference_receiver(S_dynamic)',
        '~$property_undefined_reference_arguments([phpType7_argument, phpType7_argument])',
        '~$property_undefined_reference_arguments([(NArg (NIdentifier (BYTES text_parameter) metadata_parameter) expression_argument (BOOLEAN true) (BOOLEAN false) metadata_argument)])',
        '~$property_undefined_reference_arguments([(NArg (NIdentifier (BYTES text_parameter) metadata_parameter) expression_argument (BOOLEAN false) (BOOLEAN true) metadata_argument)])',
        '~$property_undefined_reference_arguments([(NArg (NIdentifier (BYTES text_parameter) metadata_parameter) (NScalarInt (INTEGER 7) metadata_value) (BOOLEAN false) (BOOLEAN false) metadata_argument)])',
        'S_fallback_name = S_before[.CODE = [pcode[.NAMES = (CODENAME pcpath_call ptbytes_callee ($ptascii("fallback22"))) :: pcode.NAMES]]]',
        '~$property_undefined_reference_source(S_fallback_name, ppropertywarning.READ)',
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
        '$property_undefined_cell_tasks(S_saved.TODO, n_cell, ppropertywarning.READ.SITE) = 0',
        '$property_undefined_cell_tasks(S_scope.TODO, n_cell, ppropertywarning.READ.SITE) = 1',
        'S_saved_duplicate = S_saved[.FRAMES = pframe[.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: pframe.TODO] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_duplicate)',
        'S_saved_missing = S_saved[.FRAMES = pframe[.TODO = ptask_saved_tail*] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_missing)']
    for field in ('.CELL = eps', '.CELL = (|S_invoke.STORE|)', '.BORROWED = false',
                  '.FREEING = true', '.READ.LINE = 999', '.READ.NAME = $ptascii("forged22")',
                  '.KEY = $ptascii("forged22")', '.OBJECT = |S_invoke.OBJECTS|'):
        checks += [f'~$error_call_valid(S_invoke, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]])',
            f'~$call_descriptors_valid(S_saved[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]]) :: ptask_saved_tail*] :: pframe_saved_tail*])']
    return checks


def argument_warning(group):
    line, value = (26, 11) if group == 'warning' else (23, 19)
    return [*warning.seek('S_initial', 'S_argument', 31),
        'S_argument.TODO = (ERROR_HANDLER_INVOKE perrorcall_argument) :: ptask_argument_tail*',
        'perrorcall_argument.RESUME = ERROR_READ_RESULT perrorread_argument',
        f'perrorcall_argument.LINE = {line}', f'perrorread_argument.LINE = {line}',
        'perrorread_argument.RESULT = KNOWN PNULL',
        'perrorread_argument.ORIGINAL = NAMED_SEND pcalltarget_argument eps 0 pnamedargs_argument (PORIGIN n_unit_argument pcpath_call_argument) z_call_argument',
        'pnamedargs_argument = {SLOTS eps, NAMED eps}',
        '$origin_node(S_argument.SOURCES, PORIGIN n_unit_argument pcpath_call_argument) = (NExprFuncCall name_argument (SEQUENCE ([phpType7_argument_source])) metadata_call_argument)',
        'phpType7_argument_source = NArg (NIdentifier (BYTES text_parameter_argument) metadata_label_argument) (NExprVariable (BYTES text_cv_argument) metadata_cv_argument) (BOOLEAN false) (BOOLEAN false) metadata_arg_argument',
        '$target_function(S_argument, pcalltarget_argument) = (pfunction_argument)',
        '$named_arg_target(pfunction_argument, phpType7_argument_source, 0) = NAMED_POSITION 1',
        '$code_expression_at_source(S_argument, PORIGIN n_unit_argument pcpath_call_argument, [PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (perrorread_argument.LINE)',
        '$error_read_state_shape(S_argument, perrorread_argument.ORIGINAL, perrorread_argument.INPUT, perrorread_argument.BASE) = (perrorread_argument)',
        '~$error_call_valid(S_argument, perrorcall_argument[.RESUME = ERROR_READ_RESULT perrorread_argument[.LINE = 999]])',
        '~$error_call_valid(S_argument, perrorcall_argument[.RESUME = ERROR_READ_RESULT perrorread_argument[.INPUT = VARIABLE $ptascii("argument") 999]])',
        *warning.seek('S_argument', 'S_argument_saved', 35),
        'S_argument_saved.FRAMES = pframe_argument :: pframe_argument_tail*',
        'pframe_argument.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved) :: ptask_argument_saved_tail*',
        'perrorcall_argument_saved.RESUME = ERROR_READ_RESULT perrorread_argument',
        'S_argument_scope = $constant_frame_scope(S_argument_saved, pframe_argument, pframe_argument_tail*)',
        '$error_entered_call_valid(S_argument_scope, perrorcall_argument_saved)',
        '~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.TARGET = (pfunction_argument.ORIGIN)]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])',
        '~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT perrorread_argument[.LINE = 999]]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])',
        '~$call_descriptors_valid(S_argument_saved[.FRAMES = pframe_argument[.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_saved[.RESUME = ERROR_READ_RESULT perrorread_argument[.INPUT = VARIABLE $ptascii("argument") 999]]) :: ptask_argument_saved_tail*] :: pframe_argument_tail*])',
        *warning.seek('S_argument', 'S_argument_handler', 34),
        'S_argument_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_argument_entered) :: ptask_argument_handler_tail*',
        'perrorcall_argument_entered.RESUME = ERROR_READ_RESULT perrorread_argument',
        '$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered)',
        '~$error_entered_call_valid(S_argument_handler, perrorcall_argument_entered[.TARGET = (pfunction_argument.ORIGIN)])',
        f'$trace_slot(S_argument_handler, S_argument_handler.ENV, $ptascii("argument")) = PINT {value}',
        *warning.seek('S_argument_handler', 'S_argument_resume', 32),
        'S_argument_resume.TODO = (ERROR_READ_RESULT perrorread_argument) :: ptask_argument_tail*',
        *warning.step('S_argument_resume', 'S_argument_send'),
        'S_argument_send.TODO = perrorread_argument.TASK :: ptask_argument_tail*',
        'S_argument_send.RESULT = KNOWN PNULL',
        f'$trace_slot(S_argument_send, S_argument_send.ENV, $ptascii("argument")) = PINT {value}']


def after_handler(state):
    return [f'$lookup({state}.ENV, $ptascii("receiver")) = eps',
        f'$property_undefined_reference_source({state}, ppropertywarning.READ)',
        f'$property_undefined_read_valid({state}, ppropertywarning)',
        f'$heap_owners($heap_graph({state}), HCELL n_cell) = 1']


def body(run, expected, group):
    checks = start(run, group)
    if group == 'samecell':
        checks += [*reference.default_control(), *carrier_admission(),
            '$base64(text_argument) = $ptascii("receiver")',
            '$lookup(S_before.ENV, $base64(text_argument)) = (n_cell)',
            'pfunction.SIGNATURE.PARAMETERS[1].BYREF']
    if group == 'quiet':
        checks += ['$base64(text_argument) = $ptascii("missing")',
            '$lookup(S_before.ENV, $base64(text_argument)) = (n_cell)',
            'pfunction.SIGNATURE.PARAMETERS[1].BYREF',
            '$instance_test_output(S_before.EVENTS) = $ptascii("C|F3|")']
    if group in ('warning', 'pending'):
        checks += argument_warning(group) + line_admission()
        if group == 'warning':
            checks += ['z_init = 24', 'z_label = 25', 'z_value = 26', 'z_send = 26', 'z = 27',
                'pfunction.EARLY',
                '$property_undefined_named_send_line(S_argument, perrorread_argument.ORIGINAL) = eps',
                '$trace_slot(S_before, S_before.ENV, $ptascii("argument")) = PINT 11',
                '$instance_test_output(S_before.EVENTS) = $ptascii("C|H|Undefined variable $argument@26|F3/1|")']
        else:
            checks += ['z_init = 22', 'z_label = 23', 'z_value = 24', 'z_send = 23', 'z = 25',
                '~pfunction.EARLY',
                '$property_undefined_named_send_line(S_argument, perrorread_argument.ORIGINAL) = (23)',
                'perrorread_argument.INPUT = VARIABLE $ptascii("argument") 24',
                '$trace_slot(S_before, S_before.ENV, $ptascii("argument")) = PINT 19',
                '$instance_test_output(S_before.EVENTS) = $ptascii("C|H|1|Undefined variable $argument@23|F3/1|")']
    if group == 'pending':
        checks += [*warning.seek('S_invoke', 'S_handler', 10),
            'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$throwable_field(S_handler, n_error, "message") = PSTRING $ptascii("H")',
            '$throwable_previous_id(S_handler, n_error) = eps',
            '$lookup(S_handler.ENV, $ptascii("argument")) = eps',
            *after_handler('S_handler'), *reference.retired('S_handler'),
            *warning.seek('S_handler', 'S_cleanup', 21),
            'S_cleanup.CURRENT = (pcallcontext_cleanup)',
            '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
            'pdestructorcall.OBJECT = n_replacement', '(HOBJECT n_replacement) <- S_cleanup.ALLOCATIONS',
            '$destructor_call_live(S_cleanup, pdestructorcall)',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.PENDING = (n_error)',
            '~$instance_storage_freeing(S_cleanup, n_replacement)',
            '$weakref_get(S_cleanup, n_replacement_weak) = POBJECT n_replacement',
            '$throwable_field(S_cleanup, n_error, "message") = PSTRING $ptascii("H")',
            *warning.seek('S_cleanup', 'S_chained', 22),
            'S_chained.TODO = (THROW_SEARCH n_final) :: ptask_final_tail*',
            '$throwable_previous_id(S_chained, n_final) = (n_error)',
            *warning.finish('S_chained', expected), '$weakref_get(S_done, n_replacement_weak) = PNULL']
    else:
        checks += [*warning.seek('S_invoke', 'S_handler', 2),
            'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$error_entered_call_valid(S_handler, perrorcall_entered)',
            *after_handler('S_handler')]
        if group == 'samecell':
            checks += ['S_handler.STORE[n_cell] = DEFINED (PINT 17)',
                '~((HOBJECT n_receiver) <- S_handler.ALLOCATIONS)', '$weakref_get(S_handler, n_weak) = PNULL']
        else:
            checks += ['S_handler.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
                '$weakref_get(S_handler, n_weak) = POBJECT n_receiver',
                '$heap_owners($heap_graph(S_handler), HOBJECT n_receiver) = 1']
        if group == 'quiet':
            checks += ['$lookup(S_handler.ENV, $ptascii("missing")) = eps']
        if group == 'warning':
            checks += ['$trace_slot(S_handler, S_handler.ENV, $ptascii("argument")) = PINT 11']
        checks += [*warning.seek('S_handler', 'S_resume', 3),
            'S_resume.RESULT = KNOWN PNULL', 'S_resume.BASE = BASE_VALUE (KNOWN PNULL)',
            '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HCELL n_cell]',
            '$heap_owners($heap_graph(S_resume), HCELL n_cell) = 1']
        if group == 'samecell':
            # Change only the returned boolean after genuine scalar-rebind effects.
            checks += ['S_false = S_handler[.RESULT = KNOWN (PBOOL false)]', *warning.valid('S_false'),
                *warning.step('S_false', 'S_fallback'),
                'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
                *warning.seek('S_fallback', 'S_false_resume', 3),
                'S_false_resume.RESULT = KNOWN PNULL',
                '$property_undefined_read_valid(S_false_resume, ppropertywarning)',
                '$heap_owners($heap_graph(S_false_resume), HCELL n_cell) = 1',
                'S_false_resume.STORE[n_cell] = DEFINED (PINT 17)']
        checks += [*warning.step('S_resume', 'S_releasing'), *warning.finish('S_releasing', expected)]
    checks += ['~((HCELL n_cell) <- S_done.ALLOCATIONS)', '$weakref_get(S_done, n_weak) = PNULL']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-reference-named-warning-', dir=ROOT/'.tools'))
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
