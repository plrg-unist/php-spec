#!/usr/bin/env python3
"""Reached once-skip helper ownership and pending exception authority, reviewed42.

--prepare-only constructs checked source/file fixtures without model applications.
The ordinary file provider supplies paths and bytes, not execution answers.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HELPERS = '\ndec $helper_pending_review_seek(pstate, nat) : pstate\ndef $helper_pending_review_seek(S, n) = S -- if S.SOURCEPENDING =/= eps\ndef $helper_pending_review_seek(S, n) = S\n  -- if S.SOURCEPENDING = eps\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $helper_pending_review_seek(S, 0) = S -- if S.SOURCEPENDING = eps\ndef $helper_pending_review_seek(S, n) = $helper_pending_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if S.SOURCEPENDING = eps\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n'
PREMISES = ['',
 '  -- if S_open.COMPLETION = SOURCE_PENDING',
 '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
 '',
 '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
 '  -- if pfilecontext_parse.UNIT = (n_unit)',
 '',
 '  -- if S_seed.COMPLETION = SOURCE_PENDING',
 '  -- if S_seed.FILECONTEXTS = pfilecontext_skip :: eps',
 '  -- if pfilecontext_skip.PHASE = FILE_RESOLVE_WAIT',
 '',
 '  -- if S_reached = $helper_pending_review_seek(S_done, 2500)',
 '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
 '  -- if S = S_reached[.COMPLETION = NORMAL]',
 '  -- if S.SOURCEPENDING = (psourcepending)',
 '  -- if psourceoperand = psourcepending.OPERAND',
 '  -- if psourcepending.HELPER = (HELPER_ONCE_SKIP pfilecontext_saved n_path*)',
 '  -- if psourceoperand.INPUT = KNOWN (POBJECT n_input)',
 '  -- if psourceoperand.KIND = 2',
 '  -- if psourceoperand.OWNER = 0',
 '  -- if S.TODO = (SOURCE_HELPER_FINISH psourceoperand (HELPER_ONCE_SKIP pfilecontext_saved n_path*)) :: '
 'psourceoperand.TAIL',
 '  -- if n_outside = |S.OBJECTS|',
 '  -- if $source_pending_record_valid(S, psourcepending)',
 '  -- if $source_pending_state_valid(S)',
 '  -- if $call_descriptors_valid(S)',
 '  -- if $call_entry_check(S) = S',
 '  -- if $heap_valid($heap_graph(S))',
 '  -- if S.RESULT = KNOWN (PBOOL true)',
 '  -- if $task_nodes(SOURCE_HELPER_FINISH psourceoperand (HELPER_ONCE_SKIP pfilecontext_saved n_path*)) = eps',
 '  -- if $source_pending_roots((psourcepending)) = [HOBJECT psourcepending.EXCEPTION]',
 '  -- if ~((HOBJECT n_input) <- S.ALLOCATIONS)',
 '  -- if ~((HOBJECT n_input) <- $machine_roots(S))',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.UNIT = 1])',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.HELPER = eps])',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.HELPER = (HELPER_EMPTY_EVAL)])',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.HELPER = (HELPER_ONCE_SKIP '
 'pfilecontext_saved[.NONCE = S.FILESEQ] n_path*)])',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.HELPER = (HELPER_ONCE_SKIP '
 'pfilecontext_saved[.PHASE = FILE_PARSE_WAIT] n_path*)])',
 '  -- if ~$source_pending_record_valid(S[.INCLUDEDOPENED = eps], psourcepending)',
 '',
 '',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.OPERAND = psourceoperand[.OWNER = 1]])',
 '  -- if ~$source_pending_record_valid(S, psourcepending[.EXCEPTION = n_outside])']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--semantic-root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    semantic = args.semantic_root.resolve()
    sys.path.insert(0, str(ROOT / 'tests/semantics'))
    import error_handler_run as recorder
    from recorded_worker import Worker
    recorder.ROOT = ROOT
    directory = ROOT / 'tests/semantics/source-stringable-helpers'
    source = directory / 'once-skip.php'
    child = directory / 'helper-skip-body.php'
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = dict(json.loads(profile_file.read_bytes()), include_path='.:', error_reporting='30719')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    php = ROOT / '.tools/php/bin/php'
    bridge = ROOT / '.tools/php-file.so'
    adapter = ROOT / '_build/default/adapter/main.exe'
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    worker = ROOT / 'frontend/worker.php'
    b64 = lambda value: base64.b64encode(value).decode()
    seq = lambda value: '(' + str(list(value)) + ')'
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    watched = [source, child, Path(__file__), profile_file, php, bridge, adapter, worker,
               ROOT / 'frontend/target.php', ROOT / 'spec/schema.json',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py']
    modules = []
    if not args.prepare_only:
        manifest = semantic / 'spec/semantics/modules.json'
        modules = [semantic / name for name in json.loads(manifest.read_bytes())]
        assert any(path.name == '298-source-stringable-lifetime.watsup' for path in modules)
        watched += [manifest, *modules, runner]
    snapshot = lambda: {str(path): sha(path) for path in watched}
    before = snapshot()
    def git(*parts):
        result = subprocess.run(['git', *parts], cwd=ROOT, env=recorder.ENV,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip() if result.returncode == 0 else None
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    out = Path(tempfile.mkdtemp(prefix='source-stringable-helper-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'working_tree_status': status, 'inputs': before,
              'profile': profile, 'source': str(source), 'child': str(child), 'semantic_root': str(semantic),
              'mode': 'SL', 'cache': False, 'det': True,
              'compiler_pin': 'da36ac3c434cd291940293a63da64544307730a3',
              'selected': 'first genuine no-unit once-skip pending record after captured operand retirement and before caller assignment',
              'binding_premises': 22, 'selected_admission_premises': 42, 'check_premises': 20,
              'source_agreements': 0, 'application_evaluations': 0, 'passed': False,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        try:
            parsed = [frontend.request({'op': 'parse', 'source': b64(source.read_bytes())}),
                      frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file', 'profile': 'cli-raw-85',
                                        'requested': b64(bytes(child)), 'resolved': b64(bytes(child)),
                                        'opened': b64(bytes(child)), 'source': b64(child.read_bytes())})]
            assert all(row['accepted'] for row in parsed)
        finally:
            frontend.close()
        checked_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
        try:
            checked = [checked_worker.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for row in parsed]
            assert all(row['ok'] for row in checked)
        finally:
            checked_worker.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        start = ('$php_file_startup_run($helper_pending_review_program(), 10000, $base64('
                 + json.dumps(b64(bytes(source))) + '), $base64(' + json.dumps(b64(bytes(ROOT)))
                 + '), {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})')
        opened = lambda context: ('(FILE_OPENED ' + context + '.NONCE ' + seq(bytes(source)) + ' '
                                  + seq(bytes(child)) + ' ' + seq(bytes(child)) + ' ' + seq(bytes(child))
                                  + ' ' + seq(child.read_bytes()) + ')')
        accepted = '(SOURCE_ACCEPT n_unit ' + seq(child.read_bytes()) + ' $helper_pending_review_child())'
        missing = '$base64(' + json.dumps(b64(bytes(directory / '__helper_never_opened__.php'))) + ')'
        premises = list(PREMISES)
        premises[0] = '  -- if S_open = ' + start
        premises[3] = '  -- if S_parse = $file_open_resume(S_open, ' + opened('pfilecontext_open') + ')'
        premises[6] = '  -- if S_seed = $file_parse_continue(S_parse, ' + accepted + ')'
        premises[10] = '  -- if S_done = $file_open_resume(S_seed, ' + opened('pfilecontext_skip') + ')'
        premises[38] = '  -- if ~(' + missing + ' <- S.INCLUDEDOPENED)'
        premises[39] = '  -- if ~$source_pending_record_valid(S, psourcepending[.HELPER = (HELPER_ONCE_SKIP pfilecontext_saved ' + missing + ')])'
        fixture = ('dec $helper_pending_review_program() : program\ndef $helper_pending_review_program() = '
                   + checked[0]['fixture'] + '\ndec $helper_pending_review_child() : program\ndef $helper_pending_review_child() = '
                   + checked[1]['fixture'] + '\n' + HELPERS)
        fixture += '\ndec $main() : bool\ndef $main() = true\n' + '\n'.join(premises) + '\ndef $main() = false -- otherwise\n'
        test = out / 'admission.watsup'
        test.write_text(fixture)
        report.update(frontend_accepted=True, adapter_ok=True, fixture_sha256=sha(test))
        if args.prepare_only:
            report['passed'] = True
        else:
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(test)], out / 'admission', 90)
            report['application_evaluations'] = 1
            stdout = (out / 'admission.stdout').read_bytes()
            stderr = (out / 'admission.stderr').read_bytes()
            report.update(process=process, observed=stdout.decode(errors='replace'), stderr=stderr.decode(errors='replace'))
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not stderr
                                and not process['group_after'] and stdout == b'true\n')
    finally:
        report['inputs_stable'] = before == snapshot()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        report['status_stable'] = status == git('status', '--short')
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return all(report[key] for key in ('passed', 'inputs_stable', 'head_stable', 'status_stable'))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
