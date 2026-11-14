#!/usr/bin/env python3
"""Check first by-value null initialization, exact sources, aliases and cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import literal_boolean_parentless_short_reference_get_hook_review_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('null_parentless_short_reference_get_hook_review')
PREFIX = prior.PREFIX.replace('$ptascii("box302peer")', '$ptascii("box304peer")')
PREFIX = PREFIX.replace('def $lbr_phase(S,0) = ($property_hook_ref_plan(S) =/= eps)',
                        'def $lbr_phase(S,0) = ($property_hook_plan(S) =/= eps)')
PREFIX = PREFIX.replace('$base64(text_name) = $ptascii("f302peer") \\/ $base64(text_name) = $ptascii("probe302peer")',
                        '$base64(text_name) = $ptascii("ref304peer")')
PREFIX = PREFIX.replace('def $lbr_phase(S,z) = false -- otherwise',
                        'def $lbr_phase(S,-5) = ($property_hook_ref_plan(S) =/= eps)\ndef $lbr_phase(S,z) = false -- otherwise')


def fields(fixture, source, form):
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box304peer")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("v")',
        'ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "null"]))]', '$property_hook_reference_decl(S_front,ppropertydesc)',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NIdentifier (BYTES text_type) metadata_type', '$base64(text_type) = $ptascii("null")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("null")',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}', 'pfunction.CODE.STRICT',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_expression) = 4', '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((4,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (4)',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_VALUE (DIRECT PNULL)' if form == 'initialized' else 'PROP_INITIAL'),
        '$lbr_output(S_front.EVENTS) = $ptascii("B|")',
        '$lookup(S_front.ENV,$ptascii("ref304peer")) = eps', '$lookup(S_front.ENV,$ptascii("alias304peer")) = eps',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 4) :: ptask_return*',
        '$reference_return_source(S_return,4)', '$reference_return_fetch_valid(S_return,4)', '$reference_verifies(S_return)',
        '$property_current_line(S_return) = 4', '$property_current_line($hold_task_inputs(S_return)) = 4',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,4)', '$property_current_line(S_noarrow) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"]))]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,4)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 4)',
        'S_copied = $lbr_seek(S_return,10,30000)', '$lbr_phase(S_copied,10)', 'S_copied.COMPLETION = NORMAL',
        '$lbr_output(S_copied.EVENTS) = $ptascii("B|C|")',
        '$objectprops_at(S_copied.OBJECTPROPS,n_root) = ([ppropertyslot_copied])',
        'ppropertyslot_copied.STATE = PROP_VALUE (ALIAS n_field)', 'S_copied.STORE[n_field] = DEFINED PNULL',
        '$propref_at(S_copied.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$lookup(S_copied.ENV,$ptascii("copy304peer")) = (n_copy)', 'n_copy =/= n_field',
        'S_copied.STORE[n_copy] = DEFINED PNULL', '$propref_at(S_copied.PROPREFS,n_copy) = eps',
        '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1', '$heap_owners($heap_graph(S_copied),HCELL n_copy) = 1',
        '$lookup(S_copied.ENV,$ptascii("ref304peer")) = eps', '$lookup(S_copied.ENV,$ptascii("alias304peer")) = eps',
        'S_reffront = $lbr_seek(S_copied,-5,30000)', '$lbr_phase(S_reffront,-5)',
        '$property_hook_ref_plan(S_reffront) = ((ppropertyhook_ref,"fetch"))',
        'ppropertyhook_ref.OBJECT = n_root', 'ppropertyhook_ref.PROPERTY = ppropertydesc.ORIGIN',
        'S_reffront.STORE[n_copy] = DEFINED (PBOOL false)', 'S_reffront.STORE[n_field] = DEFINED PNULL',
        'S_refreturn = $lbr_seek(S_reffront,-1,30000)', '$lbr_phase(S_refreturn,-1)',
        'S_fetch = $lbr_seek(S_refreturn,-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED PNULL',
        'S_aliases = $lbr_seek(S_fetch,14,30000)', '$lbr_phase(S_aliases,14)',
        '$lookup(S_aliases.ENV,$ptascii("ref304peer")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("alias304peer")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED PNULL', 'S_aliases.STORE[n_copy] = DEFINED (PBOOL false)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$propref_at(S_aliases.PROPREFS,n_copy) = eps',
        '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3', '$lbr_output(S_aliases.EVENTS) = $ptascii("B|C|V|")',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
        'S_before = $lbr_seek(S_aliases,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED PNULL', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
        '$lbr_output(S_before.EVENTS) = $ptascii("B|C|V|F|T|I|S|A|K|")',
        'S_detached = $lbr_seek(S_before,38,30000)', '$lbr_phase(S_detached,38)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        'S_detached.STORE[n_field] = DEFINED PNULL', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_written.STORE[n_field] = DEFINED (PINT 37)', 'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
        '~$hook_short_reference_header(NNullableType (NIdentifier (BYTES "bnVsbA==") eps) eps,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "bnVsbA==") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NIdentifier (BYTES "bnVsbA==") eps,[(PTBRANCH ([PTBUILTIN "bool"]))])',
        '$hook_short_reference_header(NNullableType (NIdentifier (BYTES "ZmFsc2U=") eps) eps,[(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    ]
    if form == 'omitted':
        checks += ['phpType5 = ABSENT']
    for strict in ('false', 'true'):
        checks += ['$propref_class(S_front,ppropertydesc.TYPE,PNULL,' + strict + ') = PROP_EXACT']
        for value in ('PBOOL false', 'PBOOL true', 'PINT 0', 'PSTRING ($ptascii("0"))', 'PARRAY 0'):
            checks += ['$propref_class(S_front,ppropertydesc.TYPE,' + value + ',' + strict + ') = PROP_IMPOSSIBLE']
    for state in ('S_return', 'S_copied', 'S_reffront', 'S_aliases', 'S_before', 'S_detached', 'S_written', 'S_end'):
        checks += ['$call_descriptors_valid(' + state + ')', '$property_state_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['initialized', 'omitted'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((SOURCES/'cases.json').read_text())
    source = SOURCES/cases[args.form]['source']
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(peer.__file__), source, SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'),
                           str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form)
        report['premises'] = len(checks)
        (out/'assertions.json').write_text(json.dumps(checks, indent=2)+'\n')
        (out/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if '+check+'\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
