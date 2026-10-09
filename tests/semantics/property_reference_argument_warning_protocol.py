#!/usr/bin/env python3
"""Reached one-positional-CV reference-call property Warning receivers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import property_reference_warning_protocol as reference

warning, sources, cross, ROOT = reference.warning, reference.sources, reference.cross, reference.ROOT
CASES = {
    'replacement': 'review-property-reference-cv-argument-replacement21',
    'parameter': 'review-property-reference-cv-argument-parameter-cleanup21',
    'pending': 'review-property-reference-cv-argument-pending21',
    'samecell': 'review-property-reference-cv-argument-same-cell21',
    'alias': 'review-property-reference-cv-argument-alias21',
}
PREFIX = reference.PREFIX.replace('ReferenceCallReplacementNew20', 'ReferenceCvReplacementNew21').replace(
    'ReferenceCallReplacementPendingNew20', 'ReferenceCvPendingNew21') + r'''
dec $reference_argument_names(pcodename*, pcpath) : pcodename*
def $reference_argument_names(eps, pcpath) = eps
def $reference_argument_names((CODENAME pcpath ptbytes_name ptbytes_fallback?) :: pcodename*, pcpath) = $reference_argument_names(pcodename*, pcpath)
def $reference_argument_names((CODENAME pcpath_other ptbytes_name ptbytes_fallback?) :: pcodename*, pcpath) = (CODENAME pcpath_other ptbytes_name ptbytes_fallback?) :: $reference_argument_names(pcodename*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def start(run, group):
    checks = reference.start(run)
    if group == 'parameter':
        checks = [check.replace('$ptascii("weak")) = POBJECT n_weak',
                                '$ptascii("replacement_weak")) = POBJECT n_weak') for check in checks]
        checks += ['$trace_slot(S_before, S_before.ENV, $ptascii("weak")) = POBJECT n_old_weak',
            '$weakref_get(S_before, n_old_weak) = PNULL',
            '$trace_slot(S_before, S_before.ENV, $ptascii("argument_weak")) = POBJECT n_argument_weak',
            '$weakref_get(S_before, n_argument_weak) = PNULL',
            '$lookup(S_before.ENV, $ptascii("argument")) = eps',
            '$object_name(S_before, n_receiver) = $ptascii("ReferenceCvParameterNew21")']
    return checks + [
        'ppropertywarning.READ.SITE = PORIGIN n_unit pcpath',
        'pcpath_call = pcpath ++ [PCFIELD 0]',
        '$origin_node(S_before.SOURCES, ppropertywarning.READ.SITE) = (NExprPropertyFetch expression_receiver phpType20_name metadata_property)',
        'expression_receiver = NExprFuncCall name (SEQUENCE ([phpType7_argument])) metadata_call',
        'phpType7_argument = NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument',
        'expression_argument = NExprVariable (BYTES text_argument) metadata_value',
        'pcpath_argument = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
        '$source_emission_echo_call(S_before, n_unit, pcpath_call, expression_receiver) = (z_init)',
        '$source_emission_cv(S_before, n_unit, pcpath_argument, expression_argument)',
        '$code_expression_at_source(S_before, PORIGIN n_unit pcpath_call, [PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (z_send)',
        '$property_undefined_reference_arguments([phpType7_argument])',
        '$property_undefined_reference_name(name)',
        'perrorcall.LINE = z', 'perrorcall.SITE = ppropertywarning.READ.SITE',
        '$error_handler_file(S_invoke, perrorcall) = $call_sourcefile(S_invoke.FILES, ppropertywarning.READ.SITE)']


def admission():
    # Both changed parent and call occurrences authenticate the new source image.
    checks = [
        '$code_at(S_before.CODE, n_unit) = (pcode)', 'S_before.CODE = [pcode]',
        '$code_name(pcode.NAMES, pcpath_call) = ((ptbytes_callee, eps))',
        '$call_target(S_before, ptbytes_callee, eps) = (pfunction)',
        'S_nonref = S_before[.FUNCTIONS = $reference_test_functions(S_before.FUNCTIONS, pfunction.ORIGIN)]',
        '~$property_undefined_reference_source(S_nonref, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_nonref) = eps',
        'pcunit = S_before.SOURCES[n_unit]',
        'expression_named = NExprFuncCall name (SEQUENCE ([(NArg (NIdentifier (BYTES "aW5wdXQ=") metadata_argument) expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument)])) metadata_call',
        'pcnode_named = NExprPropertyFetch expression_named phpType20_name metadata_property',
        'S_named = S_before[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_named) :: (PCOCCURRENCE pcpath_call expression_named) :: pcunit.OCCURRENCES]]',
        '$source_emission_echo_call(S_named, n_unit, pcpath_call, expression_named) = (z_init)',
        '$property_undefined_reference_source(S_named, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_named) = (ppropertywarning)',
        '~$property_undefined_reference_receiver(S_named)',
        'expression_callee = NExprVariable (BYTES "Y2FsbGVlMjE=") metadata_call',
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
        '~$property_undefined_reference_arguments([phpType7_argument, phpType7_argument, phpType7_argument])',
        '~$property_undefined_reference_arguments([(NArg ABSENT expression_argument (BOOLEAN true) (BOOLEAN false) metadata_argument)])',
        '~$property_undefined_reference_arguments([(NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN true) metadata_argument)])',
        '~$property_undefined_reference_arguments([(NArg ABSENT (NScalarInt (INTEGER 7) metadata_value) (BOOLEAN false) (BOOLEAN false) metadata_argument)])',
        'S_send_line = S_before[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_argument 999 false) :: pcode.EXPRESSIONS]]]',
        '~$property_undefined_reference_source(S_send_line, ppropertywarning.READ)',
        'S_send_effect = S_before[.CODE = [pcode[.EXPRESSIONS = (CODEEFFECT pcpath_argument) :: pcode.EXPRESSIONS]]]',
        '~$property_undefined_reference_source(S_send_effect, ppropertywarning.READ)',
        'S_fallback_name = S_before[.CODE = [pcode[.NAMES = (CODENAME pcpath_call ptbytes_callee ($ptascii("fallback21"))) :: pcode.NAMES]]]',
        '~$property_undefined_reference_source(S_fallback_name, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_fallback_name) = eps',
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
                  '.FREEING = true', '.READ.LINE = 999', '.READ.NAME = $ptascii("forged21")',
                  '.KEY = $ptascii("forged21")', '.OBJECT = |S_invoke.OBJECTS|'):
        checks += [f'~$error_call_valid(S_invoke, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]])',
            f'~$call_descriptors_valid(S_saved[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]]) :: ptask_saved_tail*] :: pframe_saved_tail*])']
    return checks


def after_handler(state):
    return [f'$lookup({state}.ENV, $base64(text_argument)) = eps',
        f'$property_undefined_reference_source({state}, ppropertywarning.READ)',
        f'$property_undefined_read_valid({state}, ppropertywarning)',
        f'$heap_owners($heap_graph({state}), HCELL n_cell) = 1']


def body(run, expected, group):
    checks = start(run, group)
    if group == 'replacement':
        checks += [*reference.default_control(), 'z_init = 14', 'z_send = 15', 'z = 16', *admission()]
    if group == 'samecell':
        checks += ['$base64(text_argument) = $ptascii("receiver")',
            '$lookup(S_before.ENV, $base64(text_argument)) = (n_cell)']
    if group == 'alias':
        checks += ['$lookup(S_before.ENV, $ptascii("argument_alias")) = (n_argument_cell)',
            '$lookup(S_before.ENV, $base64(text_argument)) = (n_argument_cell)',
            'n_argument_cell =/= n_cell', 'n_argument_cell <- S_before.REFCELLS',
            'S_before.STORE[n_argument_cell] = DEFINED (PINT 12)',
            '$heap_owners($heap_graph(S_before), HCELL n_argument_cell) = 2']
    if group == 'pending':
        checks += [*warning.seek('S_invoke', 'S_handler', 10),
            'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$throwable_field(S_handler, n_error, "message") = PSTRING $ptascii("H")',
            '$throwable_previous_id(S_handler, n_error) = eps',
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
            *warning.finish('S_chained', expected)]
    else:
        checks += [*warning.seek('S_invoke', 'S_handler', 2),
            'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$error_entered_call_valid(S_handler, perrorcall_entered)', *after_handler('S_handler')]
        if group == 'replacement':
            checks += reference.retired('S_handler')
        elif group == 'samecell':
            checks += ['S_handler.STORE[n_cell] = DEFINED (PINT 17)',
                '~((HOBJECT n_receiver) <- S_handler.ALLOCATIONS)',
                '$weakref_get(S_handler, n_weak) = PNULL']
        else:
            checks += ['S_handler.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
                '$weakref_get(S_handler, n_weak) = POBJECT n_receiver',
                '$heap_owners($heap_graph(S_handler), HOBJECT n_receiver) = 1']
        if group == 'alias':
            checks += ['$lookup(S_handler.ENV, $ptascii("argument_alias")) = (n_argument_cell)',
                'S_handler.STORE[n_argument_cell] = DEFINED (PINT 12)',
                '$heap_owners($heap_graph(S_handler), HCELL n_argument_cell) = 1']
        checks += [*warning.seek('S_handler', 'S_resume', 3),
            'S_resume.RESULT = KNOWN PNULL', 'S_resume.BASE = BASE_VALUE (KNOWN PNULL)',
            '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HCELL n_cell]',
            '$heap_owners($heap_graph(S_resume), HCELL n_cell) = 1']
        if group == 'replacement':
            # Only the returned boolean is changed after actual handler effects.
            checks += ['S_false = S_handler[.RESULT = KNOWN (PBOOL false)]', *warning.valid('S_false'),
                *warning.step('S_false', 'S_fallback'),
                'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
                *warning.seek('S_fallback', 'S_false_resume', 3),
                'S_false_resume.RESULT = KNOWN PNULL',
                '$property_undefined_read_valid(S_false_resume, ppropertywarning)',
                '$heap_owners($heap_graph(S_false_resume), HCELL n_cell) = 1',
                '$heap_owners($heap_graph(S_false_resume), HOBJECT n_replacement) = 1',
                '$weakref_get(S_false_resume, n_replacement_weak) = POBJECT n_replacement']
        checks += [*warning.step('S_resume', 'S_releasing'), *warning.finish('S_releasing', expected)]
    checks += ['~((HCELL n_cell) <- S_done.ALLOCATIONS)', '$weakref_get(S_done, n_weak) = PNULL']
    if group in ('replacement', 'pending'):
        checks += ['$weakref_get(S_done, n_replacement_weak) = PNULL']
    if group == 'alias':
        checks += ['(HCELL n_argument_cell) <- S_done.ALLOCATIONS',
            '$lookup(S_done.ENV, $ptascii("argument_alias")) = (n_argument_cell)',
            'S_done.STORE[n_argument_cell] = DEFINED (PINT 12)',
            '$heap_owners($heap_graph(S_done), HCELL n_argument_cell) = 1']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-reference-argument-warning-', dir=ROOT/'.tools'))
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
