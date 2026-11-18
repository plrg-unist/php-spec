#!/usr/bin/env python3
"""Ground resolved-case aliases through reception, return and private Notice cells."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import global_relative_case_stdclass_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_case_stdclass_producer_reference_notice_cases.json')
BASELINE = prior.CATALOGUE
BASE_CASES = {case['id']: case for case in json.loads(BASELINE.read_bytes())}
PREFIX = prior.PREFIX.replace('$ptascii("make")', '$ptascii("ScopedCase138\\\\make")').replace('$ptascii("take")', '$ptascii("ScopedCase138\\\\take")')
base_front, base_full = prior.front_lines, prior.full_lines


def front_lines(case, front):
    baseline = dict(BASE_CASES[case['derived_from']['id']], notice_line=case['notice_line'], native_stdout=case['native_stdout'])
    result = []
    imports = '[($ptascii(' + json.dumps(case['import_alias']) + '), $ptascii(' + json.dumps(case['alias_target']) + '))]'
    for line in base_front(baseline, front):
        line = line.replace('$ptascii("make")', '$ptascii("ScopedCase138\\\\make")')
        line = line.replace('NNameRelative ', 'NName ').replace('PTRELATIVE,', 'PTPLAIN,')
        if line.startswith('pfunction_producer.ENV.NAMESPACE ='):
            line = 'pfunction_producer.ENV.NAMESPACE = $ptascii("ScopedCase138")' + (' /\\ pfunction_producer.ENV.CLASSES = ' + imports if '.CLASSES =' in line else '')
        elif line.startswith('pfunction_producer.ENV.CLASSES ='):
            line = 'pfunction_producer.ENV.CLASSES = ' + imports
        raw = 'text_formal' if case['side'] == 'formal' else 'text_return'
        if line.startswith('$base64(' + raw):
            line = line[:line.index(' = ')] + ' = $ptascii(' + json.dumps(case['alias_name']) + ')'
        result.append(line)
    return result


def full_lines(case):
    return base_full(dict(BASE_CASES[case['derived_from']['id']], notice_line=case['notice_line'], native_stdout=case['native_stdout']))


def controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    role = case['role_index'] if case['side'] == 'formal' else 0
    parameter = 'psparam' if role == 0 else 'psparam_last'

    def param(typename):
        return 'NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + str(role == 1).lower() + ') (BOOLEAN false) ' + ('phpType10' if role == 0 else 'phpType10_last') + ' ABSENT (SEQUENCE eps) ' + ('metadata_parameter' if role == 0 else 'metadata_parameter_last')

    def proof(typename=None, context=env, target=None):
        arguments, result, checked = 'phpType16', 'phpType18', signature
        if typename is not None:
            if case['side'] == 'formal':
                arguments = 'SEQUENCE ([' + ('' if role == 0 else 'phpType17, ') + param(typename) + '])'
            else:
                result = typename
        if target is not None:
            normalized = prior.normalized(case, target)
            if case['side'] == 'formal':
                first = 'psparam[.TYPE = ' + normalized + '], ' if case.get('nullable_first') else 'psparam, '
                checked += '[.PARAMETERS = [' + ('' if role == 0 else first) + parameter + '[.TYPE = ' + normalized + ']]]'
            else:
                checked += '[.RETURNS = ' + normalized + ']'
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + arguments + ', ' + result + ', ' + checked + ')'

    raw_type = lambda name=None, tag='NName': prior.raw_type(case, name, tag)
    raw = raw_type()
    lines = [proof(), proof(raw), proof(raw_type(case['alias_target'], 'NNameFullyQualified')),
        proof(context=env + '[.NAMESPACE = $ptascii("Elsewhere")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for alias in (case['alias_name'].lower(), case['alias_name'].upper(), case['alias_name'].swapcase()):
        lines.append(proof(raw_type(alias)))
    for target in ('stdClass', 'STDCLASS', 'sTdClAsS', 'StDcLaSs'):
        context = env + '[.CLASSES = [($ptascii(' + json.dumps(case['import_alias']) + '), $ptascii(' + json.dumps(target) + '))]]'
        encoded = json.dumps(base64.b64encode(target.encode()).decode())
        lines += [proof(raw, context, target), '~' + proof(raw, context, target.swapcase()),
            '$reference_notice_producer_type_encoding($ptascii(' + json.dumps(target) + ')) = ' + encoded,
            '$base64($reference_notice_producer_type_encoding($ptascii(' + json.dumps(target) + '))) = $ptascii(' + json.dumps(target) + ')']
        if case['side'] == 'formal':
            lines.append('$reference_notice_producer_scoped_parameter_view(' + context + ', ' + param(raw) + ') = (' + param(raw_type(target, 'NNameFullyQualified')) + ')')
    for target in ('Other', 'Other\\stdClass', 'stdClass\\Other', 'stdClass\x00', ''):
        context = env + '[.CLASSES = [($ptascii(' + json.dumps(case['import_alias']) + '), ' + prior.types.byte_expr(target) + ')]]'
        lines.append('~' + proof(raw, context))
    context = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]]'
    lines.append('~' + proof(raw_type('sTdClAsS'), context))
    for tag in ('NNameRelative', 'NIdentifier'):
        lines.append('~' + proof(raw_type(case['alias_name'], tag)))
    for name in ('Other', case['alias_name'] + '\\stdClass', '\\' + case['alias_name'], case['alias_name'] + '\x00', '', 'int', 'mixed', 'self', 'parent', 'static'):
        lines.append('~' + proof(raw_type(name)))
    if case['shape'] == 'union':
        members = case['formal_members'] if case['side'] == 'formal' else case['return_members']
        reverse = dict(case, **{('formal_members' if case['side'] == 'formal' else 'return_members'): members[::-1]})
        lines.append('~' + proof(prior.raw_type(reverse, case['alias_name'], 'NName')))
    for update in ('.BYREF = ' + str(role == 0).lower(), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged scoped case formal"'):
        parameters = '[' + ('' if role == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for stage in (('receive', 'return', 'notice') if case['side'] == 'formal' else ('return', 'notice')):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for value in ('', 'f', 'fo', 'foo', 'foob', 'fooba', 'foobar'):
        lines.append('$reference_notice_producer_type_encoding($ptascii(' + json.dumps(value) + ')) = ' + json.dumps(base64.b64encode(value.encode()).decode()))
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    before = hashlib.sha256(BASELINE.read_bytes()).hexdigest()
    prior.CATALOGUE, prior.PREFIX = CATALOGUE, PREFIX
    prior.front_lines, prior.full_lines, prior.controls = front_lines, full_lines, controls
    passed = prior.main()
    path = args.output.resolve() / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(BASELINE)] = before
    report['inputs_stable'] = report['inputs_stable'] and hashlib.sha256(BASELINE.read_bytes()).hexdigest() == before
    report['passed'] = passed and report['inputs_stable']
    report['family'] = 'scoped-case-stdclass-producer-reference-notice'
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
