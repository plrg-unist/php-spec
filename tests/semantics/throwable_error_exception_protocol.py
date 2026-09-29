#!/usr/bin/env python3
"""Paused ErrorException slot layout, call owner, and sent-value roots."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
from throwable_protocol import PREFIX

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('eight-slots', b'<?php $e=new ErrorException("m",3,5,"f.php",-7);echo $e->getSeverity();',
     'S.TODO = (CTOR_ARGS pctorcall) :: ptask*', [
         'pctorcall.BASE = "ErrorException"',
         '$call_task_valid(S,CTOR_ARGS pctorcall)',
         '~$call_task_valid(S,CTOR_ARGS pctorcall[.BASE = "Exception"])',
         '$property_state_valid(S)',
         '$heap_valid($heap_graph(S))',
         '$($heap_owners($heap_graph(S),HOBJECT pctorcall.RECEIVER) > 0)',
         '$throwable_field(S,pctorcall.RECEIVER,"severity") = PINT 1',
         '$throwable_field(S,pctorcall.RECEIVER,"trace") = PARRAY n_trace',
         '$trace_graph_valid(S,n_trace)',
         '$objectprops_record_at(S.OBJECTPROPS,pctorcall.RECEIVER) = (pobjectprops)',
         'pobjectprops.SLOTS = [ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous,ppropertyslot_severity]',
         'ppropertyslot_string.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("string"))',
         'ppropertyslot_trace.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("trace"))',
         'ppropertyslot_previous.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("previous"))',
         'ppropertyslot_severity.DECL = (INTERNAL_PROPERTY "ErrorException" $ptascii("severity"))',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,pctorcall.RECEIVER,[ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,pctorcall.RECEIVER,[ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous,ppropertyslot_severity[.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("severity"))]])])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
    ('named-roots', b'<?php $p=new Exception("p");$e=new ErrorException(previous:$p,line:-7,filename:"f.php",severity:8,code:9,message:"m");echo $e->getPrevious()===$p;',
     'S.TODO = (CTOR_INVOKE pctorcall) :: ptask* -- if pctorcall.BASE = "ErrorException"', [
         'pctorcall.BASE = "ErrorException"',
         '$call_task_valid(S,CTOR_INVOKE pctorcall)',
         '$named_slot_at(pctorcall.SENT,5) = NAMED_SENT (KNOWN (POBJECT n_previous))',
         'n_previous =/= pctorcall.RECEIVER',
         '(HOBJECT n_previous) <- $task_nodes(CTOR_INVOKE pctorcall)',
         '$($heap_owners($heap_graph(S),HOBJECT n_previous) > 0)',
         '~$call_task_valid(S,CTOR_INVOKE pctorcall[.BASE = "Exception"])',
         '~$call_task_valid(S,CTOR_INVOKE pctorcall[.SENT = eps])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL',
         '$throwable_field(S_done,pctorcall.RECEIVER,"line") = PINT (-7)',
         '$throwable_field(S_done,pctorcall.RECEIVER,"severity") = PINT 8',
         '$property_state_valid(S_done)']),
    ('severity-getter', b'<?php $e=new ErrorException("m",0,9);echo $e->getSeverity();',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_SEVERITY', [
         'pgettercall.BASE = "ErrorException"',
         '$call_task_valid(S,GETTER_INVOKE pgettercall)',
         '~$call_task_valid(S,GETTER_INVOKE pgettercall[.BASE = "Exception"])',
         '~$call_task_valid(S,GETTER_INVOKE pgettercall[.METHOD = GET_MESSAGE])',
         '$throwable_field(S,pgettercall.RECEIVER,"severity") = PINT 9',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         'S_next.RESULT = KNOWN (PINT 9)',
         '$property_state_valid(S_next)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = modules + [ROOT / 'spec/semantics/modules.json', Path(__file__),
                        ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
                        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
                        ROOT / 'tests/semantics/profile.json',
                        ROOT / '_build/default/adapter/main.exe',
                        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    out = Path(tempfile.mkdtemp(prefix='error-exception-protocol-', dir=ROOT / '.tools'))
    records = []
    for name, source, stage, checks in CASES:
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL],1000)[.COMPLETION = NORMAL]',
                      stage] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + condition + '\n' for condition in conditions))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'pass': passed, 'assertions': len(conditions),
                        'source_sha256': digest(path), 'fixture_sha256': digest(fixture)})
        print(name, passed, flush=True)
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in inputs}, 'inputs changed'
    report = {'result': 'pass' if all(r['pass'] for r in records) else 'fail',
              'inputs': before, 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
