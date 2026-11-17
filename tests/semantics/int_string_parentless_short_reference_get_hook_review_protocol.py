#!/usr/bin/env python3
"""Check strict union order, actual failed reads, exact tags and source removal."""
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
SOURCES = Path(__file__).with_name('int_string_parentless_short_reference_get_hook_review')
PREFIX = prior.PREFIX.replace('box302peer', 'box306peer').replace('f302peer', 'a306peer').replace('probe302peer', 'a306peer')
PREFIX = PREFIX.replace('def $lbr_phase(S,0) = ($property_hook_ref_plan(S) =/= eps)',
                        'def $lbr_phase(S,0) = ($property_hook_plan(S) =/= eps)')
PREFIX = PREFIX.replace('(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*',
                        '(PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*')


def fields(fixture, source, form):
    omitted = form == 'string-int'
    first, second = form.split('-')
    mask = '[(PTBRANCH ([PTBUILTIN "' + first + '"])),(PTBRANCH ([PTBUILTIN "' + second + '"]))]'
    reversed_mask = '[(PTBRANCH ([PTBUILTIN "' + second + '"])),(PTBRANCH ([PTBUILTIN "' + first + '"]))]'
    lines = source.read_text().splitlines()
    line = lambda statement: lines.index(statement) + 1
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box306peer")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + mask,
        'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc)', 'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second])) metadata_union',
        '$base64(text_first) = $ptascii("' + first + '")', '$base64(text_second) = $ptascii("' + second + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("string|int")',
        '~$hook_short_reference_header(phpType18,' + reversed_mask + ')', '~$hook_short_reference_header(phpType18,eps)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_mask + '])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'pfunction.CODE.STRICT', 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((7,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction) = [$at_task((PORIGIN n_source pfunction.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_INITIAL' if omitted else 'PROP_VALUE (DIRECT (PINT 0))'),
        '$lookup(S_front.ENV,$ptascii("copy306peer")) = (n_copy)', 'S_front.STORE[n_copy] = DEFINED pvalue_saved',
        '$string_bytes(pvalue_saved) = ($ptascii("saved"))',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 7) :: ptask_return*',
        '$reference_return_source(S_return,7)', '$reference_return_fetch_valid(S_return,7)', '$reference_verifies(S_return)',
        '$property_current_line(S_return) = 7', '$property_current_line($hold_task_inputs(S_return)) = 7',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reversed_mask + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,7)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 7)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,7)', '$property_current_line(S_noarrow) = 0',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_reversed = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_first) metadata_first])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reversed) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,7)',
    ]
    states = ['S_front', 'S_return']
    if omitted:
        initialize = line('$box306peer->v = 0;')
        checks += [
            'phpType5 = ABSENT',
            f'S_failed = $lbr_seek(S_return,{initialize},30000)', f'$lbr_phase(S_failed,{initialize})',
            'S_failed.COMPLETION = NORMAL', 'S_failed.CURRENT = eps', 'S_failed.FRAMES = eps',
            'S_failed.STORE[n_copy] = DEFINED pvalue_saved', 'S_failed.PROPREFS = eps',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = ([ppropertyslot_failed])', 'ppropertyslot_failed.STATE = PROP_INITIAL',
            '$lbr_output(S_failed.EVENTS) = $ptascii("U|E|P|")',
            'S_initialized = $lbr_seek(S_failed,0,30000)', '$lbr_phase(S_initialized,0)',
            '$objectprops_at(S_initialized.OBJECTPROPS,n_root) = ([ppropertyslot_initialized])',
            'ppropertyslot_initialized.STATE = PROP_VALUE (DIRECT (PINT 0))', 'S_initialized.STORE[n_copy] = DEFINED pvalue_saved',
            'S_successreturn = $lbr_seek(S_initialized,-1,30000)', '$lbr_phase(S_successreturn,-1)',
            '$reference_return_source(S_successreturn,7)', '$reference_return_fetch_valid(S_successreturn,7)', '$reference_verifies(S_successreturn)',
        ]
        states += ['S_failed', 'S_initialized', 'S_successreturn']
        success = 'S_successreturn'
    else:
        checks += ['phpType5 = NScalarInt (INTEGER 0) metadata_default']
        success = 'S_return'
    copy_line = line('$copy306peer = false;')
    aliases_line = line("$a306peer = '12';")
    checks += [
        'S_fetch = $lbr_seek(' + success + ',-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED (PINT 0)',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2',
        f'S_copied = $lbr_seek(S_fetch,{copy_line},30000)', f'$lbr_phase(S_copied,{copy_line})',
        'S_copied.STORE[n_copy] = DEFINED (PINT 0)', 'n_copy =/= n_field',
        '$propref_at(S_copied.PROPREFS,n_copy) = eps', '$propref_at(S_copied.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1',
        f'S_aliases = $lbr_seek(S_copied,{aliases_line},30000)', f'$lbr_phase(S_aliases,{aliases_line})',
        '$lookup(S_aliases.ENV,$ptascii("a306peer")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("b306peer")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED (PINT 0)', 'S_aliases.STORE[n_copy] = DEFINED (PBOOL false)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
    ]
    states += ['S_fetch', 'S_copied', 'S_aliases']
    current = 'S_aliases'
    steps = [('string', '$b306peer = 17;', 'pvalue_string'),
             ('integer', 'try { $a306peer = 2.0; } catch (\\TypeError $e) {', 'PINT 17'),
             ('float', 'try { $b306peer = true; } catch (\\TypeError $e) {', 'PINT 17'),
             ('true', 'try { $a306peer = false; } catch (\\TypeError $e) {', 'PINT 17'),
             ('false', 'try { $a306peer = null; } catch (\\TypeError $e) {', 'PINT 17'),
             ('null', 'try { $b306peer = []; } catch (\\TypeError $e) {', 'PINT 17'),
             ('array', 'try { $a306peer = new \\stdClass(); } catch (\\TypeError $e) {', 'PINT 17'),
             ('object', '$b306peer = 37;', 'PINT 17')]
    for label, statement, value in steps:
        state, n_line = 'S_' + label, line(statement)
        checks += [f'{state} = $lbr_seek({current},{n_line},30000)', f'$lbr_phase({state},{n_line})',
                   f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_field] = DEFINED ({value})',
                   f'{state}.STORE[n_copy] = DEFINED (PBOOL false)',
                   f'$propref_at({state}.PROPREFS,n_field) = (ppropref)', f'$heap_owners($heap_graph({state}),HCELL n_field) = 3']
        current = state
        states += [state]
    detach = len(lines) - 3
    checks += [
        '$string_bytes(pvalue_string) = ($ptascii("12"))', '$typed_tag(pvalue_string) = "string"',
        'S_before = $lbr_seek(S_object,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (PINT 37)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
        f'S_detached = $lbr_seek(S_before,{detach},30000)', f'$lbr_phase(S_detached,{detach})',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2', 'S_detached.STORE[n_field] = DEFINED (PINT 37)',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_written.STORE[n_field] = DEFINED (PBOOL false)', 'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
    ]
    for value in ('PINT 0', 'pvalue_string'):
        checks += ['$propref_class(S_aliases,' + mask + ',' + value + ',true) = PROP_EXACT']
    for value in ('PNULL', 'PARRAY 0', 'POBJECT n_root', 'PFLOAT 4611686018427387904', 'PBOOL false', 'PBOOL true'):
        checks += ['$propref_class(S_aliases,' + mask + ',' + value + ',true) = PROP_IMPOSSIBLE',
                   '$propref_conversion(S_aliases,' + mask + ',' + value + ',true) = TYPEREJECT']
    for left, right in [('int', 'int'), ('string', 'string'), ('array', 'int'), ('mixed', 'null')]:
        raw = 'NUnionType (SEQUENCE ([NIdentifier (BYTES ' + peer.quoted(left) + ') eps,NIdentifier (BYTES ' + peer.quoted(right) + ') eps])) eps'
        normalized = '[(PTBRANCH ([PTBUILTIN "' + left + '"])),(PTBRANCH ([PTBUILTIN "' + right + '"]))]'
        checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
    checks += ['$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps,NIdentifier (BYTES "c3RyaW5n") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))])']
    for state in [*states, 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in [('return', success), ('cleanup', 'S_before')] + ([('failed', 'S_return')] if omitted else []):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['int-string', 'string-int'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES/(args.form + '.php')
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
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT/'.tools/php-file.so'),
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
        (out/'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out/'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
