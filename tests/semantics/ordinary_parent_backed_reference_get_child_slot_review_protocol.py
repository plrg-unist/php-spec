#!/usr/bin/env python3
"""Check reference GET cells, lexical slots and shared-child retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import ordinary_parent_backed_get_child_slot_review_protocol as backed
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('ordinary_parent_backed_reference_get_child_slot_review')
sha = backed.sha
quoted = backed.quoted
PREFIX = backed.PREFIX.replace('290', '291').replace(
    'def $ucsp_phase(S,n_stage,n) = false -- otherwise', r'''
def $ucsp_phase(S,5,n) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ucsp_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    checks = backed.fields(fixture, source, 'block')
    namespace = 'Ns290BackedChildSlotBlockPeer' + chr(92)
    target_namespace = 'Ns291ReferenceChildSlot' + form.title() + 'Peer' + chr(92)
    replacements = {
        'S_raw = $ucsp_seek(S_start,0,0,30000)': 'S_raw = $ucsp_seek(S_fetch,0,0,30000)',
        'ppropertyslot_pad.STATE = PROP_VALUE (DIRECT (POBJECT n_pad))':
            'ppropertyslot_pad.STATE = PROP_VALUE (ALIAS n_padcell)',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_pad,HOBJECT n_tail]':
            '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HCELL n_padcell,HOBJECT n_tail]',
        '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_pad,HOBJECT n_tail]':
            '$node_children(S_middle,HOBJECT n_root) = [HCELL n_padcell,HOBJECT n_tail]',
        'S_raw.STORE[n_get] = DEFINED (PBOOL false)': 'S_raw.STORE[n_get] = DEFINED (PINT 1)',
        'S_outside.STORE[n_get] = DEFINED (PBOOL false)': 'S_outside.STORE[n_get] = DEFINED (PINT 1)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}':
            'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF true}',
        'phpType38_byref = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) phpType39_get metadata_get':
            'phpType38_byref = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") eps) (NIdentifier (BYTES "cGFk") eps) eps) metadata_get',
    }
    assert set(replacements) <= set(checks)
    result = []
    initial = 'PINT 17' if form == 'initialized' else 'PNULL'
    for check in checks:
        check = replacements.get(check, check)
        if form == 'initialized':
            check = check.replace('ppropertydesc_pad.DEFAULT = PROP_NULL',
                                  'ppropertydesc_pad.DEFAULT = PROP_STORED porigin_default')
            check = check.replace('$property_default_state(S_raw,ppropertydesc_pad) = (PROP_VALUE (DIRECT PNULL))',
                                  '$property_default_state(S_raw,ppropertydesc_pad) = (PROP_VALUE (DIRECT (PINT 17)))')
        check = check.replace('NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false)',
                              'NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true)')
        for name in ('Root', 'Parent'):
            check = check.replace(quoted(namespace + name + '290'), quoted(target_namespace + name + '291'))
        result.append(check if check.startswith(('U = ', 'S_start = ')) else
                      check.replace('root290', 'root291').replace('outside290peer', 'outside291peer').replace('get290peer', 'get291peer'))
        if check.startswith('S_start = '):
            result += [
                'S_fetch = $ucsp_seek(S_start,5,0,30000)', '$ucsp_phase(S_fetch,5,0)',
                'S_fetch.COMPLETION = NORMAL', 'S_fetch.CURRENT = eps', 'S_fetch.FRAMES = eps',
                'S_fetch.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook_fetch "fetch") :: (PROPERTY_REF_FETCH z_fetch) :: ptask_fetch*',
                'ppropertyhook_fetch.OBJECT = n_root', 'S_fetch.RESULT = REFERENCE n_padcell',
                'S_fetch.STORE[n_padcell] = DEFINED (' + initial + ')',
                '$heap_owners($heap_graph(S_fetch),HCELL n_padcell) = 2',
                '$heap_owners($heap_graph(S_fetch),HOBJECT n_root) = 1',
                '$propref_at(S_fetch.PROPREFS,n_padcell) = eps',
                '$call_reference_operand_valid(S_fetch,S_fetch.RESULT)',
                '$property_hook_result_tail(S_fetch,ppropertyhook_fetch,S_fetch.TODO)',
                '$ucsp_output(S_fetch.EVENTS) = $ptascii("B|Q|")',
                '$call_descriptors_valid(S_fetch)', '$property_state_valid(S_fetch)',
            ]
        if check == 'ppropertyslot_pad.STATE = PROP_VALUE (ALIAS n_padcell)':
            result += [
                'S_raw.STORE[n_padcell] = DEFINED (POBJECT n_pad)',
                '$lookup(S_raw.ENV,$ptascii("alias291peer")) = eps',
                '$propref_at(S_raw.PROPREFS,n_padcell) = eps',
                '$heap_owners($heap_graph(S_raw),HCELL n_padcell) = 1',
                '$node_children(S_raw,HCELL n_padcell) = [HOBJECT n_pad]',
            ]
    if form == 'initialized':
        result += ['porigin_default = PORIGIN n_source (pcpath_property ++ [PCFIELD 1])']
    result += [
        '$property_hook_reference_decl(S_raw,ppropertydesc_pad)',
        '~((HCELL n_padcell) <- S_pad.ALLOCATIONS)',
        'S_fetch_zero = $drive_steps(S_fetch,0)', 'S_fetch_zero = S_fetch[.COMPLETION = BUDGET]',
        'S_fetch_one = $drive_steps(S_fetch,1)', 'S_fetch_one.COMPLETION = BUDGET',
        '$drive(S_fetch_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_fetch_one[.COMPLETION = NORMAL],30000) = S_done',
        'statement_nobacking = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) phpType5_default metadata_item])) (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) (SEQUENCE ([NStmtReturn (NScalarInt (INTEGER 7) eps) eps])) metadata_get])) metadata_group',
        'S_nobacking = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_nobacking) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_own_slot(S_nobacking,ppropertydesc_parentpad,ppropertydesc_pad)',
        'statement_nestedblock = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) phpType5_default metadata_item])) (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) (SEQUENCE ([NStmtReturn (NExprArrowFunction (SEQUENCE eps) (BOOLEAN false) (BOOLEAN false) (SEQUENCE eps) ABSENT expression_backed eps) eps])) metadata_get])) metadata_group',
        'S_nestedblock = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_nestedblock) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_own_slot(S_nestedblock,ppropertydesc_parentpad,ppropertydesc_pad)',
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['initialized', 'null'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-reference-' + args.form + '-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(backed.__file__), Path(backed.unbacked.__file__), source, *modules, *(ROOT / p for p in (
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
