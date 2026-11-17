#!/usr/bin/env python3
"""Ground nullable declaration-scoped FORMAL authority at an actual NULL Notice frontier."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_plain_nullable_stdclass_formal_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_nullable_stdclass_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX


def normal(initial, case, front):
    original, inherited = prior.normal(initial, case, front)
    canonical = prior.prior.nullable('stdClass')
    class_only = prior.prior.class_type('stdClass')
    reached = []
    for line in original:
        line = line.replace(prior.prior.nullable('sTdClAsS'), canonical)
        if line.startswith('$base64(text_formal) = '):
            line = '$base64(text_formal) = $ptascii("stdClass")'
        elif line.startswith('pfunction_producer.ENV.NAMESPACE = '):
            line = r'pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = [($ptascii("spare"), $ptascii("stdClass"))]'
        reached.append(line)
    context = '$pltypecontext(pfunction_producer.ENV, PTGLOBAL, PTPARAMETER, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 })'
    reached += ['$ptvalidname($base64(text_formal), true)',
        '$ptsingle(' + context + ', PTPLAIN, $base64(text_formal)) = PTOK (' + class_only + ') eps',
        '$ptnullable(' + context + ', PTOK (' + class_only + ') eps) = PTOK (' + canonical + ') eps']
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith(('~$error_call_valid(', '~$typed_return_task_valid(', 'S_zero_', '$drive($drive(S_zero_', '$typed_conversion_at('))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    view = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    env = 'pfunction_producer.ENV'
    helper = lambda context, raw: '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + raw + ')'
    scoped = '$reference_notice_producer_scoped_header(' + env + ', SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    proof = lambda raw: scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + raw + ']),', 1)
    typed = lambda signature: scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = ' + signature + ']]])')
    derived += [helper(env, 'phpType17') + ' = (' + view + ')', helper(env, view) + ' = (' + view + ')', proof(view),
        '$reference_notice_producer_global_parameter_view(phpType17) = (' + view + ')',
        scoped.replace(env + ',', env + '[.CLASSES = eps],', 1),
        '~' + scoped.replace(env + ',', env + '[.NAMESPACE = $ptascii("Other")],', 1),
        scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        '~' + scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([phpType17, phpType17]),', 1)]
    for signature in ('eps', class_only, prior.prior.nullable('Other'), prior.prior.nullable('STDCLASS'),
            prior.prior.prior.branches(['object', 'null']), prior.prior.prior.branches(['null']),
            '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTCLASS ($ptascii("stdClass"))]))]',
            canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]', canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'):
        derived.append('~' + typed(signature))
    for alias in ('Spare', 'sPaRe', 'SPARE'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(alias.encode()).decode()), 1)
        derived += [helper(env, raw) + ' = (' + view + ')', proof(raw)]
    for tag in ('NNameRelative', 'NIdentifier'):
        raw = parameter.replace('NName (BYTES text_formal)', tag + ' (BYTES text_formal)', 1)
        derived += [helper(env, raw) + ' = (' + raw + ')', '~' + proof(raw)]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()), 1)
        derived += [helper(env, raw) + ' = (' + raw + ')', '~' + proof(raw)]
    for name in ('int', 'mixed', 'self', 'array', 'callable'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()), 1)
        fake = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        derived += [helper(fake, raw) + ' = (' + raw + ')', '~' + proof(raw).replace(env + ',', fake + ',', 1)]
    for target in ('Other', 'STDCLASS', 'StDcLaSs'):
        fake = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(target) + '))]]'
        derived += [helper(fake, 'phpType17') + ' = phpType17', '~' + scoped.replace(env + ',', fake + ',', 1)]
    wrapper = 'NNullableType (NName (BYTES text_formal) metadata_formal) metadata_formalnullable'
    union = 'NUnionType (SEQUENCE ([NName (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_formalnullable'
    raw = parameter.replace(wrapper, union, 1)
    derived += [helper(env, raw) + ' = (' + raw + ')', '~' + proof(raw)]
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN false)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN false) (BOOLEAN true)'),
            (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
            ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        raw = parameter.replace(before, after, 1)
        derived += [helper(env, raw) + ' = (' + view.replace(before, after, 1) + ')', '~' + proof(raw)]
    for before, after in (('metadata_formalnullable', 'eps'), ('metadata_formal)', 'eps)'), ('metadata_parameter', 'eps')):
        derived.append(helper(env, parameter.replace(before, after)) + ' = (' + view.replace(before, after) + ')')
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged scoped nullable formal default"'):
        derived.append('~' + scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]])'))
    return reached, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    for case in cases:
        row = rows[case['id']]
        source = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
        paths += [source, Path(row['stdout']), Path(row['stderr'])]
    source = Path(rows[cases[0]['id']]['command'][-1])
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
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
    reached, derived = normal(initial, cases[0], args.front)
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[cases[0]['id']], unchanged_reception_controls=[cases[1]['id']], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('scoped-nullable-stdclass-formal-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
