#!/usr/bin/env python3
"""Source-reached captured element/default authority and receive cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
from variadic_string_parameters import CASES, EXPECTED, ROOT, driver, inputs, sha

STAGES = ['positional-reference-backing', 'variadic-same-object-reentry',
          'inherited-named-hole-default', 'unpacked-hole-default',
          'required-hole-before-conversion', 'variadic-attach-throw']
PREFIX = r'''
dec $variadic_protocol_is_output(pevent) : bool
def $variadic_protocol_is_output(OUTPUT ptbytes) = true
def $variadic_protocol_is_output(pevent) = false -- otherwise
dec $variadic_protocol_output(pevent*) : ptbytes
def $variadic_protocol_output(eps) = eps
def $variadic_protocol_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $variadic_protocol_output(pevent*)
def $variadic_protocol_output(pevent :: pevent_tail*) = $variadic_protocol_output(pevent_tail*)
  -- if ~$variadic_protocol_is_output(pevent)
dec $variadic_protocol_is_new(pcnode) : bool
def $variadic_protocol_is_new(NExprNew phpType28 phpType6 metadata) = true
def $variadic_protocol_is_new(pcnode) = false -- otherwise
dec $variadic_protocol_new_site(pcoccurrence*) : pcpath?
def $variadic_protocol_new_site(eps) = eps
def $variadic_protocol_new_site((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*) = (pcpath)
  -- if $variadic_protocol_is_new(pcnode)
def $variadic_protocol_new_site((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*) = $variadic_protocol_new_site(pcoccurrence*)
  -- if ~$variadic_protocol_is_new(pcnode)
dec $variadic_protocol_phase(pstate,nat) : bool
def $variadic_protocol_phase(S,0) = $variadic_string_candidate(S)
def $variadic_protocol_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring]
def $variadic_protocol_phase(S,2) = true
  -- if S.TODO = [VARIADIC_STRING_RESULT pvariadicstring]
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $variadic_protocol_phase(S,3) = true
  -- if $variadic_protocol_phase(S,1)
  -- if S.FRAMES = pframe_new :: pframe_converter :: pframe_old :: pframe_tail*
  -- if pframe_old.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring_old]
def $variadic_protocol_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = [STRINGIFY_RESULT n_object porigin_site z,DEFAULT_STRING_RESULT pparameterstring]
def $variadic_protocol_phase(S,5) = true
  -- if S.TODO = [DEFAULT_STRING_RESULT pparameterstring]
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $variadic_protocol_phase(S,6) = true
  -- if S.TODO = [THROW_SEARCH n_throw,STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring]
def $variadic_protocol_phase(S,7) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin n]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.HOLES = [0]
def $variadic_protocol_phase(S,n) = false -- otherwise
dec $variadic_protocol_seek(pstate,nat,nat) : pstate
def $variadic_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $variadic_protocol_seek(S,n_phase,n) = S
  -- if $variadic_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $variadic_protocol_seek(S,n_phase,0) = S
  -- if ~$variadic_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $variadic_protocol_seek(S,n_phase,n) = $variadic_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$variadic_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $variadic_protocol_seek({parent},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$variadic_protocol_phase({state},{phase})']


def step(parent, state):
    return [f'{state}_found = $drive_steps({parent},1)',
            f'{state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]']


def terminal(parent, name):
    text = '$base64(' + json.dumps(base64.b64encode(EXPECTED[name]).decode()) + ')'
    return [f'S_done = $drive_steps({parent},4096)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            'S_done.HELD = eps', '$variadic_protocol_output(S_done.EVENTS) = ' + text,
            *valid('S_done')]


def checks(initial, name):
    clauses = ['S_initial = ' + initial]
    if name == 'required-hole-before-conversion':
        return clauses + [*seek('S_initial', 'S_hole', 7),
            'S_hole.CURRENT = (pcallcontext_receive)',
            'pcallcontext_receive.ARGC = 2 /\\ pcallcontext_receive.HOLES = [0]',
            '$function_at($all_functions(S_hole),pcallcontext_receive.FUNCTION) = (pfunction)',
            '$default_at(pfunction.DEFAULTS,0) = eps',
            '$call_holes_valid(S_hole,pcallcontext_receive)',
            '~$fixed_parameter_supplied(S_hole,0)',
            '$fixed_parameter_supplied(S_hole,1)',
            '$variadic_protocol_output(S_hole.EVENTS) = eps',
            *valid('S_hole'), *terminal('S_hole', name),
            'S_done.PARAMETERBACKINGS = eps /\\ S_done.REFCOERCIONS = eps']
    if name == 'variadic-same-object-reentry':
        return clauses + [*seek('S_initial', 'S_nested', 3),
            'S_nested.FRAMES = pframe_new :: pframe_converter :: pframe_old :: pframe_tail*',
            'pframe_new.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring_new]',
            'pframe_old.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring_old]',
            'pvariadicstring_new.OPERAND = REFERENCE n_new',
            'pvariadicstring_old.OPERAND = REFERENCE n_old',
            'n_new =/= n_old /\\ pvariadicstring_new.OBJECT = pvariadicstring_old.OBJECT',
            '$receive_string_same_owner(VARIADIC_STRING_RESULT pvariadicstring_new,VARIADIC_STRING_RESULT pvariadicstring_old)',
            '$receive_string_scope_valid(S_nested,VARIADIC_STRING_RESULT pvariadicstring_new)',
            '$receive_string_scope_valid($parameter_string_frame_scope(S_nested,pframe_old,pframe_tail*),VARIADIC_STRING_RESULT pvariadicstring_old)',
            '~$receive_string_scope_valid(S_nested,VARIADIC_STRING_RESULT pvariadicstring_new[.OPERAND = REFERENCE n_old])',
            'S_mixed = S_nested[.FRAMES = pframe_new[.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring_new[.OPERAND = REFERENCE n_old]]] :: pframe_converter :: pframe_old :: pframe_tail*]',
            '~$call_descriptors_valid(S_mixed)',
            '$stringify_chain_valid(S_nested,S_nested.CURRENT,S_nested.FRAMES)',
            *valid('S_nested'), *terminal('S_nested', name),
            '$parameter_backing_at(S_done.PARAMETERBACKINGS,n_new) = (pparameterbacking_new)',
            '$parameter_backing_at(S_done.PARAMETERBACKINGS,n_old) = (pparameterbacking_old)',
            'pparameterbacking_new.VALUE = $ptascii("s") /\\ pparameterbacking_old.VALUE = $ptascii("s")',
            '|S_done.PARAMETERBACKINGS| = 2 /\\ S_done.REFCOERCIONS = eps',
            '$heap_count(HCELL n_new,$heap_graph(S_done).ROOTS) = 2 /\\ $heap_owners($heap_graph(S_done),HCELL n_new) = 2',
            '$heap_count(HCELL n_old,$heap_graph(S_done).ROOTS) = 2 /\\ $heap_owners($heap_graph(S_done),HCELL n_old) = 2',
            '$heap_count(HOBJECT n_object,$heap_graph(S_done).ROOTS) = 0 /\\ $heap_owners($heap_graph(S_done),HOBJECT n_object) = 1']
    if name in ['inherited-named-hole-default', 'unpacked-hole-default']:
        clauses += [*seek('S_initial', 'S_entered', 4),
            'S_entered.CURRENT = (pcallcontext_converter)',
            'S_entered.FRAMES = pframe_receive :: pframe_tail*',
            'pframe_receive.CONTEXT = (pcallcontext_receive)',
            'pframe_receive.TODO = [STRINGIFY_RESULT n_object porigin_site z,DEFAULT_STRING_RESULT pparameterstring]',
            'pcallcontext_receive.ARGC = 2 /\\ pcallcontext_receive.HOLES = [0]',
            'pcallcontext_converter.ARGC = 0 /\\ pcallcontext_converter.HOLES = eps /\\ pcallcontext_converter.RECEIVER = (n_object)',
            'pframe_receive.LOCALS = (psymboltable_receive)',
            '$lookup(psymboltable_receive.ENV,$ptascii("s")) = (pparameterstring.CELL)',
            '$receive_string_scope_valid(S_entered,DEFAULT_STRING_RESULT pparameterstring)',
            'S_owner = $parameter_string_frame_scope(S_entered,pframe_receive,pframe_tail*)',
            '$fixed_parameter_defaulted(S_owner,0) /\\ ~$fixed_parameter_supplied(S_owner,0)',
            '$fixed_parameter_supplied(S_owner,1)',
            '~$parameter_string_scope_valid(S_owner,pparameterstring)',
            '~$receive_string_scope_valid(S_owner,DEFAULT_STRING_RESULT pparameterstring[.CELL = $(|S_owner.STORE| + 1)])',
            '~$call_holes_valid(S_owner,pcallcontext_receive[.HOLES = [0,0]])',
            '~$call_holes_valid(S_owner,pcallcontext_receive[.HOLES = [2]])',
            '$function_at($all_functions(S_owner),pparameterstring.FUNCTION) = (pfunction)',
            '$class_method_origin(S_owner.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
            '$class_at(S_owner.CLASSES,pmethoddesc.OWNER) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            'S_owner.OBJECTS[n_object] = INSTANCE pclassdesc_owner.ORIGIN',
            '$effective_method(S_owner,pclassdesc_owner.ORIGIN,$ptascii("__construct"),|S_owner.CLASSES|) = eps',
            'pcallcontext_receive.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
            'pcallcontext_receive.CALLED_CLASS = (porigin_called)',
            '$class_at(S_owner.CLASSES,porigin_called) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("D")',
            '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
            'pdefault.KIND = PDDEFERRED',
            'P_site = $ppstart(0,program_source,$ptascii("parameter.php"))',
            'P_site.COMPLETION = PPCNORMAL',
            'pdefault.ORIGIN = PORIGIN n_unit pcpath_new',
            '$ppparameter_new_site(P_site[.FOLD.DEFAULT = true],pcpath_new)',
            '~$ppparameter_new_site(P_site[.FOLD.DEFAULT = false],pcpath_new)',
            '$default_cache_at(S_owner.DEFAULTCACHE,pdefault.ORIGIN) = eps',
            '$default_cacheable(PVOBJECT) = false',
            '$constant_value_class_valid(S_owner,POBJECT n_object,PVOBJECT)',
            '$stringify_context_frame_valid(S_owner,pcallcontext_converter,pframe_receive)',
            *valid('S_entered'), *seek('S_entered', 'S_result', 5),
            'S_result.TODO = [DEFAULT_STRING_RESULT pparameterstring]',
            'S_result.RESULT = KNOWN (PSTRING $base64("dgByYXc="))',
            'S_supplied = S_result[.TODO = [PARAMETER_STRING_RESULT pparameterstring]]',
            '~$parameter_string_scope_valid(S_supplied,pparameterstring)',
            '~$parameter_backing_admission(S_supplied,pparameterstring,$base64("dgByYXc="))',
            '~$receive_backing_admission(S_result,DEFAULT_STRING_RESULT pparameterstring,pparameterstring.CELL,$base64("dgByYXc="))',
            *valid('S_result'), *terminal('S_result', name),
            'S_done.PARAMETERBACKINGS = eps /\\ S_done.REFCOERCIONS = eps',
            '~((HCELL pparameterstring.CELL) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = eps']
        if name == 'inherited-named-hole-default':
            clauses += ['~$call_holes_valid(S_owner,pcallcontext_receive[.HOLES = eps])']
        else:
            clauses += ['$call_unpack_site(S_owner,pcallcontext_receive.CALLSITE)']
        return clauses
    clauses += [*seek('S_initial', 'S_begin', 0), *valid('S_begin'),
        *seek('S_begin', 'S_entered', 1),
        'S_entered.CURRENT = (pcallcontext_converter)',
        'S_entered.FRAMES = pframe_receive :: pframe_tail*',
        'pframe_receive.CONTEXT = (pcallcontext_receive)',
        'pframe_receive.TODO = [STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring]',
        'pvariadicstring.OPERAND = REFERENCE n_cell',
        'pvariadicstring.INDEX = 0 /\\ pvariadicstring.ELEMENT = 0 /\\ ~pvariadicstring.NAMED',
        'pcallcontext_receive.EXTRA[0] = REFERENCE n_cell',
        'pcallcontext_converter.ARGC = 0 /\\ pcallcontext_converter.RECEIVER = (n_object)',
        '$receive_string_scope_valid(S_entered,VARIADIC_STRING_RESULT pvariadicstring)',
        '~$receive_string_scope_valid(S_entered,VARIADIC_STRING_RESULT pvariadicstring[.OPERAND = KNOWN (POBJECT n_object)])',
        '~$receive_string_scope_valid(S_entered,VARIADIC_STRING_RESULT pvariadicstring[.ELEMENT = 1])',
        '~$receive_string_scope_valid(S_entered,VARIADIC_STRING_RESULT pvariadicstring[.NAMED = true])',
        '~$receive_string_scope_valid(S_entered,VARIADIC_STRING_RESULT pvariadicstring[.LINE = $(pvariadicstring.LINE + 1)])',
        '~$receive_string_scope_valid(S_entered[.SOURCES = eps],VARIADIC_STRING_RESULT pvariadicstring)',
        *valid('S_entered')]
    if name == 'variadic-attach-throw':
        return clauses + [*seek('S_entered', 'S_throw', 6),
            'S_throw.TODO = [THROW_SEARCH n_throw,STRINGIFY_RESULT n_object porigin_site z,VARIADIC_STRING_RESULT pvariadicstring]',
            'S_throw.OBJECTS[n_throw] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception" /\\ $throwable_previous_id(S_throw,n_throw) = eps',
            'S_throw.STORE[n_cell] = DEFINED (POBJECT n_replacement)',
            'n_replacement =/= n_object',
            '$propref_at(S_throw.PROPREFS,n_cell) = (ppropref)',
            'S_throw.PARAMETERBACKINGS = eps /\\ S_throw.REFCOERCIONS = eps',
            '$receive_string_scope_valid(S_throw,VARIADIC_STRING_RESULT pvariadicstring)',
            '~$receive_backing_admission(S_throw,VARIADIC_STRING_RESULT pvariadicstring,n_cell,$ptascii("s"))',
            *valid('S_throw'), *terminal('S_throw', name),
            'S_done.PARAMETERBACKINGS = eps /\\ S_done.REFCOERCIONS = eps',
            '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_replacement) <- S_done.ALLOCATIONS',
            '$heap_count(HCELL n_cell,$heap_graph(S_done).ROOTS) = 2 /\\ $heap_owners($heap_graph(S_done),HCELL n_cell) = 2',
            '$heap_count(HOBJECT n_replacement,$heap_graph(S_done).ROOTS) = 0 /\\ $heap_owners($heap_graph(S_done),HOBJECT n_replacement) = 1']
    return clauses + [*seek('S_entered', 'S_result', 2),
        'S_result.TODO = [VARIADIC_STRING_RESULT pvariadicstring]',
        'S_result.RESULT = KNOWN (PSTRING $base64("dgByYXc="))',
        '$propref_at(S_result.PROPREFS,n_cell) = (ppropref)',
        'ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid]',
        'P_site = $ppstart(0,program_source,$ptascii("parameter.php"))',
        'P_site.COMPLETION = PPCNORMAL',
        '$variadic_protocol_new_site(P_site.FOLD.SOURCE.OCCURRENCES) = (pcpath_new)',
        '~$ppparameter_new_site(P_site[.FOLD.DEFAULT = true],pcpath_new)',
        '$class_static_at(S_result.CLASSSTATICS,ppropertyid) = (pclassstatic)',
        'pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)',
        '$receive_backing_admission(S_result,VARIADIC_STRING_RESULT pvariadicstring,n_cell,$base64("dgByYXc="))',
        '~$receive_backing_admission(S_result[.COMPLETION = THROWN "Exception" $ptascii("stop") 1],VARIADIC_STRING_RESULT pvariadicstring,n_cell,$base64("dgByYXc="))',
        '~$receive_backing_admission(S_result,VARIADIC_STRING_RESULT pvariadicstring,n_cell,$ptascii("forged"))',
        *valid('S_result'), *step('S_result', 'S_stored'),
        '$parameter_backing_at(S_stored.PARAMETERBACKINGS,n_cell) = (pparameterbacking)',
        'pparameterbacking = {FUNCTION pvariadicstring.FUNCTION, INDEX pvariadicstring.INDEX, CELL n_cell, LINE pvariadicstring.LINE, VALUE $base64("dgByYXc=")}',
        '$parameter_backing_row_valid(S_stored,pparameterbacking)',
        'S_stored.STORE[n_cell] = DEFINED (PSTRING $base64("dgByYXc="))',
        'S_stored.CURRENT = (pcallcontext_receive)',
        'S_stored.TODO = [VARIADIC_RECEIVE pvariadicstring.FUNCTION 1]',
        '$lookup(S_stored.ENV,$ptascii("xs")) = (n_array_cell)',
        'S_stored.STORE[n_array_cell] = DEFINED (PARRAY n_array)',
        '$entry_lookup(S_stored.ARRAYS[n_array].ITEMS,KINT 0) = (ALIAS n_cell)',
        *valid('S_stored'), *terminal('S_stored', name),
        'S_done.PARAMETERBACKINGS = eps /\\ S_done.REFCOERCIONS = eps',
        '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact stage IDs')
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else STAGES
    assert selected and len(selected) == len(set(selected)) and all(n in STAGES for n in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs(args.freeze)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    out = Path(tempfile.mkdtemp(prefix='variadic-string-parameters-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': driver.types.PROFILE, 'state_assertions_evaluated': 0,
              'unused_body_assertions': 0, 'mode': 'unused' if args.elaborate_only else 'source-reached'}
    frontend = adapter = None
    unused = []
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *driver.types.FLAGS, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            row = {'id': name, 'source_sha256': sha(path), 'completed': False, 'passed': False}
            report['records'].append(row)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')'
            clauses = ['program_source = ' + checked['fixture'], *checks(initial, name)]
            (directory / 'assertions.json').write_text(json.dumps(clauses, indent=2) + '\n')
            body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses)
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = $body()\n')
            row.update(assertions=len(clauses), fixture_sha256=sha(fixture))
            if args.elaborate_only:
                unused.append(body.replace('$body', '$unused_' + str(len(unused))))
                report['unused_body_assertions'] += len(clauses)
            else:
                result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    *[str(ROOT / module) for module in modules], str(fixture)], directory / 'numeric', 120, ROOT)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                report['state_assertions_evaluated'] += len(clauses)
                row['passed'] = True
            row['completed'] = True
            print(name, 'prepared' if args.elaborate_only else 'pass', len(clauses), flush=True)
        if args.elaborate_only:
            fixture = out / 'all-unused.watsup'
            fixture.write_text(PREFIX + '\n'.join(unused) + '\ndec $main() : bool\ndef $main() = true\n')
            result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT / module) for module in modules], str(fixture)], out / 'unused-numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report['result'] = 'prepared' if args.elaborate_only else 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        cleanup = []
        for worker in [adapter, frontend]:
            if worker is not None:
                try:
                    worker.close()
                except BaseException as error:
                    cleanup.append({'type': type(error).__name__, 'message': str(error)})
        report['cleanup_errors'] = cleanup
        report['after_inputs'] = inputs(args.freeze)
        if cleanup or report['after_inputs'] != before:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == ('prepared' if args.elaborate_only else 'pass')


if __name__ == '__main__':
    main()
