#!/usr/bin/env python3
"""Check sole backed GET slots, source refusals and shared-child cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import ordinary_parent_unbacked_get_child_slot_review_protocol as unbacked
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('ordinary_parent_backed_get_child_slot_review')
sha = unbacked.sha
quoted = unbacked.quoted
PREFIX = unbacked.PREFIX.replace('289', '290')


def fields(fixture, source, form):
    checks = unbacked.fields(fixture, source, form)
    namespace = 'Ns289UnbackedChildSlot' + form.title() + 'Peer' + chr(92)
    replacements = {
        '$property_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_pad]':
            '$property_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_pad,ppropertydesc_tail]',
        '~$property_hook_override_backed(S_raw,ppropertydesc_pad)':
            '$property_hook_override_backed(S_raw,ppropertydesc_pad)',
        '$property_hook_ordinary_backing(S_raw,ppropertydesc_pad,|S_raw.CLASSES|)':
            '~$property_hook_ordinary_backing(S_raw,ppropertydesc_pad,|S_raw.CLASSES|)',
        '~$hook_body_backed(phpType39_get,$ptascii("pad"))':
            '$hook_body_backed(phpType39_get,$ptascii("pad"))',
        '$property_hook_child_append_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad)':
            '$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad)',
        '$property_layout_appended(S_raw,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_pad,ppropertydesc_middle,ppropertydesc_tail]) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_pad]':
            '$property_layout_parent(S_raw,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor]',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_tail,HOBJECT n_pad]':
            '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_pad,HOBJECT n_tail]',
        '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_tail,HOBJECT n_pad]':
            '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_pad,HOBJECT n_tail]',
        '$ucsp_output(S_tail.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|")':
            '$ucsp_output(S_tail.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|")',
        '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_pad]':
            '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_tail]',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_leaf) = 1':
            '$heap_owners($heap_graph(S_tail),HOBJECT n_leaf) = 2',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_pad) = 1':
            '$heap_owners($heap_graph(S_tail),HOBJECT n_pad) = 0',
        '~((HOBJECT n_tail) <- S_tail.ALLOCATIONS)': '~((HOBJECT n_pad) <- S_tail.ALLOCATIONS)',
        '~(n_pad <- S_tail.DESTRUCTION.CALLED)': '~(n_tail <- S_tail.DESTRUCTION.CALLED)',
        '$ucsp_output(S_outside.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|U|Z|")':
            '$ucsp_output(S_outside.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|T|Z|")',
        '$ucsp_output(S_done.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|U|Z|L|E|")':
            '$ucsp_output(S_done.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|T|Z|L|E|")',
    }
    assert set(replacements) <= set(checks)
    result = []
    for check in checks:
        check = replacements.get(check, check)
        if check.startswith('$origin_node(S_raw.SOURCES,PORIGIN n_source pcpath_group) = '):
            check = check.replace('metadata_pad) ABSENT metadata_item', 'metadata_pad) phpType5_default metadata_item')
        if form == 'short':
            check = check.replace('ppropertydesc_pad.DEFAULT = PROP_NULL',
                                  'ppropertydesc_pad.DEFAULT = PROP_STORED porigin_default')
            check = check.replace('$property_default_state(S_raw,ppropertydesc_pad) = (PROP_VALUE (DIRECT PNULL))',
                                  '$property_default_state(S_raw,ppropertydesc_pad) = (PROP_VALUE (DIRECT (PINT 17)))')
        check = check.replace('[ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_pad]',
                              '[ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_pad,ppropertyslot_tail]')
        if check.startswith('~$property_hook_child_append_slot(S_raw,') or check.startswith('~$property_hook_child_append_slot(S_parent'):
            check = check.replace('$property_hook_child_append_slot', '$property_hook_child_own_slot')
        if check.startswith('~$property_hook_child_append_slot(S_byref,'):
            check = check.replace('$property_hook_child_append_slot', '$property_hook_child_own_slot')
        for name in ('Root', 'Parent'):
            check = check.replace(quoted(namespace + name + '289'),
                                  quoted(namespace.replace('289Unbacked', '290Backed') + name + '290'))
        result.append(check if check.startswith(('U = ', 'S_start = ')) else check.replace('289', '290').replace('S_tail', 'S_pad'))
    result += [
        '~$property_hook_child_append_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad)',
        '~$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad[.NAME = $ptascii("other")])',
        '~$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3,PCINDEX 1])])',
        'phpType39_virtual = NExprVariable (BYTES "b3RoZXI=") eps',
        'phpType39_otherreceiver = NExprPropertyFetch (NExprVariable (BYTES "b3RoZXI=") eps) (NIdentifier (BYTES "cGFk") eps) eps',
        'phpType39_othername = NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") eps) (NIdentifier (BYTES "b3RoZXI=") eps) eps',
        'phpType39_backed = expression_backed',
        'phpType39_nested = NExprArrowFunction (SEQUENCE eps) (BOOLEAN false) (BOOLEAN false) (SEQUENCE eps) ABSENT expression_backed eps',
    ]
    if form == 'short':
        result += ['porigin_default = PORIGIN n_source (pcpath_property ++ [PCFIELD 1])']
    for label in ('virtual', 'otherreceiver', 'othername', 'nested'):
        result += [
            'phpType38_' + label + ' = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_' + label + ' metadata_get',
            'statement_' + label + ' = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) ABSENT metadata_item])) (SEQUENCE ([phpType38_' + label + '])) metadata_group',
            'S_' + label + ' = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_' + label + ') :: pcunit.OCCURRENCES]]]',
            '~$property_hook_child_own_slot(S_' + label + ',ppropertydesc_parentpad,ppropertydesc_pad)',
        ]
    result += [
        'phpType38_explicit = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_get ([MhookParameterList true])',
        'statement_explicit = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) phpType5_default metadata_item])) (SEQUENCE ([phpType38_explicit])) metadata_group',
        'S_explicit = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_explicit) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_own_slot(S_explicit,ppropertydesc_parentpad,ppropertydesc_pad)',
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['short', 'block'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-' + args.form + '-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(unbacked.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
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
        checks = fields(checked['fixture'], source, args.form); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
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
