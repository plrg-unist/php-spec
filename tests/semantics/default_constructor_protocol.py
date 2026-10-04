#!/usr/bin/env python3
"""Source-reached constant-AST constructor ownership and forged continuations."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from default_constructor_sources import CASES, ROOT
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $default_protocol_is_output(pevent) : bool
def $default_protocol_is_output(OUTPUT ptbytes) = true
def $default_protocol_is_output(pevent) = false -- otherwise
dec $default_protocol_output(pevent*) : ptbytes
def $default_protocol_output(eps) = eps
def $default_protocol_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $default_protocol_output(pevent*)
def $default_protocol_output(pevent :: pevent_tail*) = $default_protocol_output(pevent_tail*)
  -- if ~$default_protocol_is_output(pevent)
dec $default_protocol_phase(pstate,nat) : bool
def $default_protocol_phase(S,0) = true
  -- if S.TODO = (CLASS_CONST_CONSTRUCT ptbytes phpType7* true z) :: ptask_tail*
def $default_protocol_phase(S,1) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 0
def $default_protocol_phase(S,2) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = |pdefaultnew.ARGUMENTS| /\ $(pdefaultnew.INDEX > 0)
def $default_protocol_phase(S,3) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DEFAULT_CTOR_REF_RESULT pdefaultctor
def $default_protocol_phase(S,4) = true
  -- if S.TODO = (DEFAULT_CTOR_ARGS pdefaultctor) :: ptask_tail*
  -- if pdefaultctor.INDEX = 1
def $default_protocol_phase(S,5) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = pdefaultctor.FUNCTION
def $default_protocol_phase(S,6) = true
  -- if S.TODO = [DEFAULT_BIND porigin n]
  -- if S.RESULT = KNOWN (POBJECT n_object)
def $default_protocol_phase(S,7) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if pcallcontext.NAME = $ptascii("g")
def $default_protocol_phase(S,n) = false -- otherwise
dec $default_protocol_seek(pstate,nat,nat) : pstate
def $default_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $default_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $default_protocol_phase(S,n_phase)
def $default_protocol_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$default_protocol_phase(S,n_phase)
def $default_protocol_seek(S,n_phase,n) = $default_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$default_protocol_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $default_protocol_seek({parent},{phase},4096)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$default_protocol_phase({state},{phase})', *valid(state)]


def reject(name, expression):
    return [f'S_bad_{name} = {expression}', f'$heap_valid($heap_graph(S_bad_{name}))',
            f'~$call_descriptors_valid(S_bad_{name})']


def assertions(initial, ordinary_initial):
    clauses = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_cold', 0),
        'S_cold.TODO = (CLASS_CONST_CONSTRUCT ptbytes_class phpType7* true z) :: ptask_cold*',
        r'ptbytes_class = $ptascii("C") /\ z = 12',
        'S_cold.CONSTCONTEXT = (pconstantcontext)',
        'pconstantcontext.LINE = z',
        '$default_protocol_output(S_cold.EVENTS) = $ptascii("D|")',
        *reject('cold_line', 'S_cold[.TODO = (CLASS_CONST_CONSTRUCT ptbytes_class phpType7* true $(z + 1)) :: ptask_cold*]'),
        *reject('cold_class', 'S_cold[.TODO = (CLASS_CONST_CONSTRUCT $ptascii("V") phpType7* true z) :: ptask_cold*]'),
        *seek('S_cold', 'S_allocated', 1),
        'S_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew_allocated) :: ptask_allocated*',
        r'pdefaultnew_allocated.CLASS = ptbytes_class /\ pdefaultnew_allocated.LINE = z',
        'pdefaultnew_allocated.VALUES = eps',
        '$heap_owners($heap_graph(S_allocated),HOBJECT pdefaultnew_allocated.OBJECT) = 1',
        *reject('allocated_line', 'S_allocated[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_allocated[.LINE = $(z + 1)]) :: ptask_allocated*]'),
        *reject('allocated_index', 'S_allocated[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_allocated[.INDEX = 1]) :: ptask_allocated*]'),
        *reject('allocated_class', 'S_allocated[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_allocated[.CLASS = $ptascii("V")]) :: ptask_allocated*]'),
        'S_missing_owner = S_allocated[.TODO = ptask_allocated*]',
        '$heap_owners($heap_graph(S_missing_owner),HOBJECT pdefaultnew_allocated.OBJECT) = 0',
        *seek('S_allocated', 'S_values', 2),
        'S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values) :: ptask_values*',
        'pdefaultnew_values.SITE = pdefaultnew_allocated.SITE',
        'pdefaultnew_values.OBJECT = pdefaultnew_allocated.OBJECT',
        'pdefaultnew_values.INDEX = 2',
        'pdefaultnew_values.VALUES = [POBJECT n_value,PINT 1]',
        '$default_protocol_output(S_values.EVENTS) = $ptascii("D|")',
        '$heap_owners($heap_graph(S_values),HOBJECT n_value) = 1',
        *reject('values_object', 'S_values[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values[.OBJECT = n_value]) :: ptask_values*]'),
        *reject('values_site', 'S_values[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values[.SITE = pconstantcontext.ORIGIN]) :: ptask_values*]'),
        *reject('values_index', 'S_values[.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values[.INDEX = 1]) :: ptask_values*]'),
        *seek('S_values', 'S_warning', 3),
        'S_warning.CURRENT = (pcallcontext_handler)',
        'S_warning.FRAMES = pframe_warning :: pframe_warning_tail*',
        'pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DEFAULT_CTOR_REF_RESULT pdefaultctor_warning',
        r'perrorcall.SITE = pdefaultnew_values.SITE /\ perrorcall.LINE = z /\ perrorcall.LEVEL = 2',
        r'pdefaultctor_warning.NEW = pdefaultnew_values /\ pdefaultctor_warning.INDEX = 0',
        'pdefaultctor_warning.PREPARED.SLOTS = eps',
        '$error_context_kind(S_warning,pcallcontext_handler)',
        '~$default_ctor_context_kind(S_warning,pcallcontext_handler)',
        '$heap_owners($heap_graph(S_warning),HOBJECT n_value) = 1',
        *reject('warning_line', 'S_warning[.FRAMES = pframe_warning[.TODO = (ERROR_HANDLER_RESULT perrorcall[.LINE = $(z + 1)]) :: ptask_warning*] :: pframe_warning_tail*]'),
        *reject('warning_resume', 'S_warning[.FRAMES = pframe_warning[.TODO = (ERROR_HANDLER_RESULT perrorcall[.RESUME = DEFAULT_CTOR_REF_RESULT pdefaultctor_warning[.INDEX = 1]]) :: ptask_warning*] :: pframe_warning_tail*]'),
        *seek('S_warning', 'S_wrapped', 4),
        'S_wrapped.TODO = (DEFAULT_CTOR_ARGS pdefaultctor_wrapped) :: ptask_wrapped*',
        'pdefaultctor_wrapped.NEW = pdefaultnew_values',
        'pdefaultctor_wrapped.PREPARED.SLOTS = [NAMED_SENT (REFERENCE n_cell)]',
        'S_wrapped.STORE[n_cell] = DEFINED (POBJECT n_value)',
        r'(HCELL n_cell) <- S_wrapped.ALLOCATIONS /\ n_cell <- S_wrapped.REFCELLS',
        '$heap_owners($heap_graph(S_wrapped),HCELL n_cell) = 1',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_value) = 2',
        'pnamedargs_wrong = pdefaultctor_wrapped.PREPARED[.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_value))]]',
        *reject('wrapped_mode', 'S_wrapped[.TODO = (DEFAULT_CTOR_ARGS pdefaultctor_wrapped[.PREPARED = pnamedargs_wrong]) :: ptask_wrapped*]'),
        *seek('S_wrapped', 'S_entered', 5),
        'S_entered.CURRENT = (pcallcontext_ctor)',
        'S_entered.FRAMES = pframe_ctor :: pframe_ctor_tail*',
        'pframe_ctor.TODO = (DEFAULT_CTOR_RESULT pdefaultctor_entered) :: ptask_ctor*',
        r'pdefaultctor_entered.NEW = pdefaultnew_values /\ pdefaultctor_entered.INDEX = 2',
        r'pcallcontext_ctor.CALLSITE = (pdefaultnew_values.SITE) /\ pcallcontext_ctor.LINE = z',
        'pcallcontext_ctor.TARGET = METHOD_TARGET pdefaultnew_values.OBJECT pdefaultctor_entered.FUNCTION',
        '$default_ctor_context_kind(S_entered,pcallcontext_ctor)',
        *reject('entered_line', 'S_entered[.CURRENT = (pcallcontext_ctor[.LINE = $(z + 1)])]'),
        *reject('entered_target', 'S_entered[.CURRENT = (pcallcontext_ctor[.TARGET = METHOD_TARGET n_value pdefaultctor_entered.FUNCTION])]'),
        *reject('entered_missing_owner', 'S_entered[.FRAMES = pframe_ctor[.TODO = ptask_ctor*] :: pframe_ctor_tail*]'),
        *seek('S_entered', 'S_binding', 6),
        'S_binding.TODO = [DEFAULT_BIND porigin_receiver n_receiver]',
        'S_binding.RESULT = KNOWN (POBJECT pdefaultnew_values.OBJECT)',
        'S_binding.CONSTCONTEXT = (pconstantcontext_binding)',
        '$constant_fact_at(pconstantcontext_binding.FACTS,pdefaultnew_values.SITE) = (pconstantfact_binding)',
        r'pconstantfact_binding.VALUE = eps /\ pconstantfact_binding.CLASS = PVOBJECT',
        '$function_at($all_functions(S_binding),porigin_receiver) = (pfunction_receiver)',
        '$default_at(pfunction_receiver.DEFAULTS,n_receiver) = (pdefault_receiver)',
        '$constant_class(S_binding,pdefault_receiver.ORIGIN) = PVOBJECT',
        '$default_cache_at(S_binding.DEFAULTCACHE,pdefault_receiver.ORIGIN) = eps',
        'S_uncached = $default_cache_value(S_binding[.CONSTCONTEXT = eps],pdefault_receiver.ORIGIN,POBJECT pdefaultnew_values.OBJECT,PVOBJECT)',
        '$default_cache_at(S_uncached.DEFAULTCACHE,pdefault_receiver.ORIGIN) = eps',
        '$default_string_candidate(S_uncached,pfunction_receiver,n_receiver,POBJECT pdefaultnew_values.OBJECT)',
        'S_done = $drive_steps(S_binding,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$default_protocol_output(S_done.EVENTS) = $ptascii("D|W|T|C1|S|F|v")',
        r'S_done.PARAMETERBACKINGS = eps /\ S_done.REFCOERCIONS = eps /\ S_done.HELD = eps',
        '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pdefaultnew_values.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HCELL n_cell) <- S_done.ALLOCATIONS)', *valid('S_done'),
        'S_ordinary_initial = ' + ordinary_initial,
        '~S_ordinary_initial.COMPILESTOP',
        *seek('S_ordinary_initial', 'S_ordinary', 7),
        'S_ordinary.CURRENT = (pcallcontext_ordinary)',
        r'pcallcontext_ordinary.ARGC = 2 /\ pcallcontext_ordinary.HOLES = eps',
        '~$default_ctor_context_kind(S_ordinary,pcallcontext_ordinary)',
        'S_forged = S_ordinary[.TODO = [NAMED_PREFLIGHT pcallcontext_ordinary.FUNCTION 0]]',
        '$heap_valid($heap_graph(S_forged))',
        '~$default_ctor_context_valid(S_forged,pcallcontext_ordinary)',
        '~$named_preflight_stage(S_forged,pcallcontext_ordinary.FUNCTION,0)',
        '~$call_descriptors_valid(S_forged)',
        'S_ordinary_done = $drive_steps(S_ordinary,4096)',
        r'S_ordinary_done.COMPLETION = NORMAL /\ S_ordinary_done.TODO = eps /\ S_ordinary_done.CURRENT = eps /\ S_ordinary_done.FRAMES = eps',
        '$default_protocol_output(S_ordinary_done.EVENTS) = $ptascii("G|3")',
        *valid('S_ordinary_done')]
    return clauses


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='default-constructor-owner-', dir=ROOT / '.tools'))
    source = out / 'owned-phases.php'
    source.write_bytes(CASES['owned-phases'])
    ordinary = out / 'ordinary-positional-control.php'
    ordinary.write_bytes(CASES['ordinary-positional-control'])
    report = {'passed': False, 'head': before['identity']['head'], 'before': before,
              'source_sha256': sha(source), 'profile': cross.invoke.types.PROFILE,
              'ordinary_sha256': sha(ordinary),
              'mode': 'unused' if args.elaborate_only else 'source-reached'}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        parsed_ordinary = frontend.request({'op': 'parse', 'source': base64.b64encode(ordinary.read_bytes()).decode()})
        assert parsed_ordinary['accepted'] is True
        checked_ordinary = adapter.request({'op': 'check', 'ast': parsed_ordinary['ast'], 'fixture': True})
        assert checked_ordinary['ok'] is True
        initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        ordinary_initial = '$php_run(program_ordinary,0,' + json.dumps(base64.b64encode(os.fsencode(ordinary)).decode()) + ')'
        clauses = ['program_source = ' + checked['fixture'], 'program_ordinary = ' + checked_ordinary['fixture'], *assertions(initial, ordinary_initial)]
        (out / 'assertions.json').write_text(json.dumps(clauses, indent=2) + '\n')
        body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses)
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = ' +
                           ('true' if args.elaborate_only else '$body()') + '\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            *[str(ROOT / module) for module in modules], str(fixture)], out / 'numeric', 120, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(clauses), fixture_sha256=sha(fixture),
            state_assertions_evaluated=0 if args.elaborate_only else len(clauses),
            unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
