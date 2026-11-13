#!/usr/bin/env python3
"""Quiet staged MOD operands retain their original reads and FINAL retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_handler_modulo_error_state as previous
import output_final_default_selected_handlers_quiet_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
shared = previous.shared
PREFIX = previous.PREFIX
CAPTURE = previous.CAPTURE
CASES = {name: sources.CASES['native-default-selected-handlers-quiet-modulo-error-' + name]
         for name in ['constant', 'cv-pair', 'same-cv']}


def bindings_for(name, fixture, path):
    return previous.bindings_for('cv-pair' if name == 'same-cv' else name, fixture, path)


def original(name):
    cells = [] if name == 'constant' else ['left', 'right']
    line = {'constant': 6, 'cv-pair': 8, 'same-cv': 7}[name]
    left = 0 if name == 'same-cv' else 1
    cvs = ('eps' if not cells else '[$ptascii("value")]' if name == 'same-cv'
           else '[$ptascii("left"), $ptascii("right")]')
    conditions = [
        f'z = {line}', 'n = 0', f'i_left = {left}',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS',
        f'|S.ENV| = {0 if not cells else 1 if name == "same-cv" else 2}',
        f'pvalue_left = PINT {left}', 'pvalue_right = PINT 0',
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
        'pintegerconversion_left.INPUT = pvalue_left', 'pintegerconversion_left.VALUE = i_left',
        'pintegerconversion_left.NOTICES = eps',
        'pintegerconversion.INPUT = pvalue_right', 'pintegerconversion.VALUE = 0', 'pintegerconversion.NOTICES = eps',
        '$integer_conversion(pvalue_right) = (pintegerconversion)',
        '$ob_object_modulo_integer(pvalue_left) = (i_left)', '$ob_object_modulo_integer(pvalue_right) = (0)',
        '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '$error_handler_eligible(S, 2)', '$error_handler_eligible(S, 8192)',
        'S.ERRORHANDLER.LEVELS = 8194', 'S.ERRORHANDLER.CALLBACK =/= eps',
        'S.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]',
        'S.EVENTS = [OUTPUT ([80])]', 'S.STORE = S_binary.STORE', 'S.RESULT = KNOWN PNULL',
        'S.ERRORHANDLER = S_binary.ERRORHANDLER', 'S.ERRORHANDLERS = S_binary.ERRORHANDLERS',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        'S_request = $integer_converted(S, pintegeroperation, INTEGER_RIGHT i_left, 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.TODO = ptask_tail*', 'S_request.RESULT = KNOWN PNULL',
        'S_request.EVENTS = S.EVENTS', 'S_request.STORE = S.STORE',
        'S_request.ERRORHANDLER = S.ERRORHANDLER', 'S_request.ERRORHANDLERS = S.ERRORHANDLERS',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    if cells:
        conditions += ['n_cell_left = n_cell_right' if name == 'same-cv' else 'n_cell_left =/= n_cell_right']
        for side in cells:
            cv = 'value' if name == 'same-cv' else side
            conditions += [f'n_{side}* = $ptascii("{cv}")', f'z_{side} = {line}',
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
            '$compiled_read(S, porigin_left) = (PINT 1)', '$compiled_read(S, porigin_right) = (PINT 0)']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine quiet conversions and canonical pointers precede the live MOD Error',
                               original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    form = 'cv-pair' if name == 'same-cv' else name
    bindings, checks = previous.lifecycle(form, fixture, path)
    old = previous.original(form)
    assert checks[0][1].count(old) == 1
    checks[0] = ('actual quiet completion captures nonowning source and exact driver closure',
                 checks[0][1].replace(old, original(name)))
    if name == 'same-cv':
        def fatal(line):
            return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(line).encode() +
                    b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                    b' on line ' + str(line).encode() + b'\n')
        replacements = {
            '[HCELL n_cell_left, HCELL n_cell_right]': '[HCELL n_cell_left]',
            '[DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)]':
                '[DESTRUCTION_VALUE (HCELL n_cell_left)]',
            prior.value(fatal(8)): prior.value(fatal(7)), ' 8 /\\ ': ' 7 /\\ '}
        for old, new in replacements.items():
            checks = [(label, condition.replace(old, new)) for label, condition in checks]
    checks[2] = ('C0 preserves quiet output and the original fatal trace after actual cell retirement', checks[2][1])
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
            print(json.dumps({'case': name, 'seconds': record['seconds'], 'observed': record['observed']}), flush=True)
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
