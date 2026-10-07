"""Genuine running-file scope and parked Fiber marker counterexamples."""
import base64
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from recorded_worker import Worker
import fiber_state_review as review

HELPERS = r'''
;; Reproduce the eval-only bridge on the same reached state; this is a
;; counterfactual admission predicate, not execution of an earlier revision.
dec $file_review_eval_only_vm_valid(pstate, pfibervm, nat?, pfibercaller*) : bool
def $file_review_eval_only_vm_valid(S, pfibervm, n?, pfibercaller*) = true
  -- if ~pfibervm.GLOBAL \/ (pfibervm.TABLE = $empty_table() /\ pfibervm.CURRENT = eps /\ pfibervm.FRAMES = eps /\ n? = eps)
  -- if $generator_flat_tasks(pfibervm.TODO) /\ $generator_flat_frames(pfibervm.FRAMES)
  -- if $generator_resume_ids(pfibervm.TODO) = eps /\ $generator_saved_ids(pfibervm.FRAMES) = eps
  -- if S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = n?][.FIBERCALLERS = pfibercaller*][.COMPLETION = NORMAL][.EVALCONTEXTS = eps]
  -- if $eval_tasks_markers_valid(S_view, S_view.TODO)
  -- if $eval_requests_owned(S_view.TODO)
  -- if $eval_frames_markers_valid(S_view, S_view.FRAMES)
  -- if $call_descriptors_scoped_valid(S, S_view)
def $file_review_eval_only_vm_valid(S, pfibervm, n?, pfibercaller*) = false -- otherwise
'''

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare():
    out = Path(tempfile.mkdtemp(prefix='fiber-core-file-review-', dir=ROOT / '.tools'))
    child = out / 'child.php'
    child.write_bytes(b'<?php echo "F";')
    source = out / 'source.php'
    source.write_text("<?php\nfunction parkedFileCaller313(){\n$f=new Fiber(static function(){include "
                      + json.dumps(str(child)) + ";});\n$f->start(); echo 'M';\n}\nparkedFileCaller313();\n")
    seq = lambda data: '(' + str(list(data)) + ')'
    b64 = lambda data: base64.b64encode(data).decode()
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
        parsed_child = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
            'profile': 'cli-raw-85', 'requested': b64(bytes(child)),
            'resolved': b64(bytes(child)), 'opened': b64(bytes(child)),
            'source': b64(child.read_bytes())})
        assert parsed['accepted'] and parsed_child['accepted']
        checked = [adapter.request({'op': 'check', 'ast': p['ast'], 'fixture': True})
                   for p in (parsed, parsed_child)]
        assert all(p['ok'] for p in checked)
    finally:
        frontend.close()
        adapter.close()
    (out / 'checked.json').write_text(json.dumps(checked) + '\n')
    clauses = [
        'S_open = $php_file_run(' + checked[0]['fixture'] + ', 4000, ' + seq(bytes(source))
            + ', ' + seq(bytes(ROOT)) + ')',
        'S_open.COMPLETION = SOURCE_PENDING',
        'S_open.FILECONTEXTS = pfilecontext_open :: eps',
        'pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext_open.REQUESTED = ' + seq(bytes(child)),
        'pfilecontext_open.CALLER = ' + seq(bytes(source)),
        'S_parse = $file_open_resume(S_open, FILE_OPENED pfilecontext_open.NONCE '
            + seq(bytes(source)) + ' ' + seq(bytes(child)) + ' ' + seq(bytes(child))
            + ' ' + seq(bytes(child)) + ' ' + seq(child.read_bytes()) + ')',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
        'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
        'pfilecontext_parse.UNIT = (n_unit)',
        'S = $file_parse_resume(S_parse, SOURCE_ACCEPT n_unit '
            + seq(child.read_bytes()) + ' ' + checked[1]['fixture'] + ')',
        'S.COMPLETION = NORMAL', 'S.FILECONTEXTS = pfilecontext_run :: eps',
        'pfilecontext_run.PHASE = FILE_UNIT_RUN', 'pfilecontext_run.UNIT = (n_unit)',
        'S.FIBERCALLERS = pfibercaller :: pfibercaller_tail*',
        'pfibercaller_tail* = eps', 'pfibervm = pfibercaller.VM', '~pfibervm.GLOBAL',
        'pfibervm.FRAMES = pframe :: pframe_tail*', 'pframe_tail* = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$fiber_vm_valid(S, pfibervm, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        '$file_review_eval_only_vm_valid(S, pfibervm, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        'S_old_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = pfibercaller.PREVIOUS][.FIBERCALLERS = pfibercaller_tail*][.COMPLETION = NORMAL]',
        '~$eval_state_valid(S_old_view)',
        'pfibervm.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_wait_tail*',
        'pfibervm_direct = pfibervm[.TODO = (FIBER_WAIT pfibercaller.API) :: (FILE_END n_unit) :: ptask_wait_tail*]',
        '$file_review_eval_only_vm_valid(S, pfibervm_direct, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        '~$fiber_vm_valid(S, pfibervm_direct, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        'S_direct = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_direct]]]',
        '$heap_graph(S_direct) = $heap_graph(S)', '~$call_descriptors_valid(S_direct)',
        'pfibervm_frame = pfibervm[.FRAMES = [pframe[.TODO = (FILE_END n_unit) :: pframe.TODO]]]',
        '$file_review_eval_only_vm_valid(S, pfibervm_frame, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        '~$fiber_vm_valid(S, pfibervm_frame, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        'S_frame = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_frame]]]',
        '$heap_graph(S_frame) = $heap_graph(S)', '~$call_descriptors_valid(S_frame)',
        'pfibervm_hidden = pfibervm[.TODO = (CHOOSE ([FILE_END n_unit]) eps 1) :: pfibervm.TODO]',
        '~$file_review_eval_only_vm_valid(S, pfibervm_hidden, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        '~$fiber_vm_valid(S, pfibervm_hidden, pfibercaller.PREVIOUS, pfibercaller_tail*)',
        'S_hidden = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_hidden]]]',
        '$heap_graph(S_hidden) = $heap_graph(S)', '~$call_descriptors_valid(S_hidden)',
    ]
    fixture = out / 'test.watsup'
    fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + clause + '\n' for clause in clauses))
    watched = [Path(__file__), fixture, source, child, ROOT / 'spec/semantics/modules.json',
        *(ROOT / ('spec/semantics/' + name) for name in ['84-call-integrity.watsup',
          '281-fibers.watsup', '160-eval-runtime.watsup', '171-include-runtime.watsup']),
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / '.tools/php/bin/php', ROOT / '_build/default/adapter/main.exe']
    report = {'mode': 'prepared genuine file protocol; no model execution', 'assertions': len(clauses),
        'inputs': {str(path.relative_to(ROOT)): digest(path) for path in watched},
        'source': str(source), 'fixture': str(fixture), 'passed': False,
        'counterfactual': 'Exact eval-only VM admission on repaired live state; no older source agreement.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, flush=True)
    return out

def run(out):
    report = json.loads((out / 'report.json').read_text())
    paths = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    assert all(digest(ROOT / name) == value for name, value in report['inputs'].items()), 'prepared inputs changed'
    report['revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    report['process'] = review.recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        '--sl', *paths, out / 'test.watsup'], out, 'model', env, 120)
    assert all(digest(ROOT / name) == value for name, value in report['inputs'].items()), 'inputs changed during run'
    report['passed'] = (not report['process']['timeout'] and report['process']['exit'] == 0
        and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes())
    report['mode'] = 'SL120, jobs1; genuine active-file and parked marker admission'
    report['compiler'] = {'spectec_source_commit': 'da36ac3c434cd291940293a63da64544307730a3',
                          'ocaml_switch': '5.1.0', 'semantic_mode': 'SL'}
    report['runtime'] = {'version': '8.5.10', 'source_commit': '34308a6666b2d489c509541ea9befea9e2b42348'}
    report['environment'] = {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True, 'jobs': 1}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['passed'], report['assertions'], flush=True)
    return report['passed']

def source_gate(out):
    source, child = out / 'source.php', out / 'child.php'
    b64 = lambda value: base64.b64encode(value).decode()
    snapshot = {'version': 1, 'main': b64(bytes(source)), 'cwd': b64(bytes(out)),
        'include_path': b64(b'.:'), 'entries': [{'caller': b64(bytes(source)),
        'requested': b64(bytes(child)), 'status': 'opened', 'resolved': b64(bytes(child)),
        'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
    snapshot_file = out / 'source-snapshot.json'
    snapshot_file.write_text(json.dumps(snapshot, indent=2) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    watched = [Path(__file__), source, child, snapshot_file, ROOT / 'bin/php-semantics',
        ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/84-call-integrity.watsup',
        ROOT / 'spec/semantics/281-fibers.watsup', ROOT / '.tools/php/bin/php',
        ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/profile.json']
    inputs = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    native = review.recorded([ROOT / '.tools/php/bin/php', '-n', *flags, source], out,
                             'source-native', env, 75)
    native_ok = (native['exit'] == 0 and not native['timeout']
        and (out / 'source-native.stdout').read_bytes() == b'FM'
        and not (out / 'source-native.stderr').read_bytes())
    model = None
    observation = None
    if native_ok:
        model = review.recorded([ROOT / 'bin/php-semantics', source, '--steps', '100000',
            '--timeout', '60', '--file-snapshot', snapshot_file], out, 'source-model', env, 75)
        if not model['timeout'] and model['exit'] == 0:
            observation = json.loads((out / 'source-model.stdout').read_bytes())
    passed = (native_ok and model is not None and not model['timeout'] and model['exit'] == 0
        and not (out / 'source-model.stderr').read_bytes() and observation['status'] == 'normal'
        and observation['stdout'] == b64(b'FM') and observation['stderr'] == ''
        and observation['exit_status'] == 0)
    assert inputs == {str(path.relative_to(ROOT)): digest(path) for path in watched}, 'source gate inputs changed'
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256': digest(source), 'mode': 'exact native/model source with real finite file facts',
        'inputs': inputs, 'native': native, 'model': model, 'observation': observation,
        'passed': passed, 'normal_agreements': int(passed),
        'budgets': {'steps': 100000, 'model_seconds': 60, 'process_seconds': 75, 'jobs': 1},
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
        'profile': profile, 'runtime': {'version': '8.5.10',
        'source_commit': '34308a6666b2d489c509541ea9befea9e2b42348'},
        'compiler': {'mode': 'SL', 'spectec_commit': 'da36ac3c434cd291940293a63da64544307730a3'}}
    (out / 'source-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'source', passed, flush=True)
    return passed

if __name__ == '__main__':
    out = prepare()
    raise SystemExit(0 if run(out) and source_gate(out) else 1)
