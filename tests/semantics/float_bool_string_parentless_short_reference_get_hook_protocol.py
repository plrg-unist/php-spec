#!/usr/bin/env python3
"""Check weak float/bool/string Get, shared INT widening and detached INT."""
import argparse
import base64
import json
from itertools import permutations
from pathlib import Path
import subprocess

import literal_boolean_parentless_short_reference_get_hook_review_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('float_bool_string_parentless_short_reference_get_hook')
PREFIX = prior.PREFIX.replace('box302peer', 'box315').replace('f302peer', 'a315').replace('probe302peer', 'a315')
PREFIX = PREFIX.replace('def $lbr_phase(S,0) = ($property_hook_ref_plan(S) =/= eps)',
                        'def $lbr_phase(S,0) = ($property_hook_plan(S) =/= eps)')
PREFIX = PREFIX.replace('(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*',
                        '(PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*')


def fields(fixture, source, form):
    omitted = form == 'bool-string-float'
    first, second, third = form.split('-')
    mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in (first, second, third)) + ']'
    reversed_mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in (third, second, first)) + ']'
    lines = source.read_text().splitlines()
    line = lambda statement: lines.index(statement) + 1
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box315")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + mask,
        'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc)', 'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_third) metadata_third])) metadata_union',
        '$base64(text_first) = $ptascii("' + first + '")', '$base64(text_second) = $ptascii("' + second + '")', '$base64(text_third) = $ptascii("' + third + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("string|float|bool")',
        '~$hook_short_reference_header(phpType18,' + reversed_mask + ')', '~$hook_short_reference_header(phpType18,eps)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_mask + '])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        '~pfunction.CODE.STRICT', 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((7,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction) = [$at_task((PORIGIN n_source pfunction.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_INITIAL' if omitted else 'PROP_VALUE (DIRECT (PFLOAT 0))'),
        '$lookup(S_front.ENV,$ptascii("copy315")) = (n_copy)', 'S_front.STORE[n_copy] = DEFINED pvalue_saved',
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
        'statement_reversed = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_third) metadata_third,NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_first) metadata_first])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reversed) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,7)',
    ]
    states = ['S_front', 'S_return']
    if omitted:
        initialize = line('$box315->v = 0.0;')
        checks += [
            'phpType5 = ABSENT',
            f'S_failed = $lbr_seek(S_return,{initialize},30000)', f'$lbr_phase(S_failed,{initialize})',
            'S_failed.COMPLETION = NORMAL', 'S_failed.CURRENT = eps', 'S_failed.FRAMES = eps',
            'S_failed.STORE[n_copy] = DEFINED pvalue_saved', 'S_failed.PROPREFS = eps',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = ([ppropertyslot_failed])', 'ppropertyslot_failed.STATE = PROP_INITIAL',
            '$lbr_output(S_failed.EVENTS) = $ptascii("U|E|P|")',
            'S_initialized = $lbr_seek(S_failed,0,30000)', '$lbr_phase(S_initialized,0)',
            '$objectprops_at(S_initialized.OBJECTPROPS,n_root) = ([ppropertyslot_initialized])',
            'ppropertyslot_initialized.STATE = PROP_VALUE (DIRECT (PFLOAT 0))', 'S_initialized.STORE[n_copy] = DEFINED pvalue_saved',
            'S_successreturn = $lbr_seek(S_initialized,-1,30000)', '$lbr_phase(S_successreturn,-1)',
            '$reference_return_source(S_successreturn,7)', '$reference_return_fetch_valid(S_successreturn,7)', '$reference_verifies(S_successreturn)',
        ]
        states += ['S_failed', 'S_initialized', 'S_successreturn']
        success = 'S_successreturn'
    else:
        checks += ['phpType5 = NScalarFloat (FLOAT text_default) metadata_default', '$hex_bits(text_default,0) = 0']
        success = 'S_return'
    copy_line = line('$copy315 = 17;')
    aliases_line = line('$a315 = 23;')
    checks += [
        'S_fetch = $lbr_seek(' + success + ',-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED (PFLOAT 0)',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2',
        f'S_copied = $lbr_seek(S_fetch,{copy_line},30000)', f'$lbr_phase(S_copied,{copy_line})',
        'S_copied.STORE[n_copy] = DEFINED (PFLOAT 0)', 'n_copy =/= n_field',
        '$propref_at(S_copied.PROPREFS,n_copy) = eps', '$propref_at(S_copied.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1',
        f'S_aliases = $lbr_seek(S_copied,{aliases_line},30000)', f'$lbr_phase(S_aliases,{aliases_line})',
        '$lookup(S_aliases.ENV,$ptascii("a315")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("b315")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED (PFLOAT 0)', 'S_aliases.STORE[n_copy] = DEFINED (PINT 17)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
    ]
    states += ['S_fetch', 'S_copied', 'S_aliases']
    current = 'S_aliases'
    steps = [('integer', '$b315 = true;', 'PFLOAT 4627167142146473984'),
             ('true', '$a315 = false;', 'PBOOL true'),
             ('false', '$probe_bool315 = $box315->v;', 'PBOOL false'),
             ('boolprobe', "$a315 = 'plain';", 'PBOOL false'),
             ('plaintext', '$probe_string315 = $box315->v;', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'),
             ('stringprobe', "$a315 = '12';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'),
             ('inttext', "$b315 = '12.5';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("12"))'),
             ('floattext', "$a315 = '2e0';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("12.5"))'),
             ('exponenttext', "$b315 = '';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2e0"))'),
             ('emptytext', "$a315 = '0';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii(""))'),
             ('zerotext', '$b315 = 2;', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
             ('float', 'try { $a315 = null; } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('null', 'try { $b315 = []; } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('array', 'try { $a315 = new \\stdClass(); } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('object', '$b315 = 37;', 'PFLOAT 4611686018427387904')]
    for label, statement, value in steps:
        state, n_line = 'S_' + label, line(statement)
        if label in ('boolprobe', 'stringprobe'):
            tag = 'bool' if label == 'boolprobe' else 'string'
            start = 'S_false' if label == 'boolprobe' else 'S_plaintext'
            front, returned, fetched = ('S_' + tag + suffix for suffix in ('_get_front', '_get_return', '_get_fetch'))
            hook, context = 'ppropertyhook_' + tag, 'pcallcontext_' + tag
            checks += [f'{front} = $lbr_seek({start},0,30000)', f'$lbr_phase({front},0)',
                       f'$property_hook_plan({front}) = ({hook})', f'$property_hook_ref_plan({front}) = eps',
                       f'{hook}.OBJECT = n_root', f'{hook}.HOOK = ppropertyhook.HOOK',
                       f'{front}.STORE[n_field] = DEFINED ({value})', f'$propref_at({front}.PROPREFS,n_field) = (ppropref)',
                       f'$heap_owners($heap_graph({front}),HCELL n_field) = 3',
                       f'{returned} = $lbr_seek({front},-1,30000)', f'$lbr_phase({returned},-1)',
                       f'{returned}.TODO = (RETURN_REF_FETCH 7) :: ptask_{tag}_return*', f'{returned}.CURRENT = ({context})',
                       f'{context}.TARGET = PROPERTY_HOOK_TARGET {hook}', f'{context}.FUNCTION = ppropertyhook.HOOK',
                       f'$property_hook_function({returned},{hook}) = (pfunction)',
                       f'$reference_return_source({returned},7)', f'$reference_return_fetch_valid({returned},7)',
                       f'$reference_verifies({returned})', f'$property_current_line({returned}) = 7',
                       f'{returned}.STORE[n_field] = DEFINED ({value})',
                       f'{fetched} = $lbr_seek({returned},-2,30000)', f'$lbr_phase({fetched},-2)',
                       f'{fetched}.TODO = (PROPERTY_HOOK_RESULT {hook}) :: ptask_{tag}_result*',
                       f'{fetched}.RESULT = REFERENCE n_field', f'{fetched}.STORE[n_field] = DEFINED ({value})',
                       f'$propref_at({fetched}.PROPREFS,n_field) = (ppropref)', f'$heap_owners($heap_graph({fetched}),HCELL n_field) = 4']
            states += [front, returned, fetched]
            current = fetched
        checks += [f'{state} = $lbr_seek({current},{n_line},30000)', f'$lbr_phase({state},{n_line})',
                   f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_field] = DEFINED ({value})',
                   f'{state}.STORE[n_copy] = DEFINED (PINT 17)',
                   f'$propref_at({state}.PROPREFS,n_field) = (ppropref)', f'$heap_owners($heap_graph({state}),HCELL n_field) = 3']
        current = state
        states += [state]
    checks += ['$lookup(S_boolprobe.ENV,$ptascii("probe_bool315")) = eps',
               '$lookup(S_stringprobe.ENV,$ptascii("probe_string315")) = eps',
               '$lbr_output(S_boolprobe.EVENTS) = $ptascii("' + ('U|E|P|' if omitted else 'I|') + 'V|N|J|T|F|G|")',
               '$lbr_output(S_stringprobe.EVENTS) = $ptascii("' + ('U|E|P|' if omitted else 'I|') + 'V|N|J|T|F|G|P|H|")']
    detach = len(lines) - 3
    checks += [
        'S_before = $lbr_seek(S_object,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (PFLOAT 4630404104378646528)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
        f'S_detached = $lbr_seek(S_before,{detach},30000)', f'$lbr_phase(S_detached,{detach})',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2', 'S_detached.STORE[n_field] = DEFINED (PFLOAT 4630404104378646528)',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_written.STORE[n_field] = DEFINED (PINT 2)', 'S_written.STORE[n_copy] = DEFINED (PINT 17)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
    ]
    for index in range(3):
        changed = [first, second, third]; changed[index] = 'array'
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in changed) + '])) eps'
        normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in changed) + ']'
        checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
    members_to_check = permutations(('float', 'bool', 'string')) if form == 'float-bool-string' else [(first, second, third)]
    for members in members_to_check:
        current_mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in members) + ']'
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in members) + '])) eps'
        upper = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part.upper()) + ') eps' for part in members) + '])) eps'
        reversed_raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in reversed(members)) + '])) eps'
        checks += ['$hook_short_reference_header(' + raw + ',' + current_mask + ')',
                   '$hook_short_reference_header(' + upper + ',' + current_mask + ')',
                   '~$hook_short_reference_header(' + reversed_raw + ',' + current_mask + ')']
        for value in ('PFLOAT 0', 'PFLOAT 4627167142146473984', 'PBOOL true', 'PBOOL false',
                      'PSTRING ($ptascii("plain"))', 'PSTRING ($ptascii("12"))',
                      'PSTRING ($ptascii("12.5"))', 'PSTRING ($ptascii("2e0"))',
                      'PSTRING ($ptascii(""))', 'PSTRING ($ptascii("0"))',
                      'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'):
            for strict in ('false', 'true'):
                checks += ['$propref_class(S_aliases,' + current_mask + ',' + value + ',' + strict + ') = PROP_EXACT',
                           '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',' + strict + ') = TYPEVALUE (' + value + ')']
        for strict in ('false', 'true'):
            checks += ['$propref_class(S_aliases,' + current_mask + ',PINT 2,' + strict + ') = PROP_POSSIBLE',
                       '$propref_conversion(S_aliases,' + current_mask + ',PINT 2,' + strict + ') = TYPEVALUE (PFLOAT 4611686018427387904)']
        for value in ('PNULL', 'PARRAY 0', 'POBJECT n_root'):
            classification = 'PROP_IMPOSSIBLE' if value == 'PNULL' else 'PROP_POSSIBLE'
            checks += ['$propref_class(S_aliases,' + current_mask + ',' + value + ',false) = ' + classification,
                       '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',false) = TYPEREJECT',
                       '$propref_class(S_aliases,' + current_mask + ',' + value + ',true) = PROP_IMPOSSIBLE',
                       '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',true) = TYPEREJECT']
    for members in [('float', 'float', 'string'), ('bool', 'string', 'string'), ('float', 'bool', 'null'), ('float', 'int', 'null'), ('mixed', 'bool', 'string'), ('float', 'bool', 'string', 'int')]:
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in members) + '])) eps'
        normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in members) + ']'
        checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
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
    parser.add_argument('--form', required=True, choices=['float-bool-string', 'bool-string-float', 'string-float-bool'])
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
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 360)
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
