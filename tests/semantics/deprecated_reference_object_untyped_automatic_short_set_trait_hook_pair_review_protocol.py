#!/usr/bin/env python3
"""Check automatic short SET storage and unique/shared child cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_parented_trait_hook_pair_review_protocol as base
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_automatic_short_set_trait_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREFIX = base.PREFIX.replace('281', '284')
SELECTED = base.SELECTED.replace('B|Q|C|', 'B|Q|S|C|')


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns281ParentedTrait' + form + 'PairPeer' + chr(92)
    new = 'Ns284AutomaticShortSetTrait' + form + 'PairPeer' + chr(92)
    quoted = base.base.quoted
    body_queries = {
        'phpType39_get = expression_get', 'phpType39_set = expression_set',
        'phpType39_get = SEQUENCE statement_get*', 'phpType39_set = SEQUENCE statement_set*',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set,false))',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
    }
    checks = []
    for check in base.fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for name in ('Root', 'RootPad', 'Parent'):
            check = check.replace(quoted(old + name + '281'), quoted(new + name + '284'))
        check = check.replace('281', '284').replace('B|Q|C|', 'B|Q|S|C|').replace('I|F|M|', 'I|F|U|M|')
        if check in body_queries:
            continue
        if check == '$hook_body_backed(phpType39_get,ppropertydesc_source.NAME)':
            checks += [
                'phpType39_get = ' + ('expression_get' if actual else 'SEQUENCE statement_get*'),
                'phpType39_set = expression_set',
                '~$hook_body_backed(phpType39_get,ppropertydesc_source.NAME)',
                '~$hook_body_backed(expression_set,ppropertydesc_source.NAME)',
                '~$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME)',
                ('' if actual else '~') + '$hook_pair_untyped_trait_set_backed_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME)',
                'phpType38_no_backing_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set (SEQUENCE eps) metadata_set',
                '~$hook_pair_untyped_trait_headers(phpType38_get,phpType38_no_backing_set,ppropertydesc_source.NAME)',
                '~$hook_pair_untyped_trait_bodies(phpType39_get,SEQUENCE eps,ppropertydesc_source.NAME)',
            ]
            continue
        check = check.replace('ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT PNULL)',
                              'ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (POBJECT n_padleaf))')
        check = check.replace('$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf]',
                              '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf,HOBJECT n_padleaf]')
        check = check.replace('$property_slot_release_job(S_raw,n_receiver,ppropertyslot_rootpad) = eps',
                              '$property_slot_release_job(S_raw,n_receiver,ppropertyslot_rootpad) = [DESTRUCTION_VALUE (HOBJECT n_padleaf)]')
        checks.append(check)
    at = checks.index('ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (POBJECT n_padleaf))') + 1
    checks[at:at] = [
        'S_raw.OBJECTS[n_padleaf] = INSTANCE porigin_padleaf',
        '$class_at(S_raw.CLASSES,porigin_padleaf) = (pclassdesc_padleaf)',
        'pclassdesc_padleaf.NAME = ' + quoted(new + 'PadLeaf284'),
        '$objectprops_at(S_raw.OBJECTPROPS,n_padleaf) = (eps)',
        '$node_children(S_raw,HOBJECT n_padleaf) = eps',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_padleaf) = 1',
        '~(n_padleaf <- S_raw.DESTRUCTION.CALLED)',
    ]
    at = checks.index('pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]') + 1
    receipts = [
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set,false))',
        r'$(z_set > 0 /\ z_set >= $source_line(metadata_set) /\ z_set <= $source_end_line(metadata_set))',
        '$property_set_expression(S_raw,porigin_set) = ((ppropertydesc_source,expression_set,$source_line(metadata_set)))',
    ]
    if actual:
        receipts += [
            '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
            '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
            '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
            r'$(z_get > 0 /\ z_get >= $source_line(metadata_get) /\ z_get <= $source_end_line(metadata_get))',
        ]
    checks[at:at] = receipts
    if not actual:
        at = checks.index('S_functions = S_class[.FUNCTIONS = [pfunction_get,pfunction_set]]') + 1
        checks[at:at] = [
            'S_set_code = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.CODE.EXPRESSIONS = eps]]]',
            '$property_hook_pair_origins(S_set_code,ppropertydesc_source) = eps',
            '$property_hook_trait_pair_functions(S_set_code,ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(S_set_code,n_receiver,eps)',
        ]
    at = checks.index('~(n_leaf <- S_edge.DESTRUCTION.CALLED)') + 1
    checks[at:at] = [
        '$heap_owners($heap_graph(S_edge),HOBJECT n_padleaf) = 1',
        '~(n_padleaf <- S_edge.DESTRUCTION.CALLED)',
    ]
    at = checks.index('$node_children(S_tail,HOBJECT n_receiver) = eps') + 1
    checks[at:at] = [
        'n_padleaf <- S_tail.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_padleaf) = 0',
        '$ccn_output(S_tail.EVENTS) = $ptascii("B|Q|S|C|R|D|H|9|P|I|F|U|")',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('automatic-short-set-untyped-trait-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(base.base.__file__), Path(base.base.pair.__file__),
             Path(base.base.peer.__file__), Path(base.base.header.__file__), source, *modules, *(ROOT / p for p in (
                 'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                 '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
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
        checks = fields(checked['fixture'], source, args.form == 'actual'); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
