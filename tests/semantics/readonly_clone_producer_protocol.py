#!/usr/bin/env python3
"""Source-reached implicit clone maker caches and per-key write revisions."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from readonly_clone_updates_protocol import PREFIX
from readonly_clone_updates_sources import CASES, EXPECTED, ROWS, snapshot

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'readonly-clone-with-parked-prior-write-changes-receipt'

CACHE_PREFIX = r'''
def $clone_updates_review_phase(S,16) = true
  -- if S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail*
  -- if $intrinsic_count(S,pfiberstart.SITE) = (pfiberstart.INDEX)
'''

def cache(initial):
    return [
        'S_initial = ' + initial,
        '~S_initial.COMPILESTOP',
        'S_start_found = $clone_updates_review_seek(S_initial,16,2048)',
        'S_start_found.COMPLETION = NORMAL \\/ S_start_found.COMPLETION = BUDGET',
        'S_start = S_start_found[.COMPLETION = NORMAL]',
        '$clone_updates_review_phase(S_start,16)',
        'S_start.TODO = (FIBER_ARGS pfiberstart) :: ptask_start_tail*',
        '$fiber_at(S_start,pfiberstart.OBJECT) = (pfiber)',
        'pfiber.STATUS = FIBER_INIT',
        'pfiber.READY',
        'pfiber.CALL = (pconfigcall)',
        'pfiber.TARGET = (pcalltarget)',
        'pfiber.PRODUCER = (pshutdownproducer)',
        'pfiber.CAPTURE = (pmethodcapture)',
        'S_start.CURRENT = (pcallcontext)',
        '$clone_context_valid(S_start,pcallcontext)',
        'pshutdownproducer.INTERNAL',
        'pshutdownproducer.TARGET = pcallcontext.TARGET',
        'pshutdownproducer.SITE = pcallcontext.CALLSITE',
        '$consumer_clone_context(S_start,pcallcontext)',
        '$call_descriptors_valid(S_start)',
        '$heap_valid($heap_graph(S_start))',
        '$fiber_producer_valid(S_start,pfiber)',
        '$fiber_cache_valid(S_start,pfiberstart.OBJECT,pfiber)',
        '$consumer_clone_producer_valid(S_start,pshutdownproducer)',
        '~$consumer_producer_internal(S_start,pshutdownproducer.TARGET)',
        '$consumer_producer_internal_at(S_start,pshutdownproducer)',
        'S_history = $consumer_producer_history(S_start,pshutdownproducer)',
        '$target_function(S_history,pshutdownproducer.TARGET) = (pfunction)',
        '$consumer_clone_producer_valid(S_history,pshutdownproducer)',
        'S_start.FRAMES = pframe_clone :: pframe_tail*',
        'pframe_clone.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_clone_tail*',
        'pframe_clone.CONTEXT = (pcallcontext_copied)',
        'pcallcontext_copied.CALLSITE = (porigin_method_call)',
        '$origin_node(S_start.SOURCES,porigin_method_call) = (NExprMethodCall expression_receiver phpType20_name phpType6_args metadata_method)',
        '~$consumer_clone_site_valid(S_start,porigin_method_call)',
        'S_start.OBJECTS[pcloneoperation.TARGET] = INSTANCE porigin_class',
        '$effective_method(S_start,porigin_class,$ptascii("copied"),|S_start.CLASSES|) = (pmethoddesc_copied)',
        'pshutdownproducer_ordinary = pshutdownproducer[.SITE = (porigin_method_call)]',
        'pmethodcapture_ordinary = pmethodcapture[.CALLSITE = (porigin_method_call)]',
        '~$consumer_clone_producer_valid(S_history,pshutdownproducer_ordinary)',
        'pfiber_ordinary = pfiber[.PRODUCER = (pshutdownproducer_ordinary)][.CAPTURE = (pmethodcapture_ordinary)]',
        'S_ordinary = $fiber_put(S_start,pfiberstart.OBJECT,pfiber_ordinary)',
        '$heap_valid($heap_graph(S_ordinary))',
        '~$fiber_producer_valid(S_ordinary,pfiber_ordinary)',
        '~$fiber_cache_valid(S_ordinary,pfiberstart.OBJECT,pfiber_ordinary)',
        '~$call_descriptors_valid(S_ordinary)',
        'pshutdownproducer_notinternal = pshutdownproducer[.INTERNAL = false]',
        'pmethodcapture_notinternal = pmethodcapture',
        '~$consumer_clone_producer_valid(S_history,pshutdownproducer_notinternal)',
        'pfiber_notinternal = pfiber[.PRODUCER = (pshutdownproducer_notinternal)][.CAPTURE = (pmethodcapture_notinternal)]',
        'S_notinternal = $fiber_put(S_start,pfiberstart.OBJECT,pfiber_notinternal)',
        '$heap_valid($heap_graph(S_notinternal))',
        '~$fiber_producer_valid(S_notinternal,pfiber_notinternal)',
        '~$fiber_cache_valid(S_notinternal,pfiberstart.OBJECT,pfiber_notinternal)',
        '~$call_descriptors_valid(S_notinternal)',
        'pshutdownproducer_missing = pshutdownproducer[.SITE = eps]',
        'pmethodcapture_missing = pmethodcapture[.CALLSITE = eps]',
        '~$consumer_clone_producer_valid(S_history,pshutdownproducer_missing)',
        'pfiber_missing = pfiber[.PRODUCER = (pshutdownproducer_missing)][.CAPTURE = (pmethodcapture_missing)]',
        'S_missing = $fiber_put(S_start,pfiberstart.OBJECT,pfiber_missing)',
        '$heap_valid($heap_graph(S_missing))',
        '~$fiber_producer_valid(S_missing,pfiber_missing)',
        '~$fiber_cache_valid(S_missing,pfiberstart.OBJECT,pfiber_missing)',
        '~$call_descriptors_valid(S_missing)',
        'pshutdownproducer_unrelated = pshutdownproducer[.TARGET = METHOD_TARGET pcloneoperation.TARGET pmethoddesc_copied.FUNCTION.ORIGIN]',
        'pmethodcapture_unrelated = pmethodcapture[.FUNCTION = pmethoddesc_copied.FUNCTION.ORIGIN]',
        '~$consumer_clone_producer_valid(S_history,pshutdownproducer_unrelated)',
        'pfiber_unrelated = pfiber[.PRODUCER = (pshutdownproducer_unrelated)][.CAPTURE = (pmethodcapture_unrelated)]',
        'S_unrelated = $fiber_put(S_start,pfiberstart.OBJECT,pfiber_unrelated)',
        '$heap_valid($heap_graph(S_unrelated))',
        '~$fiber_producer_valid(S_unrelated,pfiber_unrelated)',
        '~$fiber_cache_valid(S_unrelated,pfiberstart.OBJECT,pfiber_unrelated)',
        '~$call_descriptors_valid(S_unrelated)',
        '$consumer_producer_site((pmethodcapture_ordinary),pshutdownproducer_ordinary.SITE)',
        '$target_function(S_history,pshutdownproducer_ordinary.TARGET) = (pfunction)',
    ]

REVISIONS_PREFIX = r'''
dec $clone_updates_review_prior_receipt(pstate,ptbytes) : bool
def $clone_updates_review_prior_receipt(S,ptbytes) = true
  -- if S.ACTIVEFIBER = eps
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_tail*
  -- if $context_target(pcallcontext) = METHOD_TARGET n porigin_method
  -- if n = pcloneupdatestring.OBJECT
  -- if pcloneupdatestring.KEY = $ptascii("y")
  -- if $clone_updates_review_output(S.EVENTS) = $ptascii("P|Y|")
  -- if $location_slot(S,PROPERTY pcloneupdatestring.UPDATE.OPERATION.TARGET $ptascii("x")) = DEFINED (PSTRING ptbytes)
def $clone_updates_review_prior_receipt(S,ptbytes) = false -- otherwise
def $clone_updates_review_phase(S,14) = $clone_updates_review_prior_receipt(S,$ptascii("first"))
def $clone_updates_review_phase(S,15) = $clone_updates_review_prior_receipt(S,$ptascii("late"))
'''

def revisions(initial):
    return [
        'S_initial = ' + initial,
        'S_before_found = $clone_updates_review_seek(S_initial,14,2048)',
        'S_before_found.COMPLETION = NORMAL \\/ S_before_found.COMPLETION = BUDGET',
        'S_before = S_before_found[.COMPLETION = NORMAL]',
        '$clone_updates_review_phase(S_before,14)',
        '$call_descriptors_valid(S_before)',
        '$heap_valid($heap_graph(S_before))',
        '$clone_windows_valid(S_before)',
        'S_before.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_string_tail*',
        'S_before_caller = $parameter_string_frame_scope(S_before,pframe,pframe_tail*)',
        'pcloneupdate = pcloneupdatestring.UPDATE',
        'pcloneoperation = pcloneupdate.OPERATION',
        'pcloneupdate.CURSOR = 1',
        'pcloneupdate.VISITED = [pclonevisit_x]',
        'pclonevisit_x.KEY = KSTRING $ptascii("x")',
        'pclonevisit_x.TARGET = $ptascii("x")',
        'pclonevisit_x.VALUE = (PSTRING $ptascii("first"))',
        'pclonevisit_x.REVISION = (1)',
        'S_before.CLONES = [pclonewindow_before]',
        'pclonewindow_before.PHASE = CLONE_UPDATES',
        'pclonewindow_before.AVAILABLE = [$ptascii("y")]',
        'pclonewindow_before.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 0}]',
        '$clone_update_string_valid(S_before_caller,pcloneupdatestring)',
        'S_before.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("pending")) = (n_pending_cell)',
        'S_before.STORE[n_pending_cell] = DEFINED (POBJECT n_pending)',
        '$fiber_at(S_before,n_pending) = (pfiber_before)',
        'pfiber_before.STATUS = FIBER_SUSPENDED',
        '$fiber_cache_valid(S_before,n_pending,pfiber_before)',
        'pfiber_before.VM = (pfibervm_before)',
        '$fiber_vm_valid(S_before,pfibervm_before,(n_pending),eps)',
        '~$clone_reinitable(S_before,pcloneoperation.TARGET,$ptascii("x"))',
        '$clone_reinitable(S_before,pcloneoperation.TARGET,$ptascii("y"))',
        '$clone_written_revision(S_before.CLONES,pcloneoperation.TARGET,$ptascii("x")) = (1)',
        '$location_slot(S_before,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("first"))',
        '$objectprops_record_at(S_before.OBJECTPROPS,pcloneoperation.TARGET) = (pobjectprops_before)',
        'S_bad_current = S_before[.OBJECTPROPS = $objectprops_set(S_before.OBJECTPROPS,pcloneoperation.TARGET,$property_slot_set(pobjectprops_before.SLOTS,$ptascii("x"),PROP_VALUE (DIRECT (PSTRING $ptascii("late"))))) ]',
        '$heap_valid($heap_graph(S_bad_current))',
        'S_bad_current_caller = $parameter_string_frame_scope(S_bad_current,pframe,pframe_tail*)',
        '~$clone_updates_valid(S_bad_current_caller,pcloneupdate)',
        '~$call_descriptors_valid(S_bad_current)',
        'S_after_found = $clone_updates_review_seek(S_before,15,2048)',
        'S_after_found.COMPLETION = NORMAL \\/ S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]',
        '$clone_updates_review_phase(S_after,15)',
        '$call_descriptors_valid(S_after)',
        '$heap_valid($heap_graph(S_after))',
        '$clone_windows_valid(S_after)',
        'S_after.FRAMES = pframe_after :: pframe_after_tail*',
        'pframe_after.TODO = pframe.TODO',
        'S_after_caller = $parameter_string_frame_scope(S_after,pframe_after,pframe_after_tail*)',
        'S_after.CLONES = [pclonewindow_after]',
        'pclonewindow_after.OPERATION = pclonewindow_before.OPERATION',
        'pclonewindow_after.PHASE = CLONE_UPDATES',
        'pclonewindow_after.AVAILABLE = pclonewindow_before.AVAILABLE',
        'pclonewindow_after.REVISIONS = [{KEY $ptascii("x"), COUNT 2},{KEY $ptascii("y"), COUNT 0}]',
        '$clone_written_revision(S_after.CLONES,pcloneoperation.TARGET,$ptascii("x")) = (2)',
        '$clone_updates_valid(S_after_caller,pcloneupdate)',
        '$clone_update_string_valid(S_after_caller,pcloneupdatestring)',
        '$location_slot(S_after,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("late"))',
        '$location_slot(S_after,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PSTRING $ptascii("seed-y"))',
        '~$clone_reinitable(S_after,pcloneoperation.TARGET,$ptascii("x"))',
        '$clone_reinitable(S_after,pcloneoperation.TARGET,$ptascii("y"))',
        'S_after.ACTIVEFIBER = eps',
        'S_after.FIBERCALLERS = eps',
        '$fiber_at(S_after,n_pending) = (pfiber_after)',
        'pfiber_after.STATUS = FIBER_TERMINATED',
        'pfiber_after.VM = eps',
        'pfiber_after.CALL = eps',
        'pfiber_after.CAPTURE = eps',
        'pfiber_after.PRODUCER = eps',
        'pclonevisit_zero = pclonevisit_x[.REVISION = (0)]',
        'pcloneupdatestring_zero = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_zero]]]',
        'pframe_zero = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_zero) :: ptask_string_tail*]',
        'S_zero = S_after[.FRAMES = pframe_zero :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_zero))',
        '$clone_windows_valid(S_zero)',
        'S_zero_caller = $parameter_string_frame_scope(S_zero,pframe_zero,pframe_after_tail*)',
        '~$clone_updates_valid(S_zero_caller,pcloneupdatestring_zero.UPDATE)',
        '~$call_descriptors_valid(S_zero)',
        'pclonevisit_future = pclonevisit_x[.REVISION = (3)]',
        'pcloneupdatestring_future = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_future]]]',
        'pframe_future = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_future) :: ptask_string_tail*]',
        'S_future = S_after[.FRAMES = pframe_future :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_future))',
        '$clone_windows_valid(S_future)',
        'S_future_caller = $parameter_string_frame_scope(S_future,pframe_future,pframe_after_tail*)',
        '~$clone_updates_valid(S_future_caller,pcloneupdatestring_future.UPDATE)',
        '~$call_descriptors_valid(S_future)',
        'pclonevisit_missing = pclonevisit_x[.REVISION = eps]',
        'pcloneupdatestring_missing = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_missing]]]',
        'pframe_missing = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_missing) :: ptask_string_tail*]',
        'S_missing = S_after[.FRAMES = pframe_missing :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_missing))',
        '$clone_windows_valid(S_missing)',
        'S_missing_caller = $parameter_string_frame_scope(S_missing,pframe_missing,pframe_after_tail*)',
        '~$clone_updates_valid(S_missing_caller,pcloneupdatestring_missing.UPDATE)',
        '~$call_descriptors_valid(S_missing)',
        'pclonevisit_value = pclonevisit_x[.VALUE = (PSTRING $ptascii("late"))]',
        'pcloneupdatestring_value = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_value]]]',
        'pframe_value = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_value) :: ptask_string_tail*]',
        'S_value = S_after[.FRAMES = pframe_value :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_value))',
        '$clone_windows_valid(S_value)',
        'S_value_caller = $parameter_string_frame_scope(S_value,pframe_value,pframe_after_tail*)',
        '~$clone_updates_valid(S_value_caller,pcloneupdatestring_value.UPDATE)',
        '~$call_descriptors_valid(S_value)',
        'pclonevisit_key = pclonevisit_x[.KEY = KSTRING $ptascii("y")]',
        'pcloneupdatestring_key = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_key]]]',
        'pframe_key = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_key) :: ptask_string_tail*]',
        'S_key = S_after[.FRAMES = pframe_key :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_key))',
        '$clone_windows_valid(S_key)',
        'S_key_caller = $parameter_string_frame_scope(S_key,pframe_key,pframe_after_tail*)',
        '~$clone_updates_valid(S_key_caller,pcloneupdatestring_key.UPDATE)',
        '~$call_descriptors_valid(S_key)',
        'pclonevisit_target = pclonevisit_x[.TARGET = $ptascii("y")]',
        'pcloneupdatestring_target = pcloneupdatestring[.UPDATE = pcloneupdate[.VISITED = [pclonevisit_target]]]',
        'pframe_target = pframe_after[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_target) :: ptask_string_tail*]',
        'S_target = S_after[.FRAMES = pframe_target :: pframe_after_tail*]',
        '$heap_valid($heap_graph(S_target))',
        '$clone_windows_valid(S_target)',
        'S_target_caller = $parameter_string_frame_scope(S_target,pframe_target,pframe_after_tail*)',
        '~$clone_updates_valid(S_target_caller,pcloneupdatestring_target.UPDATE)',
        '~$call_descriptors_valid(S_target)',
        'S_rewind = S_after[.CLONES = [pclonewindow_after[.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 0}]][.AVAILABLE = pclonewindow_after.AVAILABLE]]]',
        '$heap_valid($heap_graph(S_rewind))',
        '~$call_descriptors_valid(S_rewind)',
        'S_nocount = S_after[.CLONES = [pclonewindow_after[.REVISIONS = [{KEY $ptascii("y"), COUNT 0}]][.AVAILABLE = pclonewindow_after.AVAILABLE]]]',
        '$heap_valid($heap_graph(S_nocount))',
        '~$call_descriptors_valid(S_nocount)',
        'S_swapcount = S_after[.CLONES = [pclonewindow_after[.REVISIONS = [{KEY $ptascii("y"), COUNT 0},{KEY $ptascii("x"), COUNT 2}]][.AVAILABLE = pclonewindow_after.AVAILABLE]]]',
        '$heap_valid($heap_graph(S_swapcount))',
        '~$call_descriptors_valid(S_swapcount)',
        'S_duplicate = S_after[.CLONES = [pclonewindow_after[.REVISIONS = [{KEY $ptascii("x"), COUNT 2},{KEY $ptascii("x"), COUNT 0}]][.AVAILABLE = pclonewindow_after.AVAILABLE]]]',
        '$heap_valid($heap_graph(S_duplicate))',
        '~$call_descriptors_valid(S_duplicate)',
        'S_reopen = S_after[.CLONES = [pclonewindow_after[.REVISIONS = pclonewindow_after.REVISIONS][.AVAILABLE = [$ptascii("x"),$ptascii("y")]]]]',
        '$heap_valid($heap_graph(S_reopen))',
        '~$call_descriptors_valid(S_reopen)',
        'S_done = $drive_steps(S_after,2048)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$clone_updates_review_output(S_done.EVENTS) = $ptascii("P|Y|seed/late/done")',
        'S_done.CLONES = eps',
        'S_done.ACTIVEFIBER = eps',
        'S_done.FIBERCALLERS = eps',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$clone_windows_valid(S_done)',
    ]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True, choices=['cache', 'revisions'])
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--prepare', action='store_true', help='frontend/adapter only; no model credit')
    parser.add_argument('--sl', action='store_true', help='strict SL runner; default is AL')
    args = parser.parse_args()
    source_bytes = CASES[SOURCE]
    row = next(row for row in ROWS if row['id'] == SOURCE)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    before['builder_sha256'] = sha(Path(__file__))
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-producer-'+args.group+'-', dir=ROOT/'.tools')).resolve()
    path = out/'source.php'; path.write_bytes(source_bytes)
    report = {'passed': False, 'prepared': False, 'before': before, 'group': args.group,
              'source_case': SOURCE, 'source': str(path), 'source_sha256': sha(path),
              'expected_stdout': EXPECTED[SOURCE], 'state_assertions_evaluated': 0,
              'mode': 'prepared; model UNRUN' if args.prepare else 'source-reached',
              'profile': cross.invoke.types.PROFILE,
              'runner_mode': 'strict SL' if args.sl else 'AL', 'numeric_cap_seconds': 120,
              'jobs': 1, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    frontend = adapter = None
    print(out, flush=True)
    try:
        assert report['source_sha256'] == row['source_sha256']
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(path)).decode())+')'
        clauses = ['program_source = '+checked['fixture'],
                   *{'cache': cache, 'revisions': revisions}[args.group](initial)]
        prefix = PREFIX + {'cache': CACHE_PREFIX, 'revisions': REVISIONS_PREFIX}[args.group]
        fixture = out/'protocol.watsup'
        fixture.write_text(prefix+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(prepared=True, prepared_assertions=len(clauses))
        if not args.prepare:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                *(['--sl'] if args.sl else []), *[str(ROOT/p) for p in modules],
                str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, state_assertions_evaluated=len(clauses))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = snapshot(args.freeze)
        report['after']['builder_sha256'] = sha(Path(__file__))
        report['inputs_unchanged'] = report['before'] == report['after']
        report['source_unchanged'] = report['source_sha256'] == sha(path)
        report['passed'] = report['passed'] and report['inputs_unchanged'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['mode'] if args.prepare else report['passed'], flush=True)
    assert report['inputs_unchanged'] and report['source_unchanged']
    assert report['prepared'] if args.prepare else report['passed']


if __name__ == '__main__':
    main()
