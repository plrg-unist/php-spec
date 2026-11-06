#!/usr/bin/env python3
"""Follow real Aggregate acquisition, copied SEND and their physical owners."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('generator_aggregate_arguments_review_cases.json')
SOURCE_SHA = 'a920fd73c9bae91d274214a2b0c89a2cee976ee92cb5fb1be655f65c6398ec4e'
CASE = 'i125-aggregate-send-body-type'
PREFIX = r'''
dec $test_i125_front(pstate, nat) : bool
def $test_i125_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
def $test_i125_front(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n porigin
def $test_i125_front(S, 2) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $test_i125_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
def $test_i125_front(S, 4) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask*
def $test_i125_front(S, 5) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_i125_front(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i125_front(S, n_stage) = false -- otherwise
dec $test_i125_seek(pstate, nat, nat) : pstate
def $test_i125_seek(S, n_stage, 0) = S
def $test_i125_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i125_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i125_seek(S, n_stage, n) = $test_i125_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i125_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_i125_output(pevent) : nat*
def $test_i125_output(OUTPUT n*) = n*
def $test_i125_output(pevent) = eps -- otherwise
dec $test_i125_outputs(pevent*) : nat*
def $test_i125_outputs(eps) = eps
def $test_i125_outputs(pevent :: pevent_tail*) = $test_i125_output(pevent) ++ $test_i125_outputs(pevent_tail*)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [state + '_found = $test_i125_seek(' + start + ', ' + str(stage) + ', 4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i125_front(' + state + ', ' + str(stage) + ')']


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))']


def checks(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0)]
    values += lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
S.CURRENT = (pcallcontext_caller)
pcallcontext_caller.NAME = $ptascii("run125T")
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
~pconfigcall.NAMED
pconfigcall.SELECTION = eps
$intrinsic_argument(S, pconfigcall.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))
S.RESULT = VARIABLE $ptascii("pack") z_argument
$lookup(S.ENV, $ptascii("target")) = (n_target_cv)
$lookup(S.ENV, $ptascii("pack")) = (n_pack_cv)
S.STORE[n_target_cv] = DEFINED (POBJECT n_target)
S.STORE[n_pack_cv] = DEFINED (POBJECT n_aggregate)
S.OBJECTS[n_target] = GENERATOR pgenerator_initial
pgenerator_initial.PHASE = GENERATOR_PAUSED
~pgenerator_initial.PENDING_INIT
pgenerator_initial.DELEGATE = eps
pgenerator_initial.CLOSURE = eps
pgenerator_initial.CREATION = eps
pgenerator_initial.ACCESS = eps
pgenerator_initial.REFCELL = eps
$generator_iterator_site(S, pconfigcall)
$config_aggregate_start(S, pconfigcall, S.RESULT, n_aggregate)
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 1
~$config_aggregate_start(S, pconfigcall[.OWNER = eps], S.RESULT, n_aggregate)
~$config_aggregate_start(S, pconfigcall[.OWNER = (n_aggregate)], S.RESULT, n_aggregate)
~$config_aggregate_start(S, pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" eps], S.RESULT, n_aggregate)
~$config_aggregate_start(S, pconfigcall[.LINE = $(pconfigcall.LINE + 1)], S.RESULT, n_aggregate)
~$config_aggregate_start(S, pconfigcall, KNOWN (POBJECT n_aggregate), n_aggregate)
S_fresh = S[.OBJECTS[n_target] = GENERATOR pgenerator_initial[.PHASE = GENERATOR_FRESH]]
~$config_aggregate_start(S_fresh, pconfigcall, S_fresh.RESULT, n_aggregate)
S_pending = S[.OBJECTS[n_target] = GENERATOR pgenerator_initial[.PENDING_INIT = true]]
~$config_aggregate_start(S_pending, pconfigcall, S_pending.RESULT, n_aggregate)
S_delegate = S[.OBJECTS[n_target] = GENERATOR pgenerator_initial[.DELEGATE = ({SITE porigin_argument, INPUT (POBJECT n_aggregate), POSITION 0, CURRENT eps, ACQUISITION eps})]]
~$config_aggregate_start(S_delegate, pconfigcall, S_delegate.RESULT, n_aggregate)
PhpStep: S ~> S_selected
S_selected.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_argument) z_argument) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
pconfigaggregate = {CALL pconfigcall, OBJECT n_aggregate, INPUT S.RESULT}
pcalltarget = AGGREGATE_METHOD_TARGET n_aggregate porigin_method
$target_nodes(pcalltarget) = eps
$target_instance(pcalltarget) = eps
$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_target]
$heap_graph(S_selected) = $heap_graph(S)
$call_selected_valid(S_selected, pcalltarget, (porigin_argument))
''')
    values += public('S_selected') + reach('S_borrowed', 'S_selected', 1)
    values += lines(r'''
S_borrowed.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = pcalltarget
pcallcontext_get.RECEIVER = (n_aggregate)
pcallcontext_get.CALLSITE = (porigin_argument)
pcallcontext_get.ARGC = 0
pcallcontext_get.EXTRA = eps
pcallcontext_get.NAMED = eps
$this_receiver(S_borrowed) = (n_aggregate)
$call_context_roots((pcallcontext_get)) = eps
S_borrowed.FRAMES = pframe_get :: pframe_get_tail*
pframe_get.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
$config_aggregate_frame(S_borrowed, pcallcontext_get, pframe_get)
$lookup(S_borrowed.ENV, $ptascii("data")) = (n_data_cv)
S_borrowed.STORE[n_data_cv] = DEFINED (POBJECT n_data)
$object_name(S_borrowed, n_data) = $ptascii("Data125T")
$heap_owners($heap_graph(S_borrowed), HOBJECT n_target) = 2
$heap_owners($heap_graph(S_borrowed), HOBJECT n_aggregate) = 1
$heap_owners($heap_graph(S_borrowed), HOBJECT n_data) = 1
''')
    values += public('S_borrowed') + reach('S_return', 'S_borrowed', 2)
    values += lines(r'''
S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
S_return.CURRENT = (pcallcontext_caller)
S_return.RESULT = KNOWN (POBJECT n_data)
$config_aggregate_iterator_admitted(S_return, pconfigaggregate, n_data)
$config_aggregate_return_allowed(S_return, pconfigaggregate)
~$config_aggregate_generator_return_allowed(S_return, pconfigaggregate)
~$config_aggregate_method_generator_return_allowed(S_return, pconfigaggregate)
$heap_owners($heap_graph(S_return), HOBJECT n_data) = 1
$heap_owners($heap_graph(S_return), HOBJECT n_aggregate) = 1
$heap_owners($heap_graph(S_return), HOBJECT n_target) = 2
S_return.OBJECTS[n_data] = INSTANCE porigin_data
$class_at(S_return.CLASSES, porigin_data) = (pclassdesc_data)
pmethoddesc_current = pclassdesc_data.METHODS[3]
pmethoddesc_current.NAME = $ptascii("current")
pmethoddesc_reference = pmethoddesc_current[.FUNCTION = pmethoddesc_current.FUNCTION[.SIGNATURE = pmethoddesc_current.FUNCTION.SIGNATURE[.BYREF = true]]]
S_reference = S_return[.CLASSES = $trait_class_set(S_return.CLASSES, pclassdesc_data[.METHODS[3] = pmethoddesc_reference])]
$effective_method(S_reference, porigin_data, $ptascii("current"), |S_reference.CLASSES|) = (pmethoddesc_reference)
~$generator_aggregate_current(S_reference, n_data)
~$config_aggregate_iterator_admitted(S_reference, pconfigaggregate, n_data)
~$config_aggregate_return_allowed(S_reference, pconfigaggregate)
PhpStep: S_reference ~> S_reference_stop
S_reference_stop = S_reference[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]
PhpStep: S_return ~> S_data
S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*
pconfigiterator_initial = {CALL pconfigcall, ITERATOR S_return.NEXTITER, OBJECT n_data, INPUT S.RESULT, PRODUCER (n_aggregate), ITEMS eps, CURRENT (KNOWN PNULL), KEY (KNOWN PNULL)}
S_data.ITERATORS = S_return.ITERATORS ++ [OBJECTITER S_return.NEXTITER n_data 0 false]
S_data.NEXTITER = $(S_return.NEXTITER + 1)
S_data.RESULT = KNOWN PNULL
S_data.BASE = BASE_VALUE (KNOWN PNULL)
S_data.ALLOCATIONS = S_return.ALLOCATIONS
S_data.STORE = S_return.STORE
S_data.EVENTS = S_return.EVENTS
$config_iterator_valid(S_data, pconfigiterator_initial, "rewind-start")
$config_iterator_producer_valid(S_data, pconfigiterator_initial)
$config_iterator_input_nodes(pconfigiterator_initial) = eps
$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_data, HOBJECT n_target]
$heap_owners($heap_graph(S_data), HOBJECT n_data) = 1
$heap_owners($heap_graph(S_data), HOBJECT n_aggregate) = 1
$heap_owners($heap_graph(S_data), HOBJECT n_target) = 2
S_return_pause = $drive(S_return, 0)
S_return_pause = S_return[.COMPLETION = BUDGET]
$call_descriptors_valid(S_return_pause)
S_return_one = $drive(S_return, 1)
S_return_one = S_data[.COMPLETION = BUDGET]
$drive(S_return_pause[.COMPLETION = NORMAL], 1) = S_return_one
''')
    values += public('S_data') + reach('S_send', 'S_data', 3)
    values += lines(r'''
S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*
pconfigiterator_send.CALL = pconfigcall
pconfigiterator_send.OBJECT = n_data
pconfigiterator_send.ITERATOR = pconfigiterator_initial.ITERATOR
pconfigiterator_send.PRODUCER = (n_aggregate)
pconfigiterator_send.INPUT = S.RESULT
pconfigiterator_send.ITEMS = eps
pconfigiterator_send.CURRENT = KNOWN (POBJECT n_token)
pconfigiterator_send.KEY = KNOWN (PINT 0)
$object_name(S_send, n_token) = $ptascii("Token125T")
S_send.STORE[n_target_cv] = DEFINED PNULL
S_send.STORE[n_pack_cv] = DEFINED PNULL
~((HOBJECT n_aggregate) <- S_send.ALLOCATIONS)
$config_iterator_producer_valid(S_send, pconfigiterator_send)
$config_iterator_aggregate_data(S_send, pconfigiterator_send)
$config_iterator_valid(S_send, pconfigiterator_send, "send")
$config_iterator_input_nodes(pconfigiterator_send) = eps
$task_nodes(CONFIG_ITERATOR pconfigiterator_send "send") = [HOBJECT n_token, HOBJECT n_data, HOBJECT n_target]
$heap_owners($heap_graph(S_send), HOBJECT n_aggregate) = 0
$heap_owners($heap_graph(S_send), HOBJECT n_data) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_token) = 1
~$config_iterator_producer_valid(S_send, pconfigiterator_send[.PRODUCER = (n_data)])
~$config_iterator_producer_valid(S_send, pconfigiterator_send[.PRODUCER = (n_target)])
~$config_iterator_producer_valid(S_send[.CODE = eps], pconfigiterator_send)
~$config_iterator_history(S_send, pconfigiterator_send[.CALL = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]])
~$config_iterator_history(S_send, pconfigiterator_send[.CALL = pconfigcall[.OWNER = (n_data)]])
~$config_iterator_history(S_send, pconfigiterator_send[.INPUT = KNOWN (POBJECT n_aggregate)])
PhpStep: S_send ~> S_copied
S_copied.TODO = (CONFIG_ITERATOR pconfigiterator_copied "next-start") :: ptask_tail*
pconfigiterator_copied = pconfigiterator_send[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]][.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]
$config_iterator_argument_nodes(pconfigiterator_copied) = [HOBJECT n_token]
$task_nodes(CONFIG_ITERATOR pconfigiterator_copied "next-start") = [HOBJECT n_data, HOBJECT n_target, HOBJECT n_token]
$heap_owners($heap_graph(S_copied), HOBJECT n_token) = 1
S_copied.STORE = S_send.STORE
S_copied.ALLOCATIONS = S_send.ALLOCATIONS
S_copied.EVENTS = S_send.EVENTS
''')
    values += public('S_send') + reach('S_finish', 'S_copied', 4)
    values += lines(r'''
S_finish.TODO = (CONFIG_ITERATOR pconfigiterator_finish "finish") :: ptask_tail*
pconfigiterator_finish = pconfigiterator_copied
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_data) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_token) = 1
$config_iterator_aggregate_data(S_finish, pconfigiterator_finish)
''')
    values += public('S_finish') + reach('S_ready', 'S_finish', 5)
    values += lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_finish "ready") :: ptask_tail*
S_ready.ITERATORS = S_return.ITERATORS
S_ready.NEXTITER = S_data.NEXTITER
~((HOBJECT n_data) <- S_ready.ALLOCATIONS)
~((HOBJECT n_aggregate) <- S_ready.ALLOCATIONS)
$config_iterator_retired_scope(S_ready, pconfigiterator_finish)
$config_iterator_valid(S_ready, pconfigiterator_finish, "ready")
$task_nodes(CONFIG_ITERATOR pconfigiterator_finish "ready") = [HOBJECT n_target, HOBJECT n_token]
$heap_owners($heap_graph(S_ready), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_token) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_data) = 0
$heap_owners($heap_graph(S_ready), HOBJECT n_aggregate) = 0
S_ready_pause = $drive(S_ready, 0)
S_ready_pause = S_ready[.COMPLETION = BUDGET]
$call_descriptors_valid(S_ready_pause)
PhpStep: S_ready ~> S_invoke
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (POBJECT n_token))]]
$config_invoke_valid(S_invoke, pconfigcall_copied)
$config_nodes(pconfigcall_copied) = [HOBJECT n_target, HOBJECT n_token]
S_ready_one = $drive(S_ready, 1)
S_ready_one = S_invoke[.COMPLETION = BUDGET]
$drive(S_ready_pause[.COMPLETION = NORMAL], 1) = S_ready_one
PhpStep: S_invoke ~> S_args
S_args.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: ptask_tail*
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
pgeneratorop.SITE = pconfigcall.SITE
pgeneratorop.LINE = pconfigcall.LINE
pgeneratorop.ARGUMENTS = eps
pgeneratorop.SELECTION = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) = $config_nodes(pconfigcall_copied)
S_args.STORE = S_invoke.STORE
S_args.ALLOCATIONS = S_invoke.ALLOCATIONS
S_args.EVENTS = S_invoke.EVENTS
$heap_owners($heap_graph(S_args), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_args), HOBJECT n_token) = 1
''')
    values += public('S_ready') + public('S_args') + reach('S_closed', 'S_args', 6)
    values += lines(r'''
S_closed.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop_closed) :: ptask_tail*
S_closed.CURRENT = (pcallcontext_caller)
pgeneratorop_closed = pgeneratorop[.ARGUMENTS = [POBJECT n_token]]
S_closed.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
~pgenerator_closed.PENDING_INIT
$generator_api_body_throw(S_closed, pgeneratorop_closed)
$object_name(S_closed, n_error) = $ptascii("TypeError")
$throwable_field(S_closed, n_error, "previous") = PNULL
$throwable_field(S_closed, n_error, "trace") = PARRAY n_trace
S_closed.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_typed)), ENTRY (KINT 1) (DIRECT (PARRAY n_body)), ENTRY (KINT 2) (DIRECT (PARRAY n_api)), ENTRY (KINT 3) (DIRECT (PARRAY n_caller))]
$trace_array_field(S_closed, n_typed, $ptascii("function")) = PSTRING $ptascii("typed125T")
$trace_array_field(S_closed, n_body, $ptascii("function")) = PSTRING $ptascii("flow125T")
$trace_array_field(S_closed, n_api, $ptascii("function")) = PSTRING $ptascii("send")
$trace_array_field(S_closed, n_api, $ptascii("class")) = PSTRING $ptascii("Generator")
$trace_array_field(S_closed, n_api, $ptascii("line")) = PINT pconfigcall.LINE
$trace_array_field(S_closed, n_caller, $ptascii("function")) = PSTRING $ptascii("run125T")
$trace_array_field(S_closed, n_typed, $ptascii("args")) = PARRAY n_typed_args
S_closed.ARRAYS[n_typed_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
$trace_array_field(S_closed, n_api, $ptascii("args")) = PARRAY n_api_args
S_closed.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
$heap_owners($heap_graph(S_closed), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_token) = 3
$heap_owners($heap_graph(S_closed), HOBJECT n_data) = 0
$heap_owners($heap_graph(S_closed), HOBJECT n_aggregate) = 0
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
$test_i125_outputs(S_closed.EVENTS) = $ptascii("INIT|CALL|GET|GET-HELD|1|1|REWIND|PACK|1|1|1|HELD|1|1|1|VALID|CURRENT|KEY|NEXT|VALID|DATA|1|1|1|1|BODY|1|1|1|FIN|1|1|1|1|")
''')
    return values + public('S_closed')


def run(out=None, process_seconds=600):
    row, = [row for row in json.loads(CATALOG.read_bytes()) if row['id'] == CASE]
    assert row['source_sha256'] == SOURCE_SHA
    assert hashlib.sha256(row['source'].encode()).hexdigest() == SOURCE_SHA
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-aggregate-arguments-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'source.php'
    source.write_text(row['source'])
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        adapter.close()
    conditions = checks(checked['fixture'], source)
    fixture = out / 'test.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (condition if condition.startswith('PhpStep:') else 'if ' + condition) + '\n'
        for condition in conditions))
    (out / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], out, 'model', environment, process_seconds)
    passed = not process['timeout'] and process['exit'] == 0 and (out / 'model.stdout').read_bytes() == b'true\n' and (out / 'model.stderr').read_bytes() == b''
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': [CASE], 'source_sha256': SOURCE_SHA, 'assertions': len(conditions), 'process': process, 'passed': passed}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
