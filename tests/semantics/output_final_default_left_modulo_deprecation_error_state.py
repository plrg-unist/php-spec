#!/usr/bin/env python3
"""Precision-only left MOD notices preserve original reads and FINAL cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_cv_modulo_conversion_error_state as shared
import output_final_default_constant_modulo_warning_error_state as constant
import output_final_default_left_cv_modulo_warning_error_state as left_cv
import output_final_default_right_cv_modulo_conversion_error_state as right_cv
import output_final_default_left_modulo_deprecation_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = shared.division
prior = shared.prior
PREFIX = shared.PREFIX
CASES = {name: sources.CASES['native-default-left-modulo-deprecation-error-' + name]
         for name in ['constant-string', 'left-cv-string', 'right-cv-float', 'cv-pair-string']}
ERROR = shared.ERROR
CAPTURE = shared.CAPTURE


def shape(name):
    form, kind = name.rsplit('-', 1)
    cells = [side for side in ['left', 'right'] if form == side + '-cv' or form == 'cv-pair']
    return form, kind, 6 + len(cells), cells


def message(kind):
    value = b'float-string "1.5"' if kind == 'string' else b'float 1.5'
    return b'Implicit conversion from ' + value + b' to int loses precision'


def bindings_for(name, fixture, path):
    form, _, _, cells = shape(name)
    base, case = {'constant': (constant, 'float-string'), 'left-cv': (left_cv, 'float-prefix'),
                  'right-cv': (right_cv, 'both'), 'cv-pair': (shared.previous, 'string-zero')}[form]
    bindings, checks = base.lifecycle(case, fixture, path)
    bindings = [binding for binding in bindings if 'n_cell_other' not in binding and 'S_other' not in binding]
    checks = [(label, r' /\ '.join(part for part in condition.split(r' /\ ') if 'n_cell_other' not in part))
              for label, condition in checks]
    if form == 'constant':
        checks = [checks[0], *checks[2:]]
        bindings.insert(bindings.index('S_left = $resolve_at($hold_task_inputs(S), KNOWN pvalue_left, z)'),
                        'pvalue_right = PINT 0')
    else:
        checks = checks[:4]
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('S_warned = '))
    bindings[index] = 'S_warned = $integer_coerce(S, pvalue_left, z)'
    bindings.insert(index, '$integer_conversion(pvalue_left) = (pintegerconversion)')
    old_error = [binding for binding in bindings if binding.startswith('pobreturnerror = ')]
    assert len(old_error) == 1
    bindings.remove(old_error[0])
    index = bindings.index('S_capture_found = $drive_steps(S, 1)')
    bindings[index:index] = [
        'S_generated.COMPLETION = THROWING n_exception', ERROR,
        'pobobjectreturn_seed = pobobjectreturn[.SOURCE = $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))]',
        'S_seed = $ob_object_final_capture(S_generated, pobobjectreturn, pobobjectreturn_seed.SOURCE)',
        'S_seed_post = $literal_reference_debt_step(S, $sensitive_trace_freeze(S_seed))']
    if cells:
        old_seek = prior.seek('S_exit', 'S_capture', 1)
        index = bindings.index(old_seek[0])
        assert bindings[index:index + len(old_seek)] == old_seek
        bindings[index:index + len(old_seek)] = [
            *prior.seek('S_leave', 'S_capture', 8),
            'S_queue_found = $drive_steps(S_leave, 1)', 'S_queue_found.COMPLETION = BUDGET',
            'S_queue = S_queue_found[.COMPLETION = NORMAL]',
            'S_queue.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
            *prior.seek('S_exit', 'S_queue', 1)]
    return bindings, checks


def original(name):
    form, kind, line, cells = shape(name)
    left = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))' if kind == 'string' else 'PFLOAT 4609434218613702656'
    operand = 'VARIABLE n_left* z_left' if 'left' in cells else 'KNOWN pvalue_left'
    cvs = '[' + ', '.join('$ptascii("' + side + '")' for side in cells) + ']' if cells else 'eps'
    conditions = [
        f'z = {line}', f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {len(cells)}',
        f'pvalue_left = {left}', 'pvalue_right = PINT 0',
        '$integer_conversion(pvalue_left) = (pintegerconversion)', 'pintegerconversion.VALUE = 1',
        'pintegerconversion.NOTICES = [(8192, ' + prior.value(message(kind)) + ')]',
        '$ob_object_modulo_integer(pvalue_left) = eps', '$long_convertible(pvalue_left)',
        '$ob_object_modulo_integer(pvalue_right) = (0)',
        f'$ob_object_error_operand_value(S, {operand}, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        f'$integer_operand_source(S, porigin_operator, [PCFIELD 0], {operand})',
        '$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT)',
        f'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], {operand}) = ' + ('(8)' if 'left' in cells else '(1)'),
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = ' + ('(8)' if 'right' in cells else '(1)'),
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})',
        'S_left.RESULT = KNOWN pvalue_left', 'S_right.RESULT = KNOWN pvalue_right',
        'S_left.EVENTS = S.EVENTS', 'S_right.EVENTS = S.EVENTS',
        'S_integer_left.COMPLETION = NORMAL', 'S_integer_left.RESULT = KNOWN (PINT 1)',
        'S_integer_left.EVENTS = S_warned.EVENTS',
        'S_integer_right.COMPLETION = NORMAL', 'S_integer_right.RESULT = KNOWN (PINT 0)',
        'S_integer_right.EVENTS = S_warned.EVENTS',
        'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Deprecated" ' + prior.value(message(kind)) + ' ' + str(line) + ']',
        'S_request = S_reference', 'S_request.RESULT = KNOWN (PINT 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.EVENTS = S_warned.EVENTS', 'S_request.STORE = S.STORE',
        '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '~$error_handler_eligible(S, 2)', '~$error_handler_eligible(S, 8192)',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    if kind == 'string':
        conditions += ['$string_long($ptascii("1.5")) = STRINT 1 (STRINGPRECISIONLOSS :: eps)',
                       '$ob_object_string_value(S, pvalue_left)']
    for side in ['left', 'right']:
        if side in cells:
            conditions += [f'z_{side} = {line}', f'n_{side}* = $ptascii("{side}")',
                f'$compiled_read(S, porigin_{side}) = eps',
                f'(HCELL n_cell_{side}) <- S.ALLOCATIONS', f'~(n_cell_{side} <- S.REFCELLS)',
                f'$heap_count(HCELL n_cell_{side}, $machine_roots(S)) = 1',
                f'$heap_owners($heap_graph(S), HCELL n_cell_{side}) = 1']
        elif side == 'right':
            conditions += ['$compiled_read(S, porigin_right) = (PINT 0)']
        elif kind == 'string':
            conditions += ['pvalue_left_compiled = PSTRING ($ptascii("1.5"))',
                           'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled)']
        else:
            conditions += ['pvalue_left_compiled = pvalue_left']
    if len(cells) == 2:
        conditions += ['n_cell_left =/= n_cell_right']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine original precision-only conversion reaches its exact live Error before admission', original(name))]


def lifecycle(name, fixture, path):
    form, _, line, cells = shape(name)
    bindings, checks = bindings_for(name, fixture, path)
    stored = ''.join(f'S_capture.STORE[n_cell_{side}] = DEFINED pvalue_{side} /\\ ' for side in cells)
    checks[0] = ('original precision-only conversion preserves source and storage through actual production capture',
        original(name) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        shared.seed_identity() + r' /\ ' + shared.post_identity() + r' /\ S_capture_found = $drive_steps(S_seed_post, 0) /\ ' + stored +
        r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
        r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
        r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    if cells:
        nodes = '[' + ', '.join('HCELL n_cell_' + side for side in cells) + ']'
        jobs = '[' + ', '.join('DESTRUCTION_VALUE (HCELL n_cell_' + side + ')' for side in cells) + ']'
        checks[1] = ('the actual compiled-CV queue releases the original private cells before C0',
            '$destructor_frame_nodes(S_leave) = ' + nodes + r' /\ $destructor_frame_jobs(S_leave) = ' + jobs + r' /\ '
            'pdestructionrelease.JOBS = ' + jobs + r' /\ S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
            r'$destructor_borrowed_context(S_leave) = (pcallcontext) /\ '
            r'S_queue.CURRENT = eps /\ S_queue.FRAMES = eps /\ S_queue.ORIGIN = eps /\ ' +
            ''.join(f'S_queue.STORE[n_cell_{side}] = DEFINED pvalue_{side} /\\ ' for side in cells) +
            r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ ' +
            checks[1][1] + r' /\ ' + prior.public('S_queue'))
    def fatal(number):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(number).encode() + b'\n')
    old_line = 6 if form == 'constant' else 7 if form == 'right-cv' else 8
    checks[2] = ('C0 preserves the sole precision-loss diagnostic before the original fatal trace',
        checks[2][1].replace(prior.value(fatal(old_line)), prior.value(fatal(line))).replace(
            f' {old_line} /\\ ', f' {line} /\\ '))
    checks[3] = ('the retired source receipt owns neither private cells nor its Error', checks[3][1])
    return bindings, checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'source_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            source = CASES[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = lifecycle(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/output_final_default_left_modulo_deprecation_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py',
                'tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_right_cv_modulo_conversion_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_left_cv_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_sources.py',
                'tests/semantics/output_final_modulo_error_sources.py',
                'tests/semantics/output_final_modulo_error_review_state.py',
                'tests/semantics/output_final_division_error_sources.py',
                'tests/semantics/output_final_division_error_review_state.py',
                'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
                'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(__file__), path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                record['observed'] = json.loads(result.stdout)
                assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, after=fp())
            assert record['before'] == record['after']
            record['passed'] = True
        report['after_revision'] = head()
        assert report['revision'] == report['after_revision'], 'revision changed'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
