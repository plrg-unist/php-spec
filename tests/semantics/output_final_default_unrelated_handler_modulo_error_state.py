#!/usr/bin/env python3
"""An uncalled Deprecated handler retains staged MOD authority and FINAL cleanup."""
import argparse
import base64
import json
import re
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_left_modulo_deprecation_error_state as previous
import output_final_default_unrelated_handler_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
shared = previous.shared
CASES = {form: sources.CASES['native-default-unrelated-handler-modulo-error-' + form]
         for form in ['constant', 'cv-pair']}
PREFIX = previous.PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 9) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion n) :: ptask_tail*
  -- if n = |pintegerconversion.NOTICES|
def $dp_phase(S, n) = false -- otherwise''')
CAPTURE = shared.CAPTURE


def bindings_for(name, fixture, path):
    bindings, checks = previous.lifecycle(name + '-string', fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('S_left = '))
    initial = [re.sub(r'\bS\b', 'S_binary', binding) for binding in bindings[:stop]]
    index = bindings.index('S_generated.COMPLETION = THROWING n_exception')
    return initial + [
        '$integer_operator_plan(S_binary) = (pintegeroperation)',
        *prior.seek('S', 'S_binary', 9),
        'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion n) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)', 'z = pintegeroperation.LINE',
        '$integer_pointer_value(S, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$integer_pointer_value(S, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$integer_conversion(pvalue_left) = (pintegerconversion_left)',
        'S_warned = S', 'S_request = $dz_raw(S)',
        'S_generated = $throwable_transition(S, S_request)',
        *bindings[index:]], checks


def original(name):
    cells = ['left', 'right'] if name == 'cv-pair' else []
    line = 8 if cells else 6
    cvs = '[$ptascii("left"), $ptascii("right")]' if cells else 'eps'
    conditions = [
        f'z = {line}', 'n = 0', 'i_left = 1',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {len(cells)}',
        'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', 'pvalue_right = PINT 0',
        'pintegeroperation.OP = MODULO', 'pintegeroperation.SWAPPED = false',
        'pintegeroperation.SITE = porigin_operator', '$integer_operation_valid(S, pintegeroperation)',
        '$integer_warning_valid(S, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, n)',
        '$integer_pointer_select(S, pintegeroperation.LEFT) = (pintegeroperation.LEFTPOINTER)',
        '$integer_pointer_select(S, pintegeroperation.RIGHT) = (pintegeroperation.RIGHTPOINTER)',
        '$ob_object_error_operand_value(S, pintegeroperation.LEFT, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, pintegeroperation.RIGHT, [PCFIELD 1], z) = (pvalue_right)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 0], pintegeroperation.LEFT) = ' + ('(8)' if cells else '(1)'),
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], pintegeroperation.RIGHT) = ' + ('(8)' if cells else '(1)'),
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})',
        '$string_long($ptascii("1x")) = STRINT i_left (LEADINGNUMBER :: eps)',
        'pintegerconversion_left = {INPUT pvalue_left, VALUE i_left, NOTICES [(2, $ptascii("A non-numeric value encountered"))]}',
        'pintegerconversion = {INPUT pvalue_right, VALUE 0, NOTICES eps}',
        '$integer_conversion(pvalue_right) = (pintegerconversion)', '$ob_object_modulo_integer(pvalue_right) = (0)',
        '$ob_object_string_value(S, pvalue_left)', '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '~$error_handler_eligible(S, 2)', '$error_handler_eligible(S, 8192)',
        f'S.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) {line}]',
        'S.STORE = S_binary.STORE', 'S.RESULT = KNOWN PNULL',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        'S_request = $integer_converted(S, pintegeroperation, INTEGER_RIGHT i_left, 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.TODO = ptask_tail*', 'S_request.RESULT = KNOWN PNULL',
        'S_request.EVENTS = S.EVENTS', 'S_request.STORE = S.STORE',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    if cells:
        conditions += ['n_cell_left =/= n_cell_right']
        for side in cells:
            conditions += [f'n_{side}* = $ptascii("{side}")', f'z_{side} = {line}',
                f'pintegeroperation.{side.upper()} = VARIABLE n_{side}* z_{side}',
                f'pintegeroperation.{side.upper()}POINTER = INTEGER_CV n_{side}*',
                f'$compiled_read(S, porigin_{side}) = eps',
                f'(HCELL n_cell_{side}) <- S.ALLOCATIONS', f'~(n_cell_{side} <- S.REFCELLS)',
                f'$heap_count(HCELL n_cell_{side}, $machine_roots(S)) = 1',
                f'$heap_owners($heap_graph(S), HCELL n_cell_{side}) = 1']
    else:
        conditions += ['pintegeroperation.LEFT = KNOWN pvalue_left', 'pintegeroperation.RIGHT = KNOWN pvalue_right',
            'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_left',
            'pintegeroperation.RIGHTPOINTER = INTEGER_COPY pvalue_right',
            'pvalue_left_compiled = PSTRING ($ptascii("1x"))',
            'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled)',
            '$compiled_read(S, porigin_right) = (PINT 0)']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine staged pointers and reconverted left value precede the live MOD Error',
                               original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    bindings, checks = bindings_for(name, fixture, path)
    cells = ['left', 'right'] if name == 'cv-pair' else []
    stored = ''.join(f'S_capture.STORE[n_cell_{side}] = DEFINED pvalue_{side} /\\ ' for side in cells)
    checks[0] = ('genuine staged completion captures only a nonowning source receipt and exact driver closure',
        original(name) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        shared.seed_identity() + r' /\ ' + shared.post_identity() + r' /\ S_capture_found = $drive_steps(S_seed_post, 0) /\ ' +
        stored + r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    checks[2] = ('C0 preserves the sole Warning and no handler output after actual cell retirement', checks[2][1])
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--frontier', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true', 'module_count': len(modules),
              'source_agreement_credit': 0, 'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = args.output / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(CASES[name]).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = (frontier if args.frontier else lifecycle)(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(module.__file__) for module in list(sys.modules.values())
                        if getattr(module, '__file__', None) and Path(module.__file__).parent == Path(__file__).parent]
            watched += [path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
            report['records'].append(record)
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
        assert report['revision'] == report['after_revision']
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(args.output / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
