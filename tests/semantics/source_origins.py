#!/usr/bin/env python3
"""Checked task occurrence traces; no compiled facts or literal pools consumed."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/semantics'))
import static_types as types
import source_occurrences as occurrences

PREFIX = r'''
syntax ptracevisit = PTRACE text porigin
syntax ptrace = { FINAL pstate, VALID bool, VISITS ptracevisit* }
var T : ptrace
var U : pcunit
dec $trace_task(ptask) : (text, pcnode)?
def $trace_task(STMT statement) = (("STMT", statement))
def $trace_task(EVAL expression) = (("EVAL", expression))
def $trace_task(ACQUIRE expression) = (("ACQUIRE", expression))
def $trace_task(DIM_PREP expression) = (("DIM_PREP", expression))
def $trace_task(UNSET expression) = (("UNSET", expression))
def $trace_task(ARRAY_NEXT n ((NArrayItem phpType5 expression (BOOLEAN b_ref) (BOOLEAN b_unpack) metadata) :: phpType13*)) = (("ARRAY_NEXT", NArrayItem phpType5 expression (BOOLEAN b_ref) (BOOLEAN b_unpack) metadata))
def $trace_task(ptask) = eps -- otherwise

dec $trace_current(pstate, pcunit) : (bool, ptracevisit*)
def $trace_current(S, U) = (true, eps)
  -- if S.TODO = ptask :: ptask_tail*
  -- if $trace_task(ptask) = eps
def $trace_current(S, U) = (true, [PTRACE text (PORIGIN n pcpath)])
  -- if S.TODO = ptask :: ptask_tail*
  -- if $trace_task(ptask) = ((text, pcnode))
  -- if S.ORIGIN = (PORIGIN n pcpath)
  -- if n = U.ID
  -- if (PCOCCURRENCE pcpath pcnode) <- U.OCCURRENCES
def $trace_current(S, U) = (false, eps) -- otherwise

dec $trace_origins(pstate, pcunit, nat) : ptrace
def $trace_origins(S, U, n) = {FINAL $drive(S, n), VALID true, VISITS eps}
  -- if S.COMPLETION =/= NORMAL
def $trace_origins(S, U, n) = {FINAL S, VALID true, VISITS eps}
  -- if S.COMPLETION = NORMAL -- if S.TODO = eps
def $trace_origins(S, U, 0) = {FINAL $drive(S, 0), VALID true, VISITS eps}
  -- if S.COMPLETION = NORMAL -- if S.TODO = ptask :: ptask_tail*
def $trace_origins(S, U, n) = T[.VALID = (b /\ T.VALID)][.VISITS = ptracevisit* ++ T.VISITS]
  -- if $(n > 0) -- if S.COMPLETION = NORMAL -- if S.TODO = ptask :: ptask_tail*
  -- if (b, ptracevisit*) = $trace_current(S, U)
  -- PhpStep: S ~> S_next
  -- if n_next = $(n - 1)
  -- if T = $trace_origins($prune_allocations(S_next), U, n_next)

dec $trace_kind(ptracevisit*, text) : porigin*
def $trace_kind(eps, text) = eps
def $trace_kind((PTRACE text porigin) :: ptracevisit*, text) = porigin :: $trace_kind(ptracevisit*, text)
def $trace_kind((PTRACE text_other porigin) :: ptracevisit*, text) = $trace_kind(ptracevisit*, text)
  -- if text_other =/= text
'''

CASES = [
    b'<?php $a=1;echo $a+$a;',
    b'<?php $a=[1,1];',
    b'<?php $a=[[1],[1]];echo $a[0][0]+$a[1][0];',
    b'<?php $a=[1=>[2,3],2=>[4]];$a[1][0]=9;unset($a[2][0]);',
    b'<?php $n="a";$$n=[1];$$n[0]=2;echo ${$n}[0];',
    b'<?php $a=[1];$b=[2];$a[0]=&$b[0];echo $a[0];',
    b'<?php $a=[1];$b=&$a[];',
    b'<?php $n="x";$k=0;$a=[$k=>&$$n,&$x];',
    b'<?php ${"x"}=1;${1.5}=2;echo ${"x"}+${1.5};',
    b'<?php $a=1;$b=2;${($n="x")}=&$a;echo ($z=&$a)+($a=&$b);',
    b'<?php $a=[];$a[$a]=&$a;',
    b'<?php echo $missing+($a=2);',
    b'<?php echo []+[1];',
    b'<?php echo "bad"+1;',
    b'<?php echo 1/0;',
    b'<?php {echo 1;{echo 2;}}',
    b'<?php $a=[];$a[($k="x")]=[1];unset($a[$k]);',
    b'<?php $a=[];$b=[];$x=&$a[($a=&$b)[0]];',
    b'<?php $a=[1];$n="a";unset($$n[0]);',
    b'<?php $a=[1];$n="a";unset($$n);',
    b'<?php $a=[1];$b=[2];$a[($a=&$b)[0]-2]=3;',
    b'<?php $a=[1];$a[0]=&${($n="x")};',
    b'<?php $a=[];${($n="x")}=&$a[];',
    b'<?php echo [];',
    b'\xff\xfe' + '<?php $a=[1,1];echo $a[0];'.encode('utf-16le'),
]


def same_metadata(node):
    if isinstance(node, list):
        for item in node: same_metadata(item)
    elif isinstance(node, dict) and 'node' in node:
        node['meta'] = {'startLine': {'int': '1'}, 'endLine': {'int': '1'}}
        for field in node['fields']: same_metadata(field)


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(ROOT/'tests/semantics'), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    def fingerprint():
        return {'closure': types.syntax_validation.implementation_fingerprint(), 'runner': hashlib.sha256(runner.read_bytes()).hexdigest()}
    before = fingerprint()
    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')])
    adapter = types.Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)])
    fixtures, records = [], []
    try:
        for i, source in enumerate(CASES):
            encoding_profile = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'} if source.startswith(b'\xff\xfe') else {}
            if encoding_profile:
                flags = [x for key, val in encoding_profile.items() for x in ['-d', key+'='+val]]
                encoded_frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, *flags, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')])
                try: parsed = encoded_frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
                finally: encoded_frontend.close()
            else:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert 'ast' in checked, checked
            ast = checked['ast']
            if i < 2:
                ast = copy.deepcopy(ast);same_metadata(ast['program'])
                checked = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})
                assert 'ast' in checked, checked
                ast = checked['ast']
            expected = []
            for j, node in enumerate(ast['program']): expected.extend(occurrences.expected(node, [('INDEX', j)]))
            unit = i + 71
            program = checked['fixture']
            uterm = '{ID '+str(unit)+', AST '+program+', OCCURRENCES '+occurrences.occurrence_term(expected)+'}'
            initial = '$initial_state(NORMAL)[.SOURCES = [U]][.TODO = $statement_tasks($pcprogram(U.AST), (PORIGIN U.ID eps), 0)]'
            checks = [f'U = {uterm}', f'U = $pcsource({unit}, {program})', f'S = {initial}',
                'T = $trace_origins(S, U, 10000)', 'T.VALID', 'T.FINAL = $run_source(U, 10000)',
                'T.FINAL.ORIGIN = eps', 'T.FINAL.SOURCES = [U]', 'T.FINAL.COMPLETION =/= BUDGET', 'T.VISITS =/= eps']
            orders = None
            if i == 0:
                orders = [[('INDEX',0),('FIELD',0)], [('INDEX',0),('FIELD',0),('FIELD',1)],
                    [('INDEX',1),('FIELD',0),('INDEX',0)], [('INDEX',1),('FIELD',0),('INDEX',0),('FIELD',0)],
                    [('INDEX',1),('FIELD',0),('INDEX',0),('FIELD',1)]]
            elif i == 1:
                orders = [[('INDEX',0),('FIELD',0)], [('INDEX',0),('FIELD',0),('FIELD',1)],
                    [('INDEX',0),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1)],
                    [('INDEX',0),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',1),('FIELD',1)]]
            if orders:
                checks.append('$trace_kind(T.VISITS, "EVAL") = ['+', '.join('(PORIGIN '+str(unit)+' '+occurrences.path_term(path)+')' for path in orders)+']')
            if i in (2,5,9):
                for budget in (1,2,3,7,17):
                    checks += [f'S_budget{budget} = $drive(S, {budget})', f'S_budget{budget}.COMPLETION = BUDGET',
                        f'S_budget{budget}.SOURCES = [U]', f'$drive(S_budget{budget}[.COMPLETION = NORMAL], 10000) = T.FINAL']
            if encoding_profile:
                assert 'ENCODEDPROGRAM' in program
                checks += [f'S_encoded = $php_run({program}, 0)', 'S_encoded.COMPLETION = BUDGET',
                    'S_encoded.SOURCES[0].AST = U.AST', 'S_encoded.SOURCES[0].ID = 0',
                    '$drive(S_encoded[.COMPLETION = NORMAL], 10000).EVENTS = T.FINAL.EVENTS']
            if i == 0:
                stmt = occurrences.node_term(ast['program'][0])
                for origin in (f'PORIGIN {unit+1000} ([PCINDEX 0])', f'PORIGIN {unit} ([PCINDEX 999])', f'PORIGIN {unit} ([PCINDEX 1])'):
                    checks += [f'S_bad = $drive(S[.TODO = [AT ({origin}) (STMT {stmt})]], 100)',
                        'S_bad.COMPLETION = UNSUPPORTED "invalid task source occurrence"', 'S_bad.ORIGIN = eps', 'S_bad.SOURCES = [U]']
                checks.append('$run_source(U[.OCCURRENCES = eps], 100).COMPLETION = UNSUPPORTED "invalid compiled source unit"')
                checks.append('$task_nodes(AT (PORIGIN U.ID ([PCINDEX 0])) (BINARY_RIGHT ADD (REFERENCE 0) 1)) = [HCELL 0]')
            fixtures.append('dec $case'+str(i)+'() : bool\ndef $case'+str(i)+'() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
            records.append({'source_base64': base64.b64encode(source).decode(), 'checked_ast': ast, 'unit': unit,
                'encoding_profile': encoding_profile, 'equal_metadata': i<2, 'eval_order': orders, 'assertions': len(checks), 'occurrences': len(expected)})
    finally:
        frontend.close();adapter.close()
    with tempfile.TemporaryDirectory(prefix='source-origins-', dir=ROOT/'.tools') as tmp:
        for i, fixture in enumerate(fixtures):
            path = Path(tmp)/'case.watsup'
            path.write_text(PREFIX+fixture+'\ndec $main() : bool\ndef $main() = $case'+str(i)+'()\n')
            run = subprocess.run([str(runner), *map(str,specs), str(path)], cwd=ROOT, capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT/'.tools/source-origins-failure.watsup').write_text(path.read_text())
                raise AssertionError(f'origin case {i}: {run.stdout}{run.stderr}')
    assert before == fingerprint(), 'source-origin implementation changed during validation'
    report = {'result': 'pass', 'classification': 'checked occurrence propagation and task scopes; no pool/fact consumption',
        'source_cases': len(records), 'assertions': sum(r['assertions'] for r in records), 'records': records, 'fingerprint': before}
    (ROOT/'coverage/semantics/source-origins.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k: report[k] for k in ('result','source_cases','assertions')})


if __name__ == '__main__': main()
