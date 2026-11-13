#!/usr/bin/env python3
"""Ground namespace authority at a genuine mixed-source Notice fence."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import class_negative_int_constant_alias_stdclass_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('namespaced_class_int_constant_alias_stdclass_reference_notice_review_cases.json')
NAMESPACE = r'ReviewNotice30\\Inner'
CLASS = NAMESPACE + r'\\ReviewMixedNamespace30'


def namespaced(text):
    return (text.replace('ReviewMixedNegativeConstant29', CLASS)
        .replace('$ptascii("take")', '$ptascii("' + NAMESPACE + r'\\take")')
        .replace('$ptascii("h")', '$ptascii("' + NAMESPACE + r'\\h")'))


PREFIX = namespaced(prior.PREFIX)
REACHED = [namespaced(line) for line in prior.REACHED]
i = REACHED.index('$base64(text_class) = pclassdesc.NAME')
REACHED[i:i + 1] = [
    '$base64(text_class) = $ptascii("ReviewMixedNamespace30")',
    'pclassdesc.NAME = $ptascii("' + CLASS + '")',
]
CONTEXT = r'''
S_pre.SOURCES = [pcunit]
pcunit = $pcsource(n_source, pcunit.AST)
pcunit.AST = PROGRAM ([NStmtNamespace (NName (BYTES text_namespace) metadata_namespace) (SEQUENCE statement_namespace*) metadata_block])
$base64(text_namespace) = $ptascii("ReviewNotice30\\Inner")
$plclasscontext(pcunit, pcpath_owner, $call_sourcefile(S_pre.FILES, porigin_owner), pclassdesc.LINE) = (ptcontext_owner)
ptcontext_owner.NAMESPACE = $base64(text_namespace)
ptcontext_owner.FILE = $call_sourcefile(S_pre.FILES, porigin_owner)
$ptvalidname($base64(text_class), true) /\ ~(92 <- $base64(text_class))
pclassdesc.NAME = $ptjoin(ptcontext_owner.NAMESPACE, $base64(text_class))
$base64(text_class) =/= pclassdesc.NAME
$origin_node(S_pre.SOURCES, porigin_owner) = (statement_owner)
$pchcompile(statement_owner, false, ptcontext_owner) = PCHOK pchheader eps
pchheader.KIND = "class" /\ pchheader.NAME = pclassdesc.NAME
pchheader.BODY = SEQUENCE ([statement_constants, statement_properties, statement_static])
'''.strip().splitlines()

NAMESPACE_CONTROLS = r'''
$named_reference_notice_class_name(S_pre, pclassdesc, $base64(text_class))
$named_reference_notice_class_name(S_pre, pclassdesc, pclassdesc.NAME)
~$named_reference_notice_class_name(S_pre, pclassdesc, eps)
~$named_reference_notice_class_name(S_pre, pclassdesc, $ptascii("7Wrong"))
~$named_reference_notice_class_name(S_pre, pclassdesc, $ptascii("Wrong"))
~$named_reference_notice_class_name(S_pre, pclassdesc, $ptascii("Other\\Name"))
~$named_reference_notice_class_name(S_pre, pclassdesc[.LINE = 0], $base64(text_class))
~$named_reference_notice_class_name(S_pre, pclassdesc[.ORIGIN = PORIGIN 999 pcpath_owner], $base64(text_class))
~$named_reference_notice_class_name(S_pre[.SOURCES = eps], pclassdesc, $base64(text_class))
~$named_reference_notice_class_name(S_pre[.FILES = eps], pclassdesc, $base64(text_class))
pcunit_global_namespace = $pcsource(n_source, PROGRAM ([NStmtNamespace ABSENT (SEQUENCE statement_namespace*) metadata_block]))
$plclasscontext(pcunit_global_namespace, pcpath_owner, ptcontext_owner.FILE, pclassdesc.LINE) = (ptcontext_global)
ptcontext_global.NAMESPACE = eps
~$named_reference_notice_class_name(S_pre[.SOURCES = [pcunit_global_namespace]], pclassdesc, $base64(text_class))
statement_other_namespace = NStmtNamespace (NName (BYTES "T3RoZXI=") metadata_namespace) (SEQUENCE statement_namespace*) metadata_block
program_other_namespace = PROGRAM ([statement_other_namespace])
pcunit_other_namespace = $pcsource(n_source, program_other_namespace)
$plclasscontext(pcunit_other_namespace, pcpath_owner, ptcontext_owner.FILE, pclassdesc.LINE) = (ptcontext_other)
ptcontext_other.NAMESPACE = $ptascii("Other")
S_other_namespace = S_pre[.SOURCES = [pcunit_other_namespace]]
~$named_reference_notice_class_constants(S_other_namespace, pclassdesc, pclassdesc.CONSTANTS)
~$named_reference_notice_array(S_other_namespace, PARRAY n_root)
$heap_graph(S_other_namespace) = H_pre
S_stale_ast = S_pre[.SOURCES = [pcunit[.AST = program_other_namespace]]]
$plclasscontext(S_stale_ast.SOURCES[0], pcpath_owner, ptcontext_owner.FILE, pclassdesc.LINE) = eps
~$named_reference_notice_array(S_stale_ast, PARRAY n_root)
S_stale_namespace = $cint_raw(S_pre, [PCINDEX 0], (statement_other_namespace))
$plclasscontext(S_stale_namespace.SOURCES[0], pcpath_owner, ptcontext_owner.FILE, pclassdesc.LINE) = eps
~$named_reference_notice_array(S_stale_namespace, PARRAY n_root)
$plclasscontext(pcunit, pcpath_owner ++ [PCINDEX 999], ptcontext_owner.FILE, pclassdesc.LINE) = eps
$plclasscontext(pcunit, pcpath_owner, eps, pclassdesc.LINE) = eps
$plclasscontext(pcunit, pcpath_owner, ptcontext_owner.FILE, 0) = eps
'''.strip().splitlines()


def selected_controls():
    selected = {'S_other_cell', 'S_dead', 'S_no_source', 'S_owner', 'S_owner_name',
        'S_visibility', 'S_final_constant', 'S_typed_constant', 'S_unfolded',
        'S_initializer', 'S_missing_descriptor', 'S_wrong_raw_owner', 'S_no_pool',
        'S_wrong_pool_value', 'S_wrong_pool_class'}
    lines = []
    active = False
    for line in prior.CONTROLS:
        if line == '$named_reference_notice_class_constants(S_pre, pclassdesc, eps)':
            break
        if line.startswith('S_') and ' = ' in line:
            active = line.split(' = ', 1)[0] in selected
        if active:
            lines.append(namespaced(line))
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress', 'checkpoint', 'post'), default='post')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    row, = json.loads(CATALOGUE.read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == digest(types.PHP)
    assert native['source_sha256'] == digest(source) == row['source_sha256']
    assert native['stdout'] == row['native_stdout'] and native['stderr'] == row['native_stderr']
    assert native['exit'] == row['native_exit'] == 0
    directory = args.output.resolve()
    directory.mkdir(parents=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), CATALOGUE, provenance, source, types.PHP,
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = REACHED + CONTEXT + ([namespaced(line) for line in prior.POST] if args.part == 'checkpoint' else [namespaced(line) for line in prior.POST[:10]] if args.part == 'post' else [])
    derived = NAMESPACE_CONTROLS + selected_controls() if args.part == 'post' else [namespaced(line) for line in prior.PROTOCOL] if args.part == 'ingress' else []
    checks = [initial] + reached + derived
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 1200)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
        'derived_conditions': len(derived), 'heap_bindings': len({check.split(' = ', 1)[0] for check in reached if check.startswith('H_') and ' = $heap_graph(' in check}), 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
