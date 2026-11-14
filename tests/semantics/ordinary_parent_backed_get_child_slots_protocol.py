#!/usr/bin/env python3
"""Check body-backed sole getters retain child declaration slots and cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import ordinary_parent_unbacked_get_child_slots_protocol as unbacked
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('ordinary_parent_backed_get_child_slots')
sha = unbacked.sha
quoted = unbacked.quoted
PREFIX = unbacked.PREFIX.replace('289', '290')


def fields(fixture, source, kind):
    checks = unbacked.fields(fixture, source, kind)
    namespace = 'Ns289UnbackedChildSlot' + kind.title() + chr(92)
    replacements = {
        'pclassdesc_root.PROPERTIES = [ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail]':
            'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_tag,ppropertydesc_tail]',
        '$property_default_state(S_get,ppropertydesc_tag) = (PROP_VALUE (DIRECT PNULL))':
            '$property_default_state(S_get,ppropertydesc_tag) = (PROP_VALUE (DIRECT (PINT 17)))',
        '$property_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_tag]':
            '$property_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tag,ppropertydesc_tail]',
        '$property_info_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_anchor]':
            '$property_info_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_middle,ppropertydesc_tag,ppropertydesc_tail,ppropertydesc_anchor]',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT PNULL)':
            'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 17))',
        '~$property_hook_override_backed(S_get,ppropertydesc_tag)':
            '$property_hook_override_backed(S_get,ppropertydesc_tag)',
        '$property_hook_ordinary_backing(S_get,ppropertydesc_tag,|S_get.CLASSES|)':
            '~$property_hook_ordinary_backing(S_get,ppropertydesc_tag,|S_get.CLASSES|)',
        '$property_hook_child_append_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)':
            '~$property_hook_child_append_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)',
        '~$property_hook_child_own_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)':
            '$property_hook_child_own_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)',
        '$property_layout_appended(S_get,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail]) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_tag]':
            '$property_layout_parent(S_get,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor]',
        'pfunction_get.LINE = 18': 'pfunction_get.LINE = 19',
        'pfunction_get.ENDLINE = 21': 'pfunction_get.ENDLINE = 22',
        '~$hook_body_backed(phpType39_get,$ptascii("tag"))':
            '$hook_body_backed(phpType39_get,$ptascii("tag"))',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((21,false))':
            '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((22,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (21)':
            '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (22)',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_tail,HOBJECT n_leaf]':
            '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_leaf,HOBJECT n_tail]',
        '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_tail,HOBJECT n_leaf]':
            '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_leaf,HOBJECT n_tail]',
        '$ucsa_output(S_tail.EVENTS) = $ptascii("N|B|M|T|")':
            '$ucsa_output(S_tail.EVENTS) = $ptascii("N|B|M|U|")',
        '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_leaf]':
            '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_tail]',
        '~((HOBJECT n_tail) <- S_tail.ALLOCATIONS)': '~((HOBJECT n_leaf) <- S_tail.ALLOCATIONS)',
        '~(n_leaf <- S_tail.DESTRUCTION.CALLED)': '~(n_tail <- S_tail.DESTRUCTION.CALLED)',
        '$ucsa_output(S_done.EVENTS) = $ptascii("N|B|M|T|U|Z|")':
            '$ucsa_output(S_done.EVENTS) = $ptascii("N|B|M|U|T|Z|")',
    }
    assert set(replacements) - set(checks) == (set() if kind == 'short' else {
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((21,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (21)'})
    result = []
    for check in checks:
        check = replacements.get(check, check)
        if check.startswith('$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_group) = '):
            check = check.replace('metadata_tag) ABSENT metadata_item', 'metadata_tag) phpType5_default metadata_item')
        check = check.replace('[ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_tag]',
                              '[ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tag,ppropertyslot_tail]')
        check = check.replace('[ppropertyslot_anchor,ppropertyslot_middle_live,ppropertyslot_tail_live,ppropertyslot_tag_live]',
                              '[ppropertyslot_anchor,ppropertyslot_middle_live,ppropertyslot_tag_live,ppropertyslot_tail_live]')
        if check.startswith('~$property_hook_child_append_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag['):
            check = check.replace('$property_hook_child_append_slot', '$property_hook_child_own_slot')
        check = check.replace(quoted(namespace + 'Box289'), quoted(namespace.replace('289Unbacked', '290Backed') + 'Box290'))
        check = check.replace(quoted(namespace + 'Parent289'), quoted(namespace.replace('289Unbacked', '290Backed') + 'Parent290'))
        if check.startswith(('U = ', 'S_start = ')):
            result.append(check)
        else:
            result.append(check.replace('289', '290').replace('S_tail', 'S_leaf'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', required=True, choices=['short', 'block'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-' + args.kind + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(unbacked.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'kind': args.kind,
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
        checks = fields(checked['fixture'], source, args.kind); report['premises'] = len(checks)
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
    print('pass', args.kind, report['premises'])


if __name__ == '__main__': main()
