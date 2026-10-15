#!/usr/bin/env python3
"""Disabled-multibyte parser warnings through genuine eval/file compilation."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = {'eval': 'eval-parser-warning-order', 'include': 'include-once-parser-warning'}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
CLI = runpy.run_path(str(ROOT / 'bin/php-semantics'))
MESSAGE = 'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
PREFIX = r'''
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_outputs(pevent*) : nat*
dec $test_output(pevent) : nat*
def $test_output(OUTPUT n*) = n*
def $test_output(pevent) = eps -- otherwise
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output(pevent) ++ $test_outputs(pevent_tail*)
dec $test_encoding_front(pstate, nat) : bool
def $test_encoding_front(S,n) = true
  -- if S.TODO = (STMT statement) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n pcpath)
  -- if $encoding_declare_valid(S,statement)
def $test_encoding_front(S,n) = false -- otherwise
dec $test_encoding_seek(pstate, nat, nat) : pstate
def $test_encoding_seek(S,n_unit,0) = S
def $test_encoding_seek(S,n_unit,n) = S
  -- if $(n > 0)
  -- if $test_encoding_front(S,n_unit) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_encoding_seek(S,n_unit,n) = $test_encoding_seek($drive_steps($test_running(S),1),n_unit,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_encoding_front(S,n_unit)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def encoding_front(state, previous, unit):
    return [state + '_found = $test_encoding_seek(' + previous + ',' + str(unit) + ',2500)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_encoding_front(' + state + ',' + str(unit) + ')',
        state + '.TODO = (STMT statement_' + state + ') :: ptask_' + state + '*', *public(state)]


def noop(state, previous):
    return [state + '_found = $drive_steps(' + previous + ',1)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        state + '.TODO = ptask_' + previous + '*',
        *[state + '.' + field + ' = ' + previous + '.' + field for field in
            ('RESULT','EVENTS','SOURCES','DECLARATIONS','STORE','ARRAYS','ALLOCATIONS')], *public(state)]


def final(state, previous, stdout):
    return [state + ' = $drive_steps(' + previous + ',2500)', state + '.COMPLETION = NORMAL',
        state + '.TODO = eps', '$test_outputs(' + state + '.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        *public(state)]


def eval_assertions(main, unit, code, case, stdout):
    accepted = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + unit
    checks = ['S_wait = $php_run(' + main + ',2500,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.EVALCONTEXTS = [pevalcontext]',
        'pevalcontext.UNIT = 1', 'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait,' + accepted + ')',
        'P = $ppstart_eval_state(S_wait,1,' + unit + ',pevalcontext.FILE,$call_request_cwd(S_wait.REQUEST),eps)',
        'P.COMPLETION = PPCNORMAL', 'P.DIAGNOSTICS = [pldiagnostic_encoding,pldiagnostic_unknown]',
        'pldiagnostic_encoding = PLDIAGNOSTIC "warning" "encoding-disabled" eps pllocation_encoding',
        'pllocation_encoding.UNIT = 1', 'pllocation_encoding.PATH = [PCINDEX 1]',
        'pllocation_encoding.FILE = pevalcontext.FILE', 'pllocation_encoding.LINE = 2',
        '$plmessage(pldiagnostic_encoding) = $ptascii(' + json.dumps(MESSAGE) + ')',
        'pldiagnostic_unknown = PLDIAGNOSTIC "warning" "unknown-declare" ([$ptascii("v54_unknown")]) pllocation_unknown',
        'pllocation_unknown.UNIT = 1', 'pllocation_unknown.LINE = 1',
        '$compiler_warning_level("encoding-disabled") = 128', '$compiler_warning_level("unknown-declare") = 128',
        'P.PUBLICATIONS = eps',
        'S_body = $eval_resume(S_wait,' + accepted + ')', *public('S_body'),
        *encoding_front('S','S_body',1),
        'S.EVENTS = S_wait.EVENTS ++ [$compiler_event("Warning",$plmessage(pldiagnostic_encoding),pllocation_encoding),$compiler_event("Warning",$plmessage(pldiagnostic_unknown),pllocation_unknown)]',
        'S.CURRENT = S_wait.CURRENT', 'S.FRAMES = S_wait.FRAMES',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        'S_resume = S_budget[.COMPLETION = NORMAL]', 'S_resume = S',
        'ptask_S_resume* = ptask_S*', *noop('S_noop','S_resume'),
        *final('S_final','S_noop',stdout),
        # Pure source projections are never driven.
        'P.FOLD.SOURCE.AST = PROGRAM (statement_unknown :: statement_encoding :: statement_tail*)',
        'statement_encoding = NStmtDeclare (SEQUENCE ([(NDeclareItem phpType11_name expression_value metadata_item)])) ABSENT metadata_statement',
        'P_reset = P[.DIAGNOSTICS = eps]',
        'P_omitted = P_reset[.FOLD.SOURCE.OCCURRENCES = eps]',
        '$ppparser_begin(P_omitted).DIAGNOSTICS = [pldiagnostic_encoding]',
        '~$encoding_declare_valid(S[.ORIGIN = eps],statement_encoding)',
        '$encoding_declare_site(P.FOLD.SOURCE.AST,[PCINDEX 1]) = (2)',
        '$encoding_declare_site(P.FOLD.SOURCE.AST,[PCINDEX 0]) = eps',
        '~$encoding_declare_first([NStmtNop metadata_statement,statement_encoding],[PCINDEX 1])']
    replacements = {
        'nonroot': 'PROGRAM ([NStmtBlock (SEQUENCE ([statement_encoding])) metadata_statement])',
        'multiline': 'PROGRAM ([NStmtDeclare (SEQUENCE ([(NDeclareItem phpType11_name expression_value metadata_item)])) ABSENT ([MstartLine 2,MendLine 3])])',
        'body': 'PROGRAM ([NStmtDeclare (SEQUENCE ([(NDeclareItem phpType11_name expression_value metadata_item)])) (SEQUENCE eps) metadata_statement])',
        'multiple': 'PROGRAM ([NStmtDeclare (SEQUENCE ([(NDeclareItem phpType11_name expression_value metadata_item),(NDeclareItem phpType11_name expression_value metadata_item)])) ABSENT metadata_statement])',
    }
    for name, program in replacements.items():
        checks += ['P_' + name + ' = P_reset[.FOLD.SOURCE.AST = ' + program + '][.FOLD.SOURCE.OCCURRENCES = eps]',
            '$ppparser_begin(P_' + name + ').COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source shape")']
    checks += ['P_nop = P_reset[.FOLD.SOURCE.AST = PROGRAM ([NStmtNop metadata_statement,statement_encoding])]',
        '$ppstrict_item(P_nop,[PCINDEX 1],ABSENT,NDeclareItem phpType11_name expression_value metadata_item).COMPLETION = PPCABRUPT (UNSUPPORTED "other declare directive compilation")']
    return checks


def include_assertions(main, units, case, stdout):
    filename,cwd,child = map(lambda p: term(os.fsencode(p)), [case/'main.php',case,case/'unit.php'])
    data = term((case/'unit.php').read_bytes())
    checks = ['S_open_first = $php_file_run(' + main + ',2500,' + filename + ',' + cwd + ')']
    previous = 'S_open_first'
    for stage,unit in [('first',1),('skip',None),('second',2)]:
        opened,parsed,body = 'S_open_'+stage,'S_parse_'+stage,'S_body_'+stage
        context = 'pfilecontext_'+stage
        if stage != 'first':
            checks += [opened + ' = $drive_steps(' + previous + ',2500)']
        response = 'FILE_OPENED '+context+'.NONCE '+context+'.CALLER '+context+'.REQUESTED '+child+' '+child+' '+data
        checks += [opened+'.COMPLETION = SOURCE_PENDING', opened+'.FILECONTEXTS = '+context+' :: pfilecontext_tail_'+stage+'*',
            context+'.PHASE = FILE_RESOLVE_WAIT',context+'.REQUESTED = $ptascii("unit.php")',
            '$file_open_response_valid('+opened+','+response+')', parsed+' = $file_open_resume('+opened+','+response+')']
        if stage == 'skip':
            checks += [context+'.KIND = 2',parsed+'.COMPLETION = NORMAL',
                *[parsed+'.'+field+' = '+opened+'.'+field for field in ('SOURCES','DECLARATIONS','FILES','EVENTS','CODE')],
                '$test_outputs('+opened+'.EVENTS) = $ptascii("B|R1:I|29|R2:")']
            previous = parsed
            continue
        accepted = 'SOURCE_ACCEPT '+str(unit)+' '+data+' '+units[unit-1]
        checks += [context+'.KIND = '+('2' if unit==1 else '1'), parsed+'.COMPLETION = SOURCE_PENDING',
            '$file_parse_response_valid('+parsed+','+accepted+')',body+' = $file_parse_resume('+parsed+','+accepted+')',
            *encoding_front('S_'+stage,body,unit),
            'S_'+stage+'.EVENTS = '+opened+'.EVENTS ++ [DIAGNOSTIC_SOURCE '+str(unit)+' "Warning" $ptascii('+json.dumps(MESSAGE)+') 2]',
            child+' <- S_'+stage+'.INCLUDEDOPENED',*noop('S_noop_'+stage,'S_'+stage)]
        previous = 'S_noop_'+stage
    return checks + final('S_final',previous,stdout) + [
        '|S_final.SOURCES| = 3', '|S_final.FILEBINDINGS| = 2',
        '$call_sourcefile(S_final.FILES,PORIGIN 1 eps) = '+child,
        '$call_sourcefile(S_final.FILES,PORIGIN 2 eps) = '+child]


class ParserWorker(Worker):
    """Local stderr custody; shared Worker continues to require empty stderr."""
    def __init__(self, command, output):
        super().__init__(command, output)
        self.recorded_stderr = bytearray()

    def parse(self, value, refusal=False):
        result = super().request(value)
        raw = (self.output/'stderr').read_bytes()
        delta = raw[len(self.recorded_stderr):]
        valid = CLI['dynamic_parser_stderr'](result, value.get('mode','eval'), delta)
        if refusal:
            assert not result['accepted'] and delta and not valid
        else:
            assert valid, (result,delta)
            assert not CLI['dynamic_parser_stderr'](result,value.get('mode','eval'),delta+b'Unexpected\n')
            if delta:
                assert not CLI['dynamic_parser_stderr'](result,value['mode'],b'')
                assert not CLI['dynamic_parser_stderr'](result,value['mode'],delta+delta)
                assert not CLI['dynamic_parser_stderr'](result,value['mode'],delta.replace(b'line 2',b'line 3'))
        self.recorded_stderr.extend(delta)
        return result

    def close(self):
        status = {}
        try:
            self.p.stdin.close()
            self.p.stdin = None
            stdout,_ = self.p.communicate(timeout=5)
            (self.output/'trailing.stdout').write_bytes(stdout)
            status = {'status':'exit','exit_status':self.p.returncode,'validated_parser_stderr_bytes':len(self.recorded_stderr)}
            assert self.p.returncode == 0 and not stdout
            self.stderr.flush()
            assert (self.output/'stderr').read_bytes() == bytes(self.recorded_stderr)
        except BaseException as error:
            status.update(exception=type(error).__name__,message=str(error))
            raise
        finally:
            if self.p.poll() is None:
                self.p.kill(); self.p.wait(timeout=5)
            status['final_exit_status'] = self.p.returncode
            (self.output/'close.json').write_text(json.dumps(status)+'\n')
            self.stderr.close()


def nodes(value):
    if isinstance(value,dict):
        if 'node' in value: yield value
        for child in value.values(): yield from nodes(child)
    elif isinstance(value,list):
        for child in value: yield from nodes(child)


def prepare(out,sources):
    out.mkdir()
    frontend = ParserWorker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        native = json.loads((sources/'static-native-v54/report.json').read_text())
        assert native['result']=='native_observation' and native['stable_inputs'] and native['target']==types.PROFILE
        for stage,name in CASES.items():
            case=sources/'static-native-v54'/name
            row,=[r for r in native['records'] if r['id']==name]
            assert row['exit']==0 and row['stderr']
            assert all(hashlib.sha256((case/key).read_bytes()).hexdigest()==value for key,value in row['originals'].items())
            parsed=frontend.parse({'op':'parse','source':b64((case/'main.php').read_bytes())});assert parsed['accepted']
            main=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            units=[]
            if stage=='eval':
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'declare(v54_unknown=')]
                unit=frontend.parse({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':b64(code)})
                assert unit['accepted'];checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                checks=eval_assertions(main,checked,code,case,row['stdout'])
            else:
                for ordinal in (1,2):
                    unit=frontend.parse({'op':'parse-file','id':str(ordinal),'mode':'file','profile':'cli-raw-85','requested':b64(b'unit.php'),'resolved':b64(os.fsencode(case/'unit.php')),'opened':b64(os.fsencode(case/'unit.php')),'source':b64((case/'unit.php').read_bytes())})
                    assert unit['accepted'];units.append(adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture'])
                checks=include_assertions(main,units,case,row['stdout'])
            target=out/stage;target.mkdir()
            (target/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+item+'\n' for item in checks))
        frontend.parse({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':b64(b'declare(encoding="UTF-8"); echo ;')},refusal=True)
    finally:
        try:
            if adapter: adapter.close()
        finally:
            frontend.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',required=True,choices=['fixtures','check'])
    parser.add_argument('--sources',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();sources,out=args.sources.resolve(),args.output.resolve()
    suite=sources/'static-native-v54'
    paths=[Path(__file__),ROOT/'tests/semantics/recorded_worker.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'frontend/target.php',ROOT/'adapter/wire.ml',suite/'run.py',suite/'report.json']
    for name in CASES.values():
        case=suite/name
        paths += [*case.glob('*.php'),*[case/'native'/n for n in ('stdout','stderr','process.json','command.json')]]
    if args.phase=='check':
        for stage in CASES: paths += [out/stage/'protocol.watsup',out/stage/'assertions.json']
    pins=lambda:dict(inputs.inputs(),**{str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before=pins();assert not (out/(args.phase+'-report.json')).exists()
    report={'phase':args.phase,'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'module_count':len(json.loads((ROOT/'spec/semantics/modules.json').read_text())),'runtime_diff_sha256':hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','spec/semantics','bin/php-semantics'],cwd=ROOT)).hexdigest(),'inputs':before,'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'sl_timeout':90,'result':'fail','records':[],'agreement_credit':0}
    try:
        if args.phase=='fixtures':
            prepare(out,sources);report['result']='pass'
        else:
            modules=[str(ROOT/name) for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
            for stage in CASES:
                target=out/stage;assert not (target/'check').exists()
                runner=process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*modules,str(target/'protocol.watsup')],target/'check',90,ROOT)
                passed=runner.returncode==0 and runner.stdout==b'true\n' and not runner.stderr
                report['records'].append({'id':stage,'pass':passed,'runner_exit':runner.returncode,'premises':len(json.loads((target/'assertions.json').read_text())) if passed else 0});print(json.dumps(report['records'][-1]),flush=True)
                if not passed:break
            report['result']='pass' if len(report['records'])==len(CASES) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs']=before==pins()
        if not report['stable_inputs']:
            report['result']='fail'
            for row in report['records']:row['pass'],row['premises']=False,0
        (out/(args.phase+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report['result']=='pass'


if __name__=='__main__':
    raise SystemExit(0 if main() else 1)
