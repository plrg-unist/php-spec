#!/usr/bin/env python3
"""Real constructor array unpack separates direct slots and retains aliases."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_unpack_cases.json'
SOURCE_SHA = '20ff70c05a5323d9f0b54c6aa543484450b3a0b70a42e46ac70767a5261787ef'

PREFIX = r'''
dec $ctor_unpack_output_item(pevent) : ptbytes
def $ctor_unpack_output_item(OUTPUT ptbytes) = ptbytes
def $ctor_unpack_output_item(pevent) = eps -- otherwise
dec $ctor_unpack_output(pevent*) : ptbytes
def $ctor_unpack_output(eps) = eps
def $ctor_unpack_output(pevent :: pevent_tail*) = $ctor_unpack_output_item(pevent) ++ $ctor_unpack_output(pevent_tail*)
dec $ctor_unpack_site(pstate,porigin) : bool
def $ctor_unpack_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata) = 5
def $ctor_unpack_site(S,porigin) = false -- otherwise
dec $ctor_unpack_stage(pstate,nat) : bool
def $ctor_unpack_stage(S,0) = true
  -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*
  -- if punpackcall.CALLSITE = (porigin_site)
  -- if $ctor_unpack_site(S,porigin_site)
def $ctor_unpack_stage(S,1) = true
  -- if S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*
  -- if punpackcall.ARGUMENTS = eps /\ punpackcall.INDEX = 1
  -- if punpackcall.CALLSITE = (porigin_site)
  -- if $ctor_unpack_site(S,porigin_site)
def $ctor_unpack_stage(S,2) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $ctor_unpack_site(S,porigin_site)
def $ctor_unpack_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 12
def $ctor_unpack_stage(S,n) = false -- otherwise
dec $ctor_unpack_seek(pstate,nat,nat) : pstate
def $ctor_unpack_seek(S,n_mode,n) = S -- if $ctor_unpack_stage(S,n_mode)
def $ctor_unpack_seek(S,n_mode,0) = S -- if ~$ctor_unpack_stage(S,n_mode)
def $ctor_unpack_seek(S,n_mode,n) = $ctor_unpack_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ctor_unpack_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ctor_unpack_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_prep_raw = $ctor_unpack_seek(S_initial[.COMPLETION = NORMAL],0,4096)',
        r'S_prep_raw.COMPLETION = NORMAL \/ S_prep_raw.COMPLETION = BUDGET',
        'S_prep = S_prep_raw[.COMPLETION = NORMAL]',
        '$ctor_unpack_stage(S_prep,0)', 'S_prep.CURRENT = eps',
        'S_prep.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
        'punpackcall.FUNCTION = METHOD_TARGET n_object porigin_ctor',
        'punpackcall.ARGUMENTS = eps', 'punpackcall.INDEX = 0',
        'punpackcall.SENT = {SLOTS eps, NAMED eps}',
        'punpackcall.CALLSITE = (porigin_site)',
        '$target_function(S_prep,punpackcall.FUNCTION) = (pfunction)',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_second]',
        'psparam_first.BYREF', 'psparam_second.BYREF',
        '~psparam_first.VARIADIC', '~psparam_second.VARIADIC',
        'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_second.TYPE = eps',
        '$unpack_class(S_prep,punpackcall) = (UNPACK_CV)',
        '$unpack_writable(S_prep,punpackcall)',
        '$lookup(S_prep.ENV,$ptascii("shared")) = (n_shared)',
        'S_prep.STORE[n_shared] = DEFINED pvalue_raw',
        '$string_bytes(pvalue_raw) = ($ptascii("7"))',
        '$lookup(S_prep.ENV,$ptascii("pack")) = (n_pack)',
        '$lookup(S_prep.ENV,$ptascii("snapshot")) = (n_snapshot)',
        'n_pack =/= n_snapshot',
        'S_prep.STORE[n_pack] = DEFINED (PARRAY n_old_array)',
        'S_prep.STORE[n_snapshot] = DEFINED (PARRAY n_old_array)',
        'S_prep.ARRAYS[n_old_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_shared),ENTRY (KINT 1) (DIRECT (PINT 20))]',
        '$unpack_needs_reference(pfunction.SIGNATURE.PARAMETERS,S_prep.ARRAYS[n_old_array].ITEMS,0)',
        'S_prep.RESULT = VARIABLE $ptascii("pack") z_pack',
        '$unpack_result_valid(S_prep)',
        '$call_task_valid(S_prep,UNPACK_PREP punpackcall)',
        '$call_descriptors_valid(S_prep)',
        '~$unpack_result_valid(S_prep[.RESULT = KNOWN (PARRAY n_old_array)])',
        '~$call_task_valid(S_prep,UNPACK_PREP punpackcall[.INDEX = 1])',
        'S_separated_raw = $drive_steps(S_prep,1)',
        r'S_separated_raw.COMPLETION = NORMAL \/ S_separated_raw.COMPLETION = BUDGET',
        'S_separated = S_separated_raw[.COMPLETION = NORMAL]',
        'S_separated.TODO = (UNPACK_NEXT punpackcall poperand_array 0 false) :: ptask_tail*',
        'S_separated.STORE[n_pack] = DEFINED (PARRAY n_live_array)',
        'n_live_array =/= n_old_array',
        '$unpack_array(S_separated,poperand_array) = n_live_array',
        'S_separated.STORE[n_snapshot] = DEFINED (PARRAY n_old_array)',
        'S_separated.STORE[n_shared] = DEFINED pvalue_raw',
        'S_separated.ARRAYS[n_live_array].ITEMS = S_prep.ARRAYS[n_old_array].ITEMS',
        'S_separated.ARRAYS[n_old_array].ITEMS = S_prep.ARRAYS[n_old_array].ITEMS',
        '$call_task_valid(S_separated,UNPACK_NEXT punpackcall poperand_array 0 false)',
        '~$call_task_valid(S_separated,UNPACK_NEXT punpackcall poperand_array 0 true)',
        'S_first_raw = $drive_steps(S_separated,1)',
        r'S_first_raw.COMPLETION = NORMAL \/ S_first_raw.COMPLETION = BUDGET',
        'S_first = S_first_raw[.COMPLETION = NORMAL]',
        'S_first.TODO = (UNPACK_NEXT punpackcall_first poperand_array 1 false) :: ptask_tail*',
        'punpackcall_first.SENT.SLOTS = [NAMED_SENT (REFERENCE n_shared)]',
        'punpackcall_first.SENT.NAMED = eps',
        'S_first.STORE[n_shared] = DEFINED pvalue_raw',
        '$call_task_valid(S_first,S_first.TODO[0])',
        'S_second_raw = $drive_steps(S_first,1)',
        r'S_second_raw.COMPLETION = NORMAL \/ S_second_raw.COMPLETION = BUDGET',
        'S_second = S_second_raw[.COMPLETION = NORMAL]',
        'S_second.TODO = (UNPACK_NEXT punpackcall_second poperand_array 2 false) :: ptask_tail*',
        'punpackcall_second.SENT.SLOTS = [NAMED_SENT (REFERENCE n_shared),NAMED_SENT (REFERENCE n_direct)]',
        'punpackcall_second.SENT.NAMED = eps',
        'n_direct =/= n_shared',
        'S_second.STORE[n_direct] = DEFINED (PINT 20)',
        'S_second.STORE[n_shared] = DEFINED pvalue_raw',
        'S_second.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_shared),ENTRY (KINT 1) (ALIAS n_direct)]',
        'S_second.ARRAYS[n_old_array].ITEMS = S_prep.ARRAYS[n_old_array].ITEMS',
        '$call_reference_operand_valid(S_second,REFERENCE n_direct)',
        '$call_task_valid(S_second,S_second.TODO[0])',
        'S_sent_raw = $ctor_unpack_seek(S_second,1,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        '$ctor_unpack_stage(S_sent,1)',
        'S_sent.TODO = (UNPACK_ARGS punpackcall_done) :: ptask_tail*',
        'punpackcall_done.SENT = punpackcall_second.SENT',
        '$call_task_valid(S_sent,UNPACK_ARGS punpackcall_done)',
        '~$call_task_valid(S_sent,UNPACK_ARGS punpackcall_done[.SENT = punpackcall_done.SENT[.SLOTS = [NAMED_SENT (KNOWN pvalue_raw),NAMED_SENT (REFERENCE n_direct)]]])',
        '$ctor_unpack_output(S_sent.EVENTS) = eps',
        'S_type_raw = $ctor_unpack_seek(S_sent,2,4096)',
        r'S_type_raw.COMPLETION = NORMAL \/ S_type_raw.COMPLETION = BUDGET',
        'S_type = S_type_raw[.COMPLETION = NORMAL]',
        'S_type.TODO = [TYPE_RECEIVE porigin_ctor 0]',
        'S_type.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
        'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
        '$lookup(S_type.ENV,$ptascii("first")) = (n_shared)',
        '$lookup(S_type.ENV,$ptascii("second")) = (n_direct)',
        'S_type.STORE[n_shared] = DEFINED pvalue_raw',
        'S_type.STORE[n_direct] = DEFINED (PINT 20)',
        '$call_task_valid(S_type,TYPE_RECEIVE porigin_ctor 0)',
        '~$typed_caller_strict(S_type)',
        'S_received_raw = $drive_steps(S_type,1)',
        r'S_received_raw.COMPLETION = NORMAL \/ S_received_raw.COMPLETION = BUDGET',
        'S_received = S_received_raw[.COMPLETION = NORMAL]',
        'S_received.TODO = [TYPE_RECEIVE porigin_ctor 1]',
        'S_received.STORE[n_shared] = DEFINED (PINT 7)',
        'S_received.STORE[n_direct] = DEFINED (PINT 20)',
        '$call_task_valid(S_received,TYPE_RECEIVE porigin_ctor 1)',
        '$heap_valid($heap_graph(S_received))',
        'S_late_raw = $ctor_unpack_seek(S_received,3,4096)',
        r'S_late_raw.COMPLETION = NORMAL \/ S_late_raw.COMPLETION = BUDGET',
        'S_late = S_late_raw[.COMPLETION = NORMAL]',
        '$ctor_unpack_stage(S_late,3)',
        '$ctor_unpack_output(S_late.EVENTS) = $ptascii("first-int|")',
        'S_late.STORE[n_shared] = DEFINED (PINT 9)',
        'S_late.STORE[n_direct] = DEFINED (PINT 30)',
        'S_late.STORE[n_pack] = DEFINED (PARRAY n_live_array)',
        'S_late.STORE[n_snapshot] = DEFINED (PARRAY n_old_array)',
        'S_late.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_shared),ENTRY (KINT 1) (ALIAS n_direct)]',
        'S_late.ARRAYS[n_old_array].ITEMS = S_prep.ARRAYS[n_old_array].ITEMS',
        '$call_reference_operand_valid(S_late,REFERENCE n_direct)',
        '$call_descriptors_valid(S_late)', '$heap_valid($heap_graph(S_late))',
        'S_done = $drive_steps(S_late,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ctor_unpack_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-unpack-binding-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source, Path(__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': SOURCE_SHA, 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        checks = assertions(checked['fixture'], os.fsencode(source), stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), derived_guards=4, fixture_sha256=sha(fixture))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
