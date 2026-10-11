#!/usr/bin/env python3
"""Reached concat-result emission, caller continuations and later magic getters."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_float_protocol as floating
import magic_property_reference_protocol as reference
import magic_property_boolean_string_protocol as boolean_string

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-property-concat-emit-'+group+'37' for group in
         ('reference-kept', 'reference-drop', 'owned', 'source-conflict', 'inner-getter')}
PREFIX = integer.PREFIX + r'''
dec $concat_emit_ready(pstate, ptbytes) : bool
def $concat_emit_ready(S, ptbytes) = true
  -- if S.TODO = (EMIT z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if S.BASE = BASE_VALUE S.RESULT
  -- if $string_bytes(pvalue) = (ptbytes)
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBinaryOpConcat expression_left expression_right metadata)
def $concat_emit_ready(S, ptbytes) = false -- otherwise
dec $concat_emit_seek(pstate, ptbytes, nat) : pstate
def $concat_emit_seek(S, ptbytes, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_emit_seek(S, ptbytes, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $concat_emit_ready(S, ptbytes) \/ n = 0
def $concat_emit_seek(S, ptbytes, n) = $concat_emit_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptbytes, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$concat_emit_ready(S, ptbytes) /\ $(n > 0)
dec $concat_emit_right_task(ptask) : bool
def $concat_emit_right_task(CONCAT_RIGHT poperand b_left b_right z) = true
def $concat_emit_right_task(ptask) = false -- otherwise
dec $concat_emit_left(ptask*) : poperand?
def $concat_emit_left((CONCAT_RIGHT poperand b_left b_right z) :: ptask_tail*) = (poperand)
def $concat_emit_left(ptask :: ptask_tail*) = $concat_emit_left(ptask_tail*)
  -- if ~$concat_emit_right_task(ptask)
def $concat_emit_left(eps) = eps
'''


def emit(parent, state, text):
    # Every field outside this consumer's four updates must remain identical.
    label = state.removeprefix('S_')
    line, tail, site = 'z_'+label, 'ptask_'+label+'_tail*', 'porigin_'+label
    value, identity, data = 'pvalue_'+label, 'n_'+label+'_identity', 'n_'+label+'_bytes*'
    return [f'{state}_found = $concat_emit_seek({parent}, {cross.invoke.byte_expr(text.encode())}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]', *get.valid(state),
        f'$concat_emit_ready({state}, {cross.invoke.byte_expr(text.encode())})',
        f'{state}.TODO = (EMIT {line}) :: {tail}',
        f'{state}.ORIGIN = ({site})',
        f'$origin_node({state}.SOURCES, {site}) = (NExprBinaryOpConcat expression_{label}_left expression_{label}_right metadata_{label})',
        f'{state}.RESULT = KNOWN {value}',
        f'{value} = PSTRING_CARRIER (REQUEST_STRING {identity}) {data}',
        f'{data} = '+cross.invoke.byte_expr(text.encode()),
        f'$string_carrier_valid({state}, {value})',
        f'{state}.BASE = BASE_VALUE (KNOWN {value})',
        f'$resolve({state}, {state}.RESULT) = {state}',
        f'$stringify({state}, {value}, {line}) = {state}',
        f'{state}_paused = $drive_steps({state}, 0)',
        f'{state}_paused = {state}[.COMPLETION = BUDGET]',
        f'{state}_expected = {state}[.TODO = {tail}][.EVENTS = {state}.EVENTS ++ [OUTPUT {data}]][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'PhpStep: {state} ~> {state}_raw', f'{state}_raw = {state}_expected',
        *get.step(state, state+'_after'), f'{state}_after = {state}_expected',
        f'{state}_after.FRAMES = {state}.FRAMES', f'{state}_after.HELD = {state}.HELD',
        f'{state}_after.CURRENT = {state}.CURRENT',
        f'$heap_graph({state}_after) = $heap_graph({state})']


def getter(parent):
    return [*integer.seek(parent, 'S_before', 0, '0'),
        'S_before.BASE = BASE_VALUE (KNOWN PNULL)',
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        '$property_get_history(S_before, ppropertyget)',
        '$property_get_valid(S_before, ppropertyget, true)',
        'S_dirty = S_before[.BASE = BASE_VALUE (KNOWN pvalue_emit)]',
        '$property_get_plan(S_dirty) = eps',
        *get.step('S_before', 'S_pending'), *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_tail_valid(S_return, ppropertyget)',
        'S_return.RESULT = REFERENCE n_return_cell',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps']


def body(run, source, expected, group):
    text = 'before-conflict|1/1|' if group == 'source-conflict' else 'inner|value|' if group in ('owned', 'inner-getter') else 'before|1|'
    clauses = ['S_initial = '+run, '~S_initial.COMPILESTOP', *emit('S_initial', 'S_emit', text)]
    if group in ('owned', 'inner-getter'):
        clauses += ['S_emit.CURRENT = (pcallcontext_get)',
            'pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_reader porigin_method',
            'S_emit.FRAMES = pframe_get :: pframe_tail*',
            'pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
            'ppropertyget.OBJECT = n_reader',
            '$property_get_frame(S_emit, pcallcontext_get, pframe_get)',
            '$heap_owners($heap_graph(S_emit), HOBJECT n_reader) = 2',
            *integer.seek('S_emit_after', 'S_return', 1),
            'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
            'S_return.RESULT = REFERENCE n_return_cell',
            'S_return.STORE[n_return_cell] = DEFINED pvalue_raw']
    else:
        clauses += getter('S_emit_after')
    if group == 'source-conflict':
        message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
        clauses += ['$trace_slot(S_emit, S_emit.ENV, $ptascii("first")) = pvalue_first',
            '$string_bytes(pvalue_first) = ($ptascii("1"))',
            '$trace_slot(S_emit, S_emit.ENV, $ptascii("getCalls")) = PINT 1',
            'S_emit.STORE[n_return_cell] = DEFINED (PBOOL true)',
            'pvalue_raw = PBOOL true', '$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)',
            '$proprefs_valid(S_return)', '$property_get_propref(S_return, ppropertyget, n_return_cell)',
            'ppropref.SOURCES = [pproptypesource_first]', *reference.source_slot(),
            '$property_type_name(S_return, ppropertydesc_source) = $ptascii("string|bool")',
            *boolean_string.error_verify(expected),
            *integer.reader('S_return', '(n_type_error)'),
            'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_raw',
            '$propref_at(S_reader_dtor.PROPREFS, n_return_cell) = (ppropref)',
            *integer.seek('S_reader_dtor', 'S_error_copy', 6),
            'S_error_copy.STORE[n_return_cell] = DEFINED pvalue_first',
            '$propref_at(S_error_copy.PROPREFS, n_return_cell) = eps',
            'S_error_copy.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
            '$get_test_message(S_error_copy, n_error, '+message+')',
            '$throwable_previous_id(S_error_copy, n_error) = eps', *get.finish('S_error_copy', expected)]
    else:
        clauses += ['$string_bytes(pvalue_raw) = ($ptascii("ok"))',
            '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return']
        if group == 'owned':
            clauses += [*floating.copied('S_return', value='pvalue_raw', alive=True),
                'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
                *integer.seek('S_copy', 'S_base', 3), 'S_base.RESULT = KNOWN pvalue_raw',
                '$property_get_base_valid(S_base, ppropertyget)',
                *integer.reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
                *integer.seek('S_reader_dtor', 'S_received', 5),
                'S_received.RESULT = KNOWN pvalue_raw',
                'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
                '$string_bytes(pvalue_changed) = ($ptascii("changed"))']
        elif group == 'reference-drop':
            clauses += [*integer.reader('S_return'),
                'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget',
                *floating.copied('S_reader_dtor', value='pvalue_raw'),
                'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed',
                '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
                *integer.receive(), 'S_received.RESULT = KNOWN pvalue_changed',
                '$weakref_get(S_received, n_reader_weak) = PNULL']
        elif group == 'inner-getter':
            clauses += ['$concat_emit_left(pframe_get.TODO) = (poperand_left)',
                'poperand_left = VARIABLE ($ptascii("prefix")) z_prefix',
                'S_global_return = $global_table_view(S_return)',
                '$trace_slot(S_global_return, S_global_return.ENV, $ptascii("prefix")) = pvalue_prefix',
                '$string_bytes(pvalue_prefix) = ($ptascii("changed|"))',
                *emit('S_return', 'S_outer', 'changed|ok|tail|')]
        clauses += get.finish('S_return' if group == 'reference-kept' else 'S_received' if group == 'reference-drop' else 'S_outer_after' if group == 'inner-getter' else 'S_received', expected)
    if group == 'reference-kept':
        # Constructed abrupt consumer control, separate from original-source agreement.
        clauses += ['S_bad = S_emit[.RESULT = KNOWN (POBJECT n_reader)]',
            '~$user_string_value(S_bad, POBJECT n_reader)',
            'S_bad_text = $stringify(S_bad, POBJECT n_reader, z_emit)',
            'S_bad_text.COMPLETION = THROWN "Error" ptbytes_bad z_emit',
            'PhpStep: S_bad ~> S_bad_after',
            'S_bad_after = S_bad_text[.TODO = eps]',
            'S_bad_after.BASE = S_emit.BASE']
    if group != 'source-conflict':
        clauses += ['$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 1',
            '$trace_slot(S_done, S_done.ENV, $ptascii("readerDrops")) = PINT 1']
    return clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-concat-emit-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- '+('' if clause.startswith('PhpStep:') else 'if ')+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(state_assertions=len(clauses), source_sha256=cross.invoke.sha(source),
                      fixture_sha256=cross.invoke.sha(fixture), helper_sha256=cross.invoke.sha(Path(__file__)))
        if not args.prepare_only:
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            report['numeric_runner_sha256'] = cross.invoke.sha(runner)
            assert report['numeric_runner_sha256'] == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            modules = before['ordered_modules']
            result = cross.invoke.process([str(runner), '--sl', *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
