#!/usr/bin/env python3
"""Check bounded scalar union headers, exact reference tags and quiet detach."""
import argparse
import base64
import json
from itertools import permutations
from pathlib import Path
import subprocess
import sys

import int_bool_null_parentless_short_reference_get_hook_protocol as prior
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
STEM = 'scalar_union_parentless_short_reference_get_hook'
PREFIX = prior.PREFIX_BASE.replace('box302peer', 'box319').replace('f302peer', 'a319').replace('probe302peer', 'b319')
PROMOTED = {
    'bool_string': [('string', 'bool', 'null')],
    'float_bool': [('float', 'bool', 'null')],
    'float_bool_string': [('float', 'bool', 'null')],
    'float_string': [('float', 'string', 'null')],
    'int_float_bool_string': [('int', 'float', 'bool', 'null'), ('int', 'float', 'bool', 'string', 'null')],
    'int_float_null': [('int', 'float', 'string', 'null')],
    'int_string': [('int', 'null', 'string')],
}


def mask(members):
    return '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in members) + ']'


def raw(members):
    return 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + prior.peer.quoted(part) + ') eps' for part in members) + '])) eps'


def header_fields():
    checks = []
    for length in (3, 4, 5):
        for members in permutations(('int', 'float', 'bool', 'string', 'null'), length):
            checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')',
                       '$hook_short_reference_header(' + raw([part.upper() for part in members]) + ',' + mask(members) + ')',
                       '~$hook_short_reference_header(' + raw(list(reversed(members))) + ',' + mask(members) + ')',
                       '~$hook_short_reference_header(' + raw(members) + ',' + mask(list(reversed(members))) + ')']
        members = ['int', 'float', 'bool', 'string', 'null'][:length]
        duplicate = members[:-1] + [members[0]]
        casealias = members[:-1] + [members[0].upper()]
        checks += ['~$hook_short_reference_header(' + raw(duplicate) + ',' + mask(duplicate) + ')',
                   '~$hook_short_reference_header(' + raw(casealias) + ',' + mask(duplicate) + ')',
                   '~$hook_short_reference_header(' + raw(members) + ',' + mask(members[:-1]) + ')',
                   '~$hook_short_reference_header(' + raw(members) + ',' + mask(members + ['int']) + ')']
    for kind in ('mixed', 'array', 'object', 'callable', 'true', 'false', 'void', 'integer'):
        members = ['int', kind, 'null']
        checks += [('' if kind in ('array', 'object') else '~') + '$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    for members in ([], ['int'], ['int', 'float', 'bool', 'string', 'null', 'int']):
        checks += ['~$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    ordinary = raw(['int', 'float', 'null'])
    for forged in (ordinary.replace('NIdentifier', 'NName', 1),
                   ordinary.replace('NIdentifier (BYTES "aW50") eps', 'NNameFullyQualified (BYTES "aW50") eps'),
                   ordinary.replace('NIdentifier (BYTES "aW50") eps', 'NIntersectionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps])) eps')):
        checks += ['~$hook_short_reference_header(' + forged + ',' + mask(['int', 'float', 'null']) + ')']
    for branches in ('eps', '[(PTBRANCH ([PTBUILTIN "int",PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "null"]))]',
                     '[(PTBRANCH ([PTCLASS ($ptascii("int"))])),(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "null"]))]',
                     mask(['INT', 'float', 'null'])):
        checks += ['~$hook_short_reference_header(' + ordinary + ',' + branches + ')']
    for members in (['int', 'float'], ['array', 'null'], ['null', 'object'], ['false', 'null']):
        checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    checks += ['$hook_short_reference_header(' + raw(['array', 'int']) + ',' + mask(['array', 'int']) + ')']
    # Exact assertions promoted in the affected older protocol tails.
    for family, orders in PROMOTED.items():
        for review in (False, True):
            for members in orders:
                if family == 'int_string' and review:
                    members = ('int', 'string', 'null')
                checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    for members in (('int', 'bool', 'string', 'null'), ('int', 'null', 'string')):
        checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    return checks


def fields(fixture, source, case):
    members = case['members']; branches = mask(members); reverse = mask(list(reversed(members)))
    lines = source.read_text().splitlines()
    line = lambda statement: [text.strip() for text in lines].index(statement) + 1
    raw_members = ','.join('NIdentifier (BYTES text_member_' + str(i) + ') metadata_member_' + str(i) for i in range(len(members)))
    canonical = '|'.join(part for part in ('string', 'int', 'float', 'bool', 'null') if part in members)
    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + prior.peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box319")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + branches,
        'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc)', 'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([' + raw_members + '])) metadata_union',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("' + canonical + '")',
        '~$hook_short_reference_header(phpType18,' + reverse + ')',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reverse + '])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        ('pfunction.CODE.STRICT' if case['strict'] else '~pfunction.CODE.STRICT'),
        'pfunction.DEFAULTS = eps', '~pfunction.EARLY', 'pfunction.CODE.UNIT = n_source',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (' + ('NScalarString' if case['strict'] else 'NIdentifier') + ' (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((7,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction) = [$at_task((PORIGIN n_source pfunction.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot])',
        'ppropertyslot.STATE = ' + ('PROP_INITIAL' if case['default'] == 'omitted' else 'PROP_VALUE (DIRECT (' + case['initial'] + '))'),
        '$lookup(S_front.ENV,$ptascii("copy319")) = (n_copy)',
        'S_front.STORE[n_copy] = DEFINED pvalue_saved', '$string_bytes(pvalue_saved) = ($ptascii("saved"))',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        '$reference_return_source(S_return,7)', '$reference_return_fetch_valid(S_return,7)', '$reference_verifies(S_return)',
        '$property_current_line(S_return) = 7',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reverse + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,7)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 7)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,7)', '$property_current_line(S_noarrow) = 0',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_reversed = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES text_member_' + str(i) + ') metadata_member_' + str(i) for i in reversed(range(len(members)))) + '])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reversed) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,7)',
        'S_fetch = $lbr_seek(S_return,-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED (' + case['initial'] + ')',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    # PHP-Parser canonicalizes builtin Identifiers; original source bytes retain case.
    checks += ['$base64(text_member_' + str(i) + ') = $ptascii("' + part.lower() + '")' for i, part in enumerate(case['raw_members'])]
    if case['default'] == 'omitted':
        checks += ['phpType5 = ABSENT']
    elif case['initial'] in ('PNULL', 'PBOOL false'):
        checks += ['phpType5 = NExprConstFetch (NName (BYTES text_default) metadata_default_name) metadata_default',
                   '$base64(text_default) = $ptascii("' + ('null' if case['initial'] == 'PNULL' else 'false') + '")']
    elif case['initial'] == 'PINT 0':
        checks += ['phpType5 = NScalarInt (INTEGER 0) metadata_default']
    else:
        assert case['initial'] == 'PFLOAT 0'
        checks += ['phpType5 = NScalarFloat (FLOAT text_default) metadata_default', '$hex_bits(text_default,0) = 0']
    states = ['S_front', 'S_return', 'S_fetch']
    def seek(name, previous, statement):
        z = line(statement)
        return [name + ' = $lbr_seek(' + previous + ',' + str(z) + ',30000)', '$lbr_phase(' + name + ',' + str(z) + ')', name + '.COMPLETION = NORMAL']
    checks += seek('S_copied', 'S_fetch', '$copy319 = false;')
    checks += ['S_copied.STORE[n_copy] = DEFINED (' + case['initial'] + ')', 'n_copy =/= n_field',
               '$propref_at(S_copied.PROPREFS,n_copy) = eps', '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1']
    checks += seek('S_aliases', 'S_copied', case['steps'][0]['statement'])
    checks += ['$lookup(S_aliases.ENV,$ptascii("a319")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("b319")) = (n_field)',
               'S_aliases.STORE[n_field] = DEFINED (' + case['initial'] + ')',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
               'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)']
    states += ['S_copied', 'S_aliases']; previous = 'S_aliases'
    for index, step in enumerate(case['steps']):
        state = 'S_step_' + str(index)
        capture = next((item for item in case['captures'] if item['after'] == index), None)
        marker = capture['marker'] if capture else (case['steps'][index + 1]['statement'] if index + 1 < len(case['steps']) else 'try { $b319 = []; } catch (\\TypeError $e) {')
        checks += seek(state, previous, marker)
        checks += [state + '.STORE[n_field] = DEFINED (' + step['value'] + ')',
                   state + '.STORE[n_copy] = DEFINED (PBOOL false)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        if capture:
            cell = 'n_capture_' + str(index)
            checks += ['$lookup(' + state + '.ENV,$ptascii("' + capture['name'] + '")) = (' + cell + ')',
                       state + '.STORE[' + cell + '] = DEFINED (' + capture['value'] + ')', cell + ' =/= n_field',
                       '$propref_at(' + state + '.PROPREFS,' + cell + ') = eps',
                       '$heap_owners($heap_graph(' + state + '),HCELL ' + cell + ') = 1']
        states.append(state); previous = state
    checks += seek('S_array', previous, 'try { $a319 = new \\stdClass(); } catch (\\TypeError $e) {')
    checks += seek('S_object', 'S_array', '$b319 = 37;')
    for state in ('S_array', 'S_object'):
        checks += [state + '.STORE[n_field] = DEFINED PNULL', '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)']
    checks += ['S_before = $lbr_seek(S_object,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
               'S_before.STORE[n_field] = DEFINED (' + case['final'] + ')',
               '$propref_at(S_before.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_before),HCELL n_field) = 3']
    checks += seek('S_detached', 'S_before', '$a319 = [];')
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
               '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2', 'S_detached.STORE[n_field] = DEFINED (' + case['final'] + ')']
    checks += seek('S_written', 'S_detached', '$copy319 = true;')
    checks += ['S_written.STORE[n_field] = DEFINED (PARRAY n_free)', '$propref_at(S_written.PROPREFS,n_field) = eps',
               '(HARRAY n_free) <- $pools_nodes(S_written.POOLS)', 'S_written.ARRAYS[n_free].ITEMS = eps',
               '$heap_owners($heap_graph(S_written),HARRAY n_free) = $(1 + $heap_count(HARRAY n_free,$pools_nodes(S_written.POOLS)))',
               'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
               'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = $ptascii("' + case['stdout'] + '")',
               '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
               'S_end.POOLS = S_written.POOLS', '(HARRAY n_free) <- S_end.ALLOCATIONS',
               '$heap_owners($heap_graph(S_end),HARRAY n_free) = $heap_count(HARRAY n_free,$pools_nodes(S_end.POOLS))']
    for capture in case['captures']:
        checks += ['~((HCELL n_capture_' + str(capture['after']) + ') <- S_end.ALLOCATIONS)']
    for state in [*states, 'S_array', 'S_object', 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')', '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('weak', 'strict'), default='weak')
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--form')
    selection.add_argument('--headers-only', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    folder = Path(__file__).with_name(STEM + ('_review' if args.suite == 'strict' else ''))
    cases = json.loads((folder / 'cases.json').read_text())
    assert args.headers_only or args.form in cases
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.peer.__file__),
             *folder.iterdir(), *modules, *(ROOT / p for p in ('spec/semantics/modules.json', 'spec/php.watsup',
             'spec/schema.json', 'frontend/worker.php', 'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py',
             'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
             '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
             'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): prior.peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'suite': args.suite, 'form': args.form,
              'scope': 'headers-only' if args.headers_only else 'lifecycle', 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'passed': False}
    try:
        if args.headers_only:
            checks = header_fields(); report['ordered_header_tuples'] = 300
            report['promoted_prior_header_assertions'] = 18
        else:
            source = folder / cases[args.form]['source']
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], out / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            finally:
                try: adapter.close()
                finally: frontend.close()
            checks = fields(checked['fixture'], source, cases[args.form])
        report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                            + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 360)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): prior.peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', report['scope'], args.form, report['premises'])


if __name__ == '__main__':
    main()
