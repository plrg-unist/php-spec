#!/usr/bin/env python3
"""Ground weak FLOAT reception/return before named private Notice-cell writes."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_builtin_fqn_stdclass_producer_reference_notice_review_state as previous
import global_plain_union_int_stdclass_return_producer_reference_notice_review_state as retained
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_union_float_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = retained.PREFIX.replace('KNOWN (PINT 17)', 'KNOWN (PFLOAT 4625478292286210048)').replace('KNOWN (PINT 37)', 'KNOWN (PFLOAT 4630404104378646528)')


def normal(initial, case, index, front):
    old, _ = previous.normal(initial, case, index, True)
    reached = old[:old.index('S_checked = $typed_return_value(S_return, z_return)')]
    reached = [line.replace('NNameFullyQualified', 'NName') if line.startswith('phpType18_return = ') else line for line in reached]
    reached += ['$base64(text_first_class) = $ptascii("sTdClAsS")',
        '$base64(text_last_class) = $ptascii("sTdClAsS")', '$base64(text_return_class) = $ptascii("stdClass")',
        '~pfunction_producer.CODE.STRICT', 'pfunction_producer.ENV.NAMESPACE = eps', 'pfunction_producer.ENV.CLASSES = eps']
    if index == 0:
        reached += ['pvalue_original = PINT 17',
            'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
            'pvalue_saved = PFLOAT 4625478292286210048', 'pvalue_received_last = PBOOL false',
            '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEVALUE (PFLOAT 4625478292286210048)',
            '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEBOOL pvalue_y_original',
            '$mcsf_output(S_return.EVENTS) = $ptascii("I;M:1:1:1:1;")']
    else:
        scalar = previous.prior.front_lines(index, case)
        first_value = next(i for i, line in enumerate(scalar) if line.startswith('pvalue_original = '))
        reached += [line.replace('S_pre', 'S_return') for line in scalar[first_value:]]
    reached += ['$origin_node(S_args.SOURCES, porigin_producer_call) = (NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call)',
        'phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg',
        'phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg',
        '$reference_cv(expression_first) = ($ptascii("x"))', '$reference_cv(expression_last) = ($ptascii("y"))']
    result = '(PFLOAT ' + str(case['value_bits']) + ')'
    reached += ['S_return.RESULT = VARIABLE ($ptascii("saved")) 4',
        '$resolve_at(S_return, S_return.RESULT, z_return) = S_return[.RESULT = KNOWN pvalue_saved]',
        '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_saved, false) = TYPEVALUE ' + result,
        '$typed_return_value(S_return, z_return) = S_return[.RESULT = KNOWN ' + result + ']']
    actuals = 'SEQUENCE ([phpType7_first, phpType7_last])'
    parameters = 'SEQUENCE ([phpType17_first, phpType17_last])'
    header = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, ' + actuals + ', ' + parameters + ', '
    reached += ['~$reference_notice_producer_header(' + actuals + ', ' + parameters + ', phpType18_return, pfunction_producer.SIGNATURE)',
        ('~' if front else '') + header + 'phpType18_return, pfunction_producer.SIGNATURE)']
    if front:
        return reached, []
    reached += ['S_pre = $mcsf_seek(S_return, 8, 5000)[.COMPLETION = NORMAL]', '$mcsf_ready(S_pre, 8)',
        'S_pre.RESULT = KNOWN ' + result, '~((HCELL n_saved) <- S_pre.ALLOCATIONS)',
        '$named_reference_notice_pending(S_pre)', 'n_private = |S_pre.STORE|',
        'S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.LINE = 9 /\\ perrorcall.LEVEL = 8', '$error_call_valid(S_notice, perrorcall)',
        'S_notice.STORE[n_private] = DEFINED ' + result,
        'n_private =/= n_original_x /\\ n_private =/= n_y /\\ n_private =/= n_saved',
        '$node_children(S_notice, HCELL n_private) = eps', '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        '$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps', '$propref_at(S_notice.PROPREFS, n_private) = eps',
        '$reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps',
        'S_resume = $mcsf_seek(S_notice, 9, 7000)[.COMPLETION = NORMAL]', '$mcsf_ready(S_resume, 9)',
        '$lookup(S_resume.ENV, $ptascii("x")) = (n_new_x)',
        'n_new_x =/= n_original_x /\\ n_new_x =/= n_private /\\ n_new_x =/= n_y',
        'S_resume.STORE[n_new_x] = DEFINED (PINT 37)', 'S_resume.STORE[n_y] = DEFINED (PINT 29)',
        'S_resume.STORE[n_private] = DEFINED ' + result]
    full = previous.prior.full_lines(index, case)
    reached += [line for line in full[full.index('S_written = $mcsf_seek(S_resume, 6, 9000)[.COMPLETION = NORMAL]'):] if line != '$string_carrier_valid(S_full, pvalue_original)']
    derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 10])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for name in ('stdClass', 'STDCLASS', 'sTdClAsS'):
        encoded_name = json.dumps(base64.b64encode(name.encode()).decode())
        for first in (False, True):
            for kind in ('int', 'null', 'float', 'bool', 'string', 'array', 'object', 'false', 'true', 'iterable', 'callable'):
                raw = previous.raw_union(json.dumps(base64.b64encode(kind.upper().encode()).decode()), 'return', first, 'NName', class_text=encoded_name)
                signature = 'pfunction_producer.SIGNATURE[.RETURNS = ' + previous.ordered(kind, first, name) + ']'
                proof = header + raw + ', ' + signature + ')'
                derived += [('' if kind in ('int', 'null', 'float', 'bool', 'string', 'array', 'false', 'true', 'iterable', 'callable') else '~') + proof]
                if kind in ('int', 'null', 'float', 'bool', 'string', 'array', 'false', 'true', 'iterable', 'callable'):
                    derived += ['~' + proof.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
                        '~' + proof.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
                        '~' + proof.replace(previous.ordered(kind, first, name), previous.ordered(kind, not first, name)),
                        proof.replace(actuals + ',', 'SEQUENCE eps,', 1)]
    raw_parameter = next(line.removeprefix('phpType17_first = ') for line in reached if line.startswith('phpType17_first = '))
    derived += ['~' + (header + 'phpType18_return, pfunction_producer.SIGNATURE)').replace(parameters + ',', 'SEQUENCE ([' + raw_parameter.replace('NNameFullyQualified', 'NName') + ', phpType17_last]),', 1),
        'S_zero = $drive(S_notice, 0)', 'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S_notice',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(previous.__file__), Path(previous.prior.__file__), Path(retained.__file__), CATALOGUE, provenance]
    specs, reached, derived = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            conditions, extra = normal(initial, case, index, args.front)
            specs.append('dec $gpic_case' + str(index) + '() : bool\ndef $gpic_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
            reached += conditions
            derived += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $gpic_case0()\n  -- if $gpic_case1()\n')
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-union-float-stdclass-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
