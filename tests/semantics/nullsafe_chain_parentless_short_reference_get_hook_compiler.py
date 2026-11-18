#!/usr/bin/env python3
"""Check reached nullsafe hook compilation errors before any body execution."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
STEM = 'nullsafe_chain_parentless_short_reference_get_hook'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
PREFIX = '''
var U : program
dec $ns337_kind(pcnode) : bool
def $ns337_kind(NExprNullsafePropertyFetch expression phpType20 metadata) = true
def $ns337_kind(pcnode) = false -- otherwise
dec $ns337_find(pcoccurrence*) : (pcpath, expression)?
def $ns337_find((PCOCCURRENCE pcpath (NExprNullsafePropertyFetch expression phpType20 metadata)) :: pcoccurrence*) = ((pcpath,NExprNullsafePropertyFetch expression phpType20 metadata))
def $ns337_find((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*) = $ns337_find(pcoccurrence*)
  -- if ~$ns337_kind(pcnode)
def $ns337_find(eps) = eps
'''


def fields(fixture, source, case):
    file = '$base64(' + quoted(str(source)) + ')'
    line = str(case['line'])
    hook = str(next(i + 1 for i, text in enumerate(source.read_text().splitlines()) if '&get' in text))
    error = 'STATICERROR "Cannot take reference of a nullsafe chain" ' + line
    return [
        'U = ' + fixture, 'P = $ppstart(337,U,' + file + ')',
        'P.FOLD.SOURCE = $pcsource(337,U)',
        '$ns337_find(P.FOLD.SOURCE.OCCURRENCES) = ((pcpath_body,expression_body))',
        'expression_body = NExprNullsafePropertyFetch expression_receiver phpType20_name metadata_body',
        '$(|pcpath_body| >= 3)',
        'pcpath_hook = pcpath_body[0:$nabs($( |pcpath_body| - 1))]',
        'pcpath_body = pcpath_hook ++ [PCFIELD 5]',
        '$origin_node([P.FOLD.SOURCE],PORIGIN 337 pcpath_hook) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) (NIdentifier (BYTES text_get) metadata_get) (SEQUENCE eps) expression_body metadata_hook)',
        '$base64(text_get) = $ptascii("get")', '$hook_parameter_facts(metadata_hook) = [false]',
        '$source_line(metadata_hook) = ' + hook,
        '$source_line(metadata_body) = ' + line, '$expression_line(expression_body) = ' + line,
        'P.LOCATION.FILE = ' + file,
        'P.COMPLETION = PPCABRUPT (' + error + ')',
        '$hook_short_reference_nullsafe_body(expression_body,$ptascii("v"))',
        '~$hook_short_reference_body(expression_body,$ptascii("v"))',
        '~$hook_short_reference_literal_this_body(expression_body,$ptascii("v"))',
        '$hook_body_backed(expression_body,$ptascii("v"))',
        '$ppreturn_variable(expression_body)', '$ppnullsafe(expression_body)',
        '$code_expression($compiled_operands(P,P.EXPRESSIONS),pcpath_body) = eps',
        '$arrow_line($compiled_operands(P,P.EXPRESSIONS),pcpath_body) = eps',
        'P.FUNCTIONS = eps',
        'S_zero = $php_run(U,0,' + quoted(str(source)) + ')',
        'S_one = $php_run(U,1,' + quoted(str(source)) + ')', 'S_zero = S_one',
        'S_zero.COMPLETION = ' + error,
        'S_zero.EVENTS = eps', 'S_zero.TODO = eps', 'S_zero.FUNCTIONS = eps',
        'S_zero.CURRENT = eps', 'S_zero.FRAMES = eps']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('weak', 'strict'), default='weak')
    parser.add_argument('--form', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    folder = Path(__file__).with_name(STEM + ('_review' if args.suite == 'strict' else ''))
    cases = json.loads((folder / 'cases.json').read_text()); assert args.form in cases
    source = folder / cases[args.form]['source']; out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(sys.argv[0]).resolve(), *folder.iterdir(), *modules,
             *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json',
             'frontend/worker.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
             'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    report = {'head':head, 'inputs':before, 'suite':args.suite, 'form':args.form,
              'scope':'compiler-static-error', 'mode':'fixture-SL', 'module_count':len(modules),
              'source_agreement_credit':0, 'native_observations':0, 'passed':False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, cases[args.form]); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
        (out / 'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',120)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)):sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['passed'], report.get('stderr','')[:3000]
    print('pass compiler',args.form,report['premises'])


if __name__ == '__main__':
    main()
