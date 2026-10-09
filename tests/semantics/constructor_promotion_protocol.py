#!/usr/bin/env python3
"""Reach authentic promotion steps and check WeakReference ownership/byref sources."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
import error_handler_run as recorder
from recorded_worker import Worker

STAGE = ('S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if $receiving_function(S, porigin) = (pfunction) '
    '-- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc) '
    '-- if $class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc) '
    '-- if pclassdesc.NAME = $ptascii("CLASS") '
    '-- if pcallcontext.RECEIVER = (n_receiver) '
    '-- if $promotion_raw(S, pfunction, 0) = (psraw) '
    '-- if $promotion_descriptor(S, pfunction, 0) = (ppropertydesc) '
    '-- if $lookup(S.ENV, psraw.NAME) = (n_cell)')
PARAM = ('NParam phpType14_param (INTEGER flags_param) phpType18_param '
         'phpType4_ref phpType4_variadic phpType10_param phpType5_default '
         'phpType37_hooks metadata_param')
METHOD = ('NStmtClassMethod phpType14_method phpType24_method phpType4_method '
          'phpType11_method (SEQUENCE ([(PARAM)])) phpType18_method '
          '(SEQUENCE statement*) metadata_method')
COMMON_BEFORE = [
    '$promotion_task_valid(S, porigin, 0)',
    '$call_task_valid(S, PROMOTE_PARAMETER porigin 0)',
    r'S.ORIGIN = (porigin) /\ pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    r'ppropertydesc.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc.TYPE =/= eps',
    '$origin_source(porigin) = PORIGIN n_unit pcpath',
    'ppropertydesc.ORIGIN = PORIGIN n_unit (pcpath ++ [PCFIELD 4, PCINDEX 0])',
    '$origin_node(S.SOURCES, porigin) = (' + METHOD.replace('PARAM', PARAM) + ')',
    '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot*)',
    '$property_slot_at(ppropertyslot*, ppropertydesc.KEY) = (ppropertyslot_before)',
    r'ppropertyslot_before.DECL = (ppropertydesc.ORIGIN) /\ ppropertyslot_before.STATE = PROP_INITIAL',
    '~$promotion_task_valid(S[.CURRENT = eps], porigin, 0)',
    '~$promotion_task_valid(S[.ORIGIN = (pmethoddesc.OWNER)], porigin, 0)',
    '~$promotion_task_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])], porigin, 0)',
    '~$promotion_task_valid(S[.CURRENT = (pcallcontext[.RECEIVER = eps])], porigin, 0)',
    '~$promotion_task_valid(S[.TODO = (PROMOTE_PARAMETER porigin 0) :: S.TODO], porigin, 0)',
    '$promotion_raw(S, pfunction, 1) = eps',
    '$promotion_raw(S, pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.NAME = $ptascii("other")]]]], 0) = eps',
]
for changed_param, predicate in [
    (PARAM.replace('(INTEGER flags_param)', '(INTEGER 0)'), '$promotion_raw'),
    (PARAM.replace('phpType10_param', '(NExprVariable (BYTES "b3RoZXI=") metadata_param)'), '$promotion_raw'),
    (PARAM.replace('phpType18_param', '(NIdentifier (BYTES "c3RyaW5n") metadata_param)'), '$promotion_descriptor'),
]:
    changed_method = METHOD.replace('PARAM', changed_param)
    COMMON_BEFORE.append(predicate + '($promotion_altered(S, porigin, ' + changed_method + '), pfunction, 0) = eps')
COMMON_AFTER = [
    r'S_promoted.COMPLETION = NORMAL /\ S_promoted.TODO = ptask_tail*',
    r'S_promoted.CURRENT = S.CURRENT /\ S_promoted.ORIGIN = S.ORIGIN',
    r'S_promoted.EVENTS = S.EVENTS /\ S_promoted.ENV = S.ENV',
    r'S_promoted.STORE = S.STORE /\ S_promoted.ALLOCATIONS = S.ALLOCATIONS',
    r'S_promoted.SOURCES = S.SOURCES /\ S_promoted.CLASSES = S.CLASSES',
    '$objectprops_at(S_promoted.OBJECTPROPS, n_receiver) = (ppropertyslot_all_after*)',
    '$property_slot_at(ppropertyslot_all_after*, ppropertydesc.KEY) = (ppropertyslot_after)',
    '$property_state_valid(S_promoted)',
    '$call_descriptors_valid(S_promoted)',
    '$declaration_history_valid(S_promoted)',
    '$heap_valid($heap_prune($heap_graph(S_promoted)))',
]
CASES = {
    'weak': (ROOT / 'tests/semantics/constructor-promotion-weak.php', 'RawArrayLastPayload19', [
        r'psraw.FLAGS = 4 /\ ~psraw.BYREF /\ psraw.NAME = $ptascii("target")',
        r'ppropertydesc.VISIBILITY = PROPERTY_PRIVATE /\ ppropertydesc.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ psraw.NAME',
        'S.STORE[n_cell] = DEFINED (POBJECT n_weak)',
        '$weakref_at(S, n_weak) = (WEAKREFERENCE (n_target))',
        '$node_children(S, HOBJECT n_weak) = eps',
        '$weakref_get(S, n_weak) = POBJECT n_target',
        '$node_children(S, HOBJECT n_receiver) = eps',
    ], [
        'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (POBJECT n_weak))',
        '$node_children(S_promoted, HOBJECT n_receiver) = [HOBJECT n_weak]',
        '$node_children(S_promoted, HOBJECT n_weak) = eps',
        '$weakref_at(S_promoted, n_weak) = $weakref_at(S, n_weak)',
        '$weakref_get(S_promoted, n_weak) = $weakref_get(S, n_weak)',
        '$heap_owners($heap_prune($heap_graph(S_promoted)), HOBJECT n_weak) = $($heap_owners($heap_prune($heap_graph(S)), HOBJECT n_weak) + 1)',
        '$heap_owners($heap_prune($heap_graph(S_promoted)), HOBJECT n_target) = $heap_owners($heap_prune($heap_graph(S)), HOBJECT n_target)',
        'S_promoted.PROPREFS = S.PROPREFS',
    ]),
    'byref': (ROOT / 'tests/semantics/constructor-promotion-reference.php', 'ReferencePromotion20', [
        r'psraw.FLAGS = 1 /\ psraw.BYREF /\ psraw.NAME = $ptascii("value")',
        r'ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc.KEY = psraw.NAME',
        'S.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("v")) = (n_cell)',
        r'n_cell <- S.REFCELLS /\ S.STORE[n_cell] = DEFINED (PINT (+4))',
        '$propref_at(S.PROPREFS, n_cell) = eps',
        '$node_children(S, HOBJECT n_receiver) = eps',
    ], [
        'ppropertyslot_after.STATE = PROP_VALUE (ALIAS n_cell)',
        '$node_children(S_promoted, HOBJECT n_receiver) = [HCELL n_cell]',
        '$propref_at(S_promoted.PROPREFS, n_cell) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_receiver ppropertydesc.KEY ppropertydesc.ORIGIN]',
        '$propref_source_valid(S_promoted, n_cell, OBJECT_PROP_SOURCE n_receiver ppropertydesc.KEY ppropertydesc.ORIGIN)',
        '$node_children(S_promoted, HCELL n_cell) = $node_children(S, HCELL n_cell)',
        'S_promoted.REFCELLS = S.REFCELLS',
    ]),
}
PREFIX = r'''
dec $promotion_replace(pcoccurrence*, pcpath, pcnode) : pcoccurrence*
def $promotion_replace(eps, pcpath, pcnode) = eps
def $promotion_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $promotion_replace((PCOCCURRENCE pcpath_old pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath_old pcnode_old) :: $promotion_replace(pcoccurrence*, pcpath, pcnode)
  -- if pcpath_old =/= pcpath
dec $promotion_altered(pstate, porigin, pcnode) : pstate
def $promotion_altered(S, PORIGIN n_unit pcpath, pcnode) = S[.SOURCES = [pcunit[.OCCURRENCES = $promotion_replace(pcunit.OCCURRENCES, pcpath, pcnode)]]]
  -- if S.SOURCES = [pcunit]
  -- if pcunit.ID = n_unit
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = {args.case: CASES[args.case]} if args.case else CASES
    recorder.ROOT = ROOT
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    php, adapter, runner, bridge, worker = (ROOT / name for name in ['.tools/php/bin/php',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        '.tools/php-file.so', 'frontend/worker.php'])
    watched = [Path(__file__), manifest, *modules, php, adapter, runner, bridge, worker,
        ROOT / 'tests/semantics/profile.json', ROOT / 'spec/schema.json',
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py',
        *(row[0] for row in selected.values())]
    catalogue = ROOT / 'tests/semantics/constructor_promotion_cases.json'
    watched.append(catalogue)
    retained = {row['id']: row for row in json.loads(catalogue.read_bytes())['cases']}
    for name, row in selected.items():
        original = retained['original-9b85' if name == 'weak' else 'reference-property-caller-type']
        assert row[0].read_bytes() == original['source'].encode()
        assert sha(row[0]) == original['source_sha256']
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    before = {str(path): sha(path) for path in watched}
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert not status, status
    out = Path(tempfile.mkdtemp(prefix='promotion-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert profile['error_reporting'] == '30719'
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'revision': revision, 'working_tree_status': status, 'inputs': before, 'profile': profile,
        'mode': 'SL', 'cache': False, 'det': True, 'source_agreements': 0, 'records': [],
        'selection': list(selected), 'evaluated': False, 'application_evaluations': 0,
        'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC',
        'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        for name, (source, classname, extra_before, extra_after) in selected.items():
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / (name + '-frontend'))
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
            finally:
                frontend.close()
            adapter_worker = Worker([str(adapter), str(ROOT)], out / (name + '-adapter'))
            try:
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'], checked
            finally:
                adapter_worker.close()
            stage = STAGE.replace('"CLASS"', json.dumps(classname))
            checks = COMMON_BEFORE + extra_before + ['PhpStep: S ~> S_promoted'] + COMMON_AFTER + extra_after
            fixture = out / (name + '.watsup')
            fixture.write_text(PREFIX + '\ndec $stage(pstate) : bool\ndef $stage(S) = true -- if ' + stage + '\n'
                'def $stage(S) = false -- otherwise\ndec $seek(pstate, nat) : pstate\n'
                'def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
                'def $seek(S, n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'def $seek(S, 0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) '
                '-- if ~$stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'dec $main() : bool\ndef $main() = true\n'
                '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
                + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
                '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
                '  -- if S_found = $seek(S_initial, 2000)\n'
                '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
                '  -- if S = S_found[.COMPLETION = NORMAL]\n  -- if ' + stage + '\n'
                + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks)
                + 'def $main() = false -- otherwise\n')
            row = {'id': name, 'source': str(source), 'source_sha256': sha(source),
                'fixture': str(fixture), 'fixture_sha256': sha(fixture), 'reached_premises': len(checks),
                'setup_premises': 6, 'evaluated': False, 'passed': args.prepare_only}
            report['records'].append(row)
            if not args.prepare_only:
                row['evaluated'] = report['evaluated'] = True
                report['application_evaluations'] += 1
                row['process'] = process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / name, 120)
                row['passed'] = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
                    and (out / (name + '.stdout')).read_bytes() == b'true\n'
                    and not (out / (name + '.stderr')).read_bytes())
                print(name, row['passed'], flush=True)
                assert row['passed'], name
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
            head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = (len(report['records']) == len(selected) and all(row['passed'] for row in report['records'])
            and all(report[key] for key in ['inputs_stable', 'head_stable', 'status_stable']))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
