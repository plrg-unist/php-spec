#!/usr/bin/env python3
"""Check block reference getters, lexical slots and real alias-cell retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import ordinary_parent_backed_get_child_slots_protocol as backed
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('ordinary_parent_backed_reference_get_child_slots')
unbacked = backed.unbacked
sha = backed.sha
quoted = backed.quoted
PREFIX = backed.PREFIX.replace('290', '291')
PREFIX = PREFIX.replace('def $ucsa_phase(S,n_stage,n) = false -- otherwise', r'''def $ucsa_phase(S,5,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask_tail*
  -- if $base64(text_name) = $ptascii("alias291")
def $ucsa_phase(S,6,n) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ucsa_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, kind):
    checks = []
    old_namespace = 'Ns290BackedChildSlotBlock' + chr(92)
    namespace = 'Ns291ReferenceChildSlot' + kind.title() + chr(92)
    for check in backed.fields(fixture, source, 'block'):
        if check.startswith(('U = ', 'S_start = ')):
            checks.append(check)
            continue
        for name in ['Box', 'Parent']:
            check = check.replace(quoted(old_namespace + name + '290'), quoted(namespace + name + '291'))
        check = check.replace('290', '291').replace('N|B|', 'N|G|B|')
        if check.startswith('pfunction_get.SIGNATURE = '):
            check = check.replace('BYREF false', 'BYREF true')
        if check.startswith('phpType38_get = NPropertyHook '):
            check = check.replace('(BOOLEAN false)', '(BOOLEAN true)')
        if kind == 'null':
            check = check.replace('$property_default_state(S_get,ppropertydesc_tag) = (PROP_VALUE (DIRECT (PINT 17)))',
                                  '$property_default_state(S_get,ppropertydesc_tag) = (PROP_VALUE (DIRECT PNULL))')
            check = check.replace('ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 17))',
                                  'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT PNULL)')
        check = check.replace('ppropertyslot_tag_live.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
                              'ppropertyslot_tag_live.STATE = PROP_VALUE (ALIAS n_tagcell)')
        check = check.replace('[HOBJECT n_middle,HOBJECT n_leaf,HOBJECT n_tail]',
                              '[HOBJECT n_middle,HCELL n_tagcell,HOBJECT n_tail]')
        check = check.replace('[HOBJECT n_leaf,HOBJECT n_tail]', '[HCELL n_tagcell,HOBJECT n_tail]')
        check = check.replace('S_raw = $ucsa_seek(S_get,1,n_root,30000)',
                              'S_raw = $ucsa_seek(S_alias,1,n_root,30000)')
        checks.append(check)
    at = checks.index('S_raw = $ucsa_seek(S_alias,1,n_root,30000)')
    initial = 'PNULL' if kind == 'null' else '(PINT 17)'
    checks[at:at] = [
        '$property_hook_reference_decl(S_get,ppropertydesc_tag)',
        'S_return = $ucsa_seek(S_get,6,n_root,30000)', '$ucsa_phase(S_return,6,n_root)',
        'S_return.RESULT = REFERENCE n_tagcell', 'S_return.STORE[n_tagcell] = DEFINED ' + initial,
        '$propref_at(S_return.PROPREFS,n_tagcell) = eps',
        '$heap_owners($heap_graph(S_return),HCELL n_tagcell) = 2',
        '$call_reference_operand_valid(S_return,S_return.RESULT)',
        '$objectprops_at(S_return.OBJECTPROPS,n_root) = ([ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_reference,ppropertyslot_tail])',
        'ppropertyslot_reference.STATE = PROP_VALUE (ALIAS n_tagcell)',
        'ppropertyslot_reference.DECL = (ppropertydesc_tag.ORIGIN)',
        'S_alias = $ucsa_seek(S_return,5,n_root,30000)', '$ucsa_phase(S_alias,5,n_root)',
        'S_alias.CURRENT = eps', 'S_alias.FRAMES = eps', 'S_alias.HELD = eps',
        '$ucsa_output(S_alias.EVENTS) = $ptascii("N|G|B|")',
        '$lookup(S_alias.ENV,$ptascii("alias291")) = (n_tagcell)',
        'S_alias.STORE[n_tagcell] = DEFINED (POBJECT n_leaf)',
        '$propref_at(S_alias.PROPREFS,n_tagcell) = eps',
        '$heap_owners($heap_graph(S_alias),HCELL n_tagcell) = 2',
        'S_return_zero = $drive_steps(S_return,0)', 'S_return_zero.COMPLETION = BUDGET',
        'S_return_zero[.COMPLETION = NORMAL] = S_return',
        'S_return_one = $drive_steps(S_return,1)', 'S_return_one.COMPLETION = BUDGET',
        '$ucsa_seek(S_return_zero[.COMPLETION = NORMAL],5,n_root,30000) = S_alias',
        '$ucsa_seek(S_return_one[.COMPLETION = NORMAL],5,n_root,30000) = S_alias',
    ]
    at = checks.index('$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HCELL n_tagcell,HOBJECT n_tail]')
    checks[at:at] = [
        '$lookup(S_raw.ENV,$ptascii("alias291")) = eps',
        'S_raw.STORE[n_tagcell] = DEFINED (POBJECT n_leaf)',
        '$propref_at(S_raw.PROPREFS,n_tagcell) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_tagcell) = 1',
        '$node_children(S_raw,HCELL n_tagcell) = [HOBJECT n_leaf]',
    ]
    at = checks.index('S_done = $drive(S_leaf,30000)')
    checks.insert(at, '~((HCELL n_tagcell) <- S_leaf.ALLOCATIONS)')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', required=True, choices=['initialized', 'null'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-' + args.kind + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(backed.__file__), Path(unbacked.__file__), source, *modules, *(ROOT / p for p in (
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
