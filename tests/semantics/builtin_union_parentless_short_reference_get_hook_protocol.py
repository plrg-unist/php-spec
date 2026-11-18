#!/usr/bin/env python3
"""Check bounded builtin unions with real array COW, objects and source detach."""
import argparse
import base64
import json
from itertools import permutations
from pathlib import Path
import subprocess
import sys

import scalar_union_parentless_short_reference_get_hook_protocol as prior
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
STEM = 'builtin_union_parentless_short_reference_get_hook'
PREFIX = prior.PREFIX.replace('box319', 'box320').replace('a319', 'a320').replace('b319', 'b320')


def header_fields():
    checks = prior.header_fields()
    domain = ('array', 'object', 'int', 'float', 'bool', 'string', 'null')
    orders = list(permutations(domain, 2))
    for length in range(3, 8):
        for start in range(7):
            order = (domain[start:] + domain[:start])[:length]
            orders.extend((order, tuple(reversed(order))))
    for members in dict.fromkeys(orders):
        raw, mask = prior.raw(members), prior.mask(members)
        checks += ['$hook_short_reference_header(' + raw + ',' + mask + ')',
                   '$hook_short_reference_header(' + prior.raw([part.upper() for part in members]) + ',' + mask + ')',
                   '~$hook_short_reference_header(' + prior.raw(list(reversed(members))) + ',' + mask + ')',
                   '~$hook_short_reference_header(' + raw + ',' + prior.mask(members[:-1]) + ')',
                   '~$hook_short_reference_header(' + raw + ',' + prior.mask(members + ('int',)) + ')']
    for length in range(2, 8):
        members = list(domain[:length])
        duplicate = members[:-1] + [members[0]]
        checks += ['~$hook_short_reference_header(' + prior.raw(duplicate) + ',' + prior.mask(duplicate) + ')',
                   '~$hook_short_reference_header(' + prior.raw(members[:-1] + [members[0].upper()]) + ',' + prior.mask(duplicate) + ')']
        for kind in ('mixed', 'true', 'false', 'iterable', 'callable', 'void', 'never', 'integer'):
            forged = members[:-1] + [kind]
            checks += [('' if kind in ('true', 'false') and length <= 5 else '~') + '$hook_short_reference_header(' + prior.raw(forged) + ',' + prior.mask(forged) + ')']
    ordinary = prior.raw(['array', 'object', 'int'])
    for node in ('NName', 'NNameFullyQualified'):
        checks += ['~$hook_short_reference_header(' + ordinary.replace('NIdentifier', node, 1) + ',' + prior.mask(['array', 'object', 'int']) + ')']
    for branches in ('eps', '[(PTBRANCH ([PTBUILTIN "array",PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "int"]))]',
                     '[(PTBRANCH ([PTCLASS ($ptascii("array"))])),(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "int"]))]',
                     prior.mask(['ARRAY', 'object', 'int'])):
        checks += ['~$hook_short_reference_header(' + ordinary + ',' + branches + ')']
    for members in ([], ['array'], list(domain) + ['array']):
        checks += ['~$hook_short_reference_header(' + prior.raw(members) + ',' + prior.mask(members) + ')']
    for members in (['false', 'null'], ['null', 'false'], ['true', 'null'], ['null', 'true']):
        checks += ['$hook_short_reference_header(' + prior.raw(members) + ',' + prior.mask(members) + ')']
    # Each dynamic legacy pair guard is checked with its unchanged raw expression.
    for right in ('int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'float', 'float', 'bool', 'string'):
        checks += ['$hook_short_reference_header(' + prior.raw(['array', right]) + ',' + prior.mask(['array', right]) + ')']
    # The exact newly admitted guard from the older object/null review.
    checks += ['$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "b2JqZWN0") eps,NIdentifier (BYTES "YXJyYXk=") eps])) eps,[(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "array"]))])']
    return checks


def fields(fixture, source, case):
    values = case['values']; members = case['members']; mask = prior.mask(members)
    reverse = prior.mask(list(reversed(members))); lines = source.read_text().splitlines()
    line = lambda statement: [text.strip() for text in lines].index(statement) + 1
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = next(i + 1 for i, text in enumerate(lines) if '$this->' in text)
    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + prior.prior.peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box320")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)', 'pclassdesc.KIND = "class"',
        'pclassdesc.PARENT = eps', '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        'ppropertydesc.TYPE = ' + mask, '$property_hook_reference_decl(S_front,ppropertydesc)',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property', 'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES text_member_' + str(i) + ') metadata_member_' + str(i) for i in range(len(members))) + '])) metadata_union',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '~$hook_short_reference_header(phpType18,' + reverse + ')',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reverse + '])',
        '$pttypename(ppropertydesc.TYPE) = $ptascii("' + case['typename'] + '")',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)', '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        ('pfunction.CODE.STRICT' if case['strict'] else '~pfunction.CODE.STRICT'), 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (' + ('NScalarString' if case['body'] == 'literal' else 'NIdentifier') + ' (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line), '$source_line(metadata_expression) = ' + str(body_line),
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + str(body_line) + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + str(body_line) + ')',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot])']
    checks += ['$base64(text_member_' + str(i) + ') = $ptascii("' + part.lower() + '")' for i, part in enumerate(case['raw_members'])]
    if case['initial'] == 'array':
        checks += ['phpType5 = NExprArray (SEQUENCE eps) metadata_default', 'ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_initial))',
                   '(HARRAY n_initial) <- $pools_nodes(S_front.POOLS)', 'S_front.ARRAYS[n_initial].ITEMS = eps']
    else:
        checks += ['phpType5 = NExprConstFetch (NName (BYTES text_default) metadata_default_name) metadata_default',
                   '$base64(text_default) = $ptascii("' + case['default'] + '")', 'ppropertyslot.STATE = PROP_VALUE (DIRECT (' + case['initial'] + '))']
    z = str(body_line)
    checks += ['S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        '$reference_return_source(S_return,' + z + ')', '$reference_return_fetch_valid(S_return,' + z + ')', '$reference_verifies(S_return)',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reverse + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,' + z + ')', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + z + ')',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,' + z + ')', '$property_current_line(S_noarrow) = 0',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_reverse = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES text_member_' + str(i) + ') metadata_member_' + str(i) for i in reversed(range(len(members)))) + '])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reverse) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,' + z + ')',
        'S_fetch = $lbr_seek(S_return,-2,30000)', '$lbr_phase(S_fetch,-2)', 'S_fetch.COMPLETION = NORMAL',
        'S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]', '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    def seek(name, previous, statement):
        z = str(line(statement))
        return [name + ' = $lbr_seek(' + previous + ',' + z + ',30000)', '$lbr_phase(' + name + ',' + z + ')', name + '.COMPLETION = NORMAL']
    checks += seek('S_aliases', 'S_fetch', '$seed320 = ' + str(values['seed']) + ';')
    checks += ['$lookup(S_aliases.ENV,$ptascii("a320")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("b320")) = (n_field)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        '$lookup(S_aliases.ENV,$ptascii("initial320")) = eps', 'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)']
    checks += seek('S_cow', 'S_aliases', '$a320 = new \\stdClass();')
    checks += ['S_cow.STORE[n_field] = DEFINED (PARRAY n_cow)', '$lookup(S_cow.ENV,$ptascii("copyarray320")) = (n_copyarraycell)',
        'S_cow.STORE[n_copyarraycell] = DEFINED (PARRAY n_copyarray)', 'n_cow =/= n_copyarray',
        '$propref_at(S_cow.PROPREFS,n_copyarraycell) = eps',
        '$lookup(S_cow.ENV,$ptascii("seed320")) = (n_seed)', 'S_cow.STORE[n_seed] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("' + values['seed_text'] + '")))',
        'S_cow.ARRAYS[n_cow].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed),ENTRY (KINT 1) (DIRECT (PARRAY n_innerlive))]',
        'S_cow.ARRAYS[n_copyarray].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed),ENTRY (KINT 1) (DIRECT (PARRAY n_innercopy))]',
        'n_innerlive =/= n_innercopy', 'S_cow.ARRAYS[n_innerlive].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT ' + str(values['written']) + '))]',
        'S_cow.ARRAYS[n_innercopy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT ' + str(values['inner']) + '))]',
        '$heap_owners($heap_graph(S_cow),HCELL n_seed) = 3', '$propref_at(S_cow.PROPREFS,n_seed) = eps',
        '$heap_owners($heap_graph(S_cow),HARRAY n_cow) = 1', '$heap_owners($heap_graph(S_cow),HARRAY n_copyarray) = 1']
    checks += seek('S_shared', 'S_cow', '$b320 = new Leaf320();')
    checks += ['S_shared.STORE[n_field] = DEFINED (POBJECT n_old)', '$lookup(S_shared.ENV,$ptascii("copyobject320")) = (n_copyobjectcell)',
        'S_shared.STORE[n_copyobjectcell] = DEFINED (POBJECT n_old)', 'S_shared.OBJECTS[n_old] = STDINSTANCE',
        '$propref_at(S_shared.PROPREFS,n_copyobjectcell) = eps',
        '$objectprops_at(S_shared.OBJECTPROPS,n_old) = ([ppropertyslot_old])', 'ppropertyslot_old.NAME = $ptascii("tag")',
        'ppropertyslot_old.STATE = PROP_VALUE (DIRECT (PINT ' + str(values['tag_written']) + '))',
        '$heap_owners($heap_graph(S_shared),HOBJECT n_old) = 2', '$heap_owners($heap_graph(S_shared),HCELL n_seed) = 2',
        '~((HARRAY n_cow) <- S_shared.ALLOCATIONS)', '~((HARRAY n_innerlive) <- S_shared.ALLOCATIONS)']
    checks += seek('S_leaf', 'S_shared', case['steps'][0]['statement'])
    checks += ['S_leaf.STORE[n_field] = DEFINED (POBJECT n_intermediate)', 'n_intermediate =/= n_old',
        'S_leaf.OBJECTS[n_intermediate] = INSTANCE porigin_leaf', '$heap_owners($heap_graph(S_leaf),HOBJECT n_intermediate) = 1',
        '$class_at(S_leaf.CLASSES,porigin_leaf) = (pclassdesc_leaf)', 'pclassdesc_leaf.KIND = \"class\"',
        'pclassdesc_leaf.PARENT = eps', 'pclassdesc_leaf.METHODS = eps',
        '$objectprops_at(S_leaf.OBJECTPROPS,n_intermediate) = ([ppropertyslot_leaf])', 'ppropertyslot_leaf.NAME = $ptascii(\"tag\")',
        'ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (PINT ' + str(values['leaf']) + '))',
        '$heap_owners($heap_graph(S_leaf),HOBJECT n_old) = 1']
    states = ['S_front', 'S_return', 'S_fetch', 'S_aliases', 'S_cow', 'S_shared', 'S_leaf']; previous = 'S_leaf'
    for i, step in enumerate(case['steps']):
        state = 'S_step_' + str(i)
        marker = case['steps'][i + 1]['statement'] if i + 1 < len(case['steps']) else '$a320 = new Leaf320();'
        checks += seek(state, previous, marker)
        checks += [state + '.STORE[n_field] = DEFINED (' + step['value'] + ')', '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        states.append(state); previous = state
    checks += ['S_before = $lbr_seek(' + previous + ',-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (POBJECT n_live)', 'n_live =/= n_intermediate', 'S_before.OBJECTS[n_live] = INSTANCE porigin_leaf',
        '$lookup(S_before.ENV,$ptascii("kept320")) = (n_keptcell)', 'S_before.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
        '$objectprops_at(S_before.OBJECTPROPS,n_live) = ([ppropertyslot_leaf])',
        '$lookup(S_before.ENV,$ptascii("copyread320")) = eps', '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 2',
        '$heap_owners($heap_graph(S_before),HOBJECT n_old) = 1', '~((HOBJECT n_intermediate) <- S_before.ALLOCATIONS)',
        '$propref_at(S_before.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_before),HCELL n_field) = 3']
    checks += seek('S_detached', 'S_before', '$a320 = ' + str(values['free']) + ';')
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_written', 'S_detached', '$a320 = [];')
    checks += ['S_written.STORE[n_field] = DEFINED (PINT ' + str(values['free']) + ')', '$heap_owners($heap_graph(S_written),HOBJECT n_live) = 1']
    checks += seek('S_pooled', 'S_written', '$copyarray320 = false;')
    checks += ['S_pooled.STORE[n_field] = DEFINED (PARRAY n_free)', '(HARRAY n_free) <- $pools_nodes(S_pooled.POOLS)',
        'S_pooled.ARRAYS[n_free].ITEMS = eps', '$heap_owners($heap_graph(S_pooled),HARRAY n_free) = $(1 + $heap_count(HARRAY n_free,$pools_nodes(S_pooled.POOLS)))',
        'S_end = $drive_steps(S_pooled,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + case['stdout'] + '")', 'S_end.POOLS = S_pooled.POOLS',
        '(HARRAY n_free) <- S_end.ALLOCATIONS', '$heap_owners($heap_graph(S_end),HARRAY n_free) = $heap_count(HARRAY n_free,$pools_nodes(S_end.POOLS))',
        '~((HOBJECT n_live) <- S_end.ALLOCATIONS)', '~((HOBJECT n_old) <- S_end.ALLOCATIONS)', '~((HARRAY n_copyarray) <- S_end.ALLOCATIONS)',
        '((HARRAY n_innercopy) <- S_end.ALLOCATIONS) = ((HARRAY n_innercopy) <- $pools_nodes(S_end.POOLS))',
        '$heap_owners($heap_graph(S_end),HARRAY n_innercopy) = $heap_count(HARRAY n_innercopy,$pools_nodes(S_end.POOLS))']
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)' for cell in ('n_rootcell', 'n_field', 'n_seed', 'n_copyarraycell', 'n_copyobjectcell', 'n_keptcell')]
    for state in states + ['S_before', 'S_detached', 'S_written', 'S_pooled', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')', '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)', f'S_{label}_one = $drive_steps({state},1)',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main(header_report=None, extra_paths=()):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('weak', 'strict'), default='weak')
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--form'); selection.add_argument('--headers-only', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); folder = Path(__file__).with_name(STEM + ('_review' if args.suite == 'strict' else ''))
    cases = json.loads((folder / 'cases.json').read_text()); assert args.headers_only or args.form in cases
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(sys.argv[0]).resolve(), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.peer.__file__),
             *extra_paths, *folder.iterdir(), *modules, *(ROOT / p for p in ('spec/semantics/modules.json', 'spec/php.watsup',
             'spec/schema.json', 'frontend/worker.php', 'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py',
             'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
             '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): prior.prior.peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'suite': args.suite, 'form': args.form,
              'scope': 'headers-only' if args.headers_only else 'lifecycle', 'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        if args.headers_only:
            checks = header_fields()
            report.update(header_report if header_report is not None else {
                'ordered_header_tuples': 112, 'retained_scalar_header_tuples': 300,
                'promoted_prior_header_assertions': 16})
        else:
            source = folder / cases[args.form]['source']
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            finally:
                try: adapter.close()
                finally: frontend.close()
            checks = fields(checked['fixture'], source, cases[args.form])
        report['premises'] = len(checks); (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
        cap_seconds = 360 if args.headers_only else cases[args.form].get('state_timeout_seconds', 360)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', cap_seconds)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): prior.prior.peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', report['scope'], args.form, report['premises'])


if __name__ == '__main__':
    main()
