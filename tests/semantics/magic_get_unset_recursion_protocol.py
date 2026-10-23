"""Check declared untyped Get recursion through population and local cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
import magic_get_recursion_protocol as common
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()


def replace(lines, old, new):
    assert lines.count(old) == 1, old
    return [part for line in lines for part in (new if line == old else [line])]


FRONT = replace(common.FRONT,
    r'ppropertyget.NAME = ptbytes_name /\ ppropertyget.DECL = eps',
    [r'ppropertyget.NAME = ptbytes_name /\ ppropertyget.DECL = (ppropertyid)'])
FRONT = replace(FRONT,
    '$property_effective_desc(S_front,n_child,ptbytes_name) = eps',
    common.lines(r'''
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc)
ppropertydesc.ORIGIN = ppropertyid /\ ppropertydesc.TYPE = eps
ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ~ppropertydesc.STATIC /\ ppropertydesc.KEY = ptbytes_name
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_name) = (ppropertyslot_front)
ppropertyslot_front.DECL = (ppropertyid) /\ ppropertyslot_front.STATE = PROP_UNSET
$property_get_recursive_untyped(S_front,n_child,ptbytes_name)
'''))
INNER = common.INNER + common.lines(r'''
$property_effective_desc(S_inner,n_child,ptbytes_name) = (ppropertydesc)
$property_get_recursive_untyped(S_inner,n_child,ptbytes_name)
$objectprops_at(S_inner.OBJECTPROPS,n_child) = (ppropertyslot_inner_all*)
$property_slot_at(ppropertyslot_inner_all*,ptbytes_name) = (ppropertyslot_inner)
ppropertyslot_inner.DECL = (ppropertyid) /\ ppropertyslot_inner.STATE = PROP_UNSET
''')
INVOKE = [line.replace('RecursiveGet119', 'RecursiveGet120') for line in common.INVOKE]
HANDLER = common.HANDLER + common.lines(r'''
$property_effective_desc(S_handler,n_child,ptbytes_name) = (ppropertydesc)
$property_get_recursive_untyped(S_handler,n_child,ptbytes_name)
''')
POPULATED = replace(common.POPULATED,
    r'ppropertyslot_populated.DECL = eps /\ ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 9))',
    [r'ppropertyslot_populated.DECL = (ppropertyid) /\ ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 9))'])


def conditions(case, checked):
    name = case['id']
    prefix = 'P:' if name == 'populate' else 'L:'
    before_warning = prefix + ('G|' if name == 'populate' else 'G|g|V|')
    after_warning = before_warning + 'W|w|'
    before_result = after_warning + ('g|' if name == 'populate' else 'n|v|')
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
        'ptbytes_before_warning = $ptascii(' + json.dumps(before_warning) + ')',
        'ptbytes_after_warning = $ptascii(' + json.dumps(after_warning) + ')',
        'ptbytes_before_result = $ptascii(' + json.dumps(before_result) + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'n_warning_owners = ' + ('2' if name == 'populate' else '3'),
        'n_after_warning_owners = ' + ('2' if name == 'populate' else '3'),
        'n_at_result_owners = 2', 'n_external_owners = 1',
        'pvalue_result = ' + ('PNULL' if name == 'populate' else 'PINT 7')]
    reached += common.reach('S_front', 'S_initial', 'GR_OUTER') + FRONT
    destination = 'first' if name == 'populate' else 'result'
    reached += ['$lookup(S_front.ENV,$ptascii(' + json.dumps(destination) + ')) = eps']
    reached += common.reach('S_get', 'S_call', 'GR_ENTER ppropertyget.METHOD') + common.ENTER
    if name == 'cleanup':
        # The saved-view guard in CLEANUP checks a control projection only.
        reached += common.reach('S_exit', 'S_get', 'GR_EXIT')
        reached += common.reach('S_inner', 'S_exit', 'GR_RECURSE') + INNER + common.CLEANUP
    else:
        reached += common.reach('S_inner', 'S_get', 'GR_RECURSE') + INNER + [
            'S_inner.CURRENT = (pcallcontext_get)', 'S_inner.FRAMES = [pframe_get]',
            '$property_get_recursive_frame(S_inner,pcallcontext_get,pframe_get,n_child,ptbytes_name)']
    reached += common.reach('S_invoke', 'S_invoke_pending', 'GR_INVOKE') + INVOKE
    reached += common.reach('S_handler', 'S_invoke', 'GR_HANDLER') + HANDLER
    reached += common.reach('S_resume', 'S_handler', 'GR_WARNING_RESULT') + common.RESUME
    reached += common.reach('S_result', 'S_read', 'GR_GET_RESULT') + common.RESULT
    reached += common.reach('S_copy', 'S_copy_pending', 'GR_GET_COPY') + common.COPY
    reached += common.reach('S_again', 'S_copied', 'GR_OUTER') + common.RESET
    reached += ['$lookup(S_again.ENV,$ptascii(' + json.dumps(destination) + ')) = (n_result_cell)',
        'S_again.STORE[n_result_cell] = DEFINED pvalue_result', 'S_end = S_again']
    reached += common.FINISH + [f'z_inner = {case["recursive_line"]}']
    derived = common.DERIVED + (POPULATED if name == 'populate' else common.CLEANUP_DERIVED)
    return reached, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_unset_recursion_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['populate', 'sole', 'throwing', 'cleanup']
    assert [case['id'] for case in data['controls']] == ['typed-initial', 'typed-unset', 'denied-private']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [case for case in data['cases'] if case['id'] in ('populate', 'cleanup')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(common.__file__), Path(recorder.__file__), catalogue, profile_file,
        php, adapter, bridge, worker, runner, compiler, manifest, *modules,
        *(HERE / case['source_file'] for case in data['cases'] + data['controls']),
        *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json',
            'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
            'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-get-unset-recursion-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
        'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [],
        'selection': [case['id'] for case in selected], 'application_invocations': 0,
        'application_evaluations': 0, 'source_agreements': 0, 'premises': 0,
        'reached_premises': 0, 'derived_premises': 0, 'cap_seconds': 90,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1},
        'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            source = HERE / case['source_file']
            assert sha(source) == case['source_sha256']
            raw = base64.b64decode(case['stdout_base64']) + b'\0' + base64.b64decode(case['stderr_base64']) + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(raw).hexdigest() == case['native_raw_sha256']
            directory = out / case['id']
            directory.mkdir()
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], directory / 'adapter')
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            reached, derived = conditions(case, checked)
            content = common.PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            content += ''.join('  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n' for condition in reached + derived)
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'declared-recursion.watsup'
            fixture.write_text(content)
            row = {'id': case['id'], 'path': str(fixture), 'sha256': sha(fixture),
                'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
            fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
            head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        if not args.prepare_only:
            report['passed'] = report['passed'] and len(report['records']) == 2 * len(selected) and all(row['passed'] for row in report['records']) and report['application_invocations'] == len(selected) and report['application_evaluations'] == len(selected)
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
