#!/usr/bin/env python3
"""Ground nullable and flat ordered Relative FORMALs, including actual NULL reception."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_plain_nullable_stdclass_formal_producer_reference_notice_state as driver
import global_plain_ordered_stdclass_formal_producer_reference_notice_state as ordered

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_nullable_ordered_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = driver.PREFIX
class_type = driver.prior.prior.class_type
nullable_front, plain_full = driver.front_lines, driver.prior.full_lines


def front_lines(index, case):
    role = case['role_index']
    base = nullable_front if case['shape'] == 'nullable' else ordered.front_lines
    # The inherited generators apply wrappers to their original mixed-case type.
    compatibility = dict(case, class_formals=['sTdClAsS'] if role == 0 else [None, 'sTdClAsS'])
    lines = []
    for line in base(role, compatibility):
        line = line.replace('NName (BYTES text_formal)', 'NNameRelative (BYTES text_formal)')
        line = line.replace('$ptascii("sTdClAsS")', '$ptascii("stdClass")')
        if line == 'pfunction_producer.ENV.CLASSES = eps' and case['import_target']:
            line = 'pfunction_producer.ENV.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(case['import_target']) + '))]'
        if case['nullable_first']:
            line = line.replace(r'~psparam.BYREF /\ psparam.TYPE = eps', r'~psparam.BYREF /\ psparam.TYPE = ' + driver.nullable_type('stdClass'))
            if line == 'phpType18_parameter = ABSENT':
                line = 'phpType18_parameter = NNullableType (NNameRelative (BYTES text_formal_first) metadata_formal_first) metadata_nullable_first'
        lines.append(line)
    if case['nullable_first']:
        lines += ['$base64(text_formal_first) = $ptascii("stdClass")',
            'S_receive_first = $pfn_receive_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]',
            '$pfn_receive_ready(S_receive_first, 0)',
            'S_receive_first.TODO = [TYPE_RECEIVE porigin_first 0]',
            '$receiving_function(S_receive_first, porigin_first) = (pfunction_first)',
            'pfunction_first = pfunction_producer',
            '$typed_receive_valid(S_receive_first, porigin_first, 0)',
            'pfunction_first.SIGNATURE.PARAMETERS = [psparam, psparam_last]',
            'psparam.TYPE = ' + driver.nullable_type('stdClass'),
            '$lookup(S_receive_first.ENV, $ptascii("left")) = (n_first)',
            'S_receive_first.STORE[n_first] = DEFINED PNULL',
            '$parameter_backing_at(S_receive_first.PARAMETERBACKINGS, n_first) = eps',
            'S_received_first = $drive(S_receive_first, 1)[.COMPLETION = NORMAL]',
            'S_received_first.STORE = S_receive_first.STORE']
    return lines


def full_lines(index, case):
    return plain_full(case['role_index'], case)


def controls(index, case):
    role, shape = case['role_index'], case['shape']
    raw = 'phpType17' if role == 0 else 'phpType17_last'
    byref = 'false' if role == 0 else 'true'
    variable = 'phpType10' if role == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if role == 0 else 'metadata_parameter_last'
    parameter = 'psparam' if role == 0 else 'psparam_last'
    typename = ('NNullableType (NNameRelative (BYTES text_formal) metadata_formal) metadata_nullable_formal'
        if shape == 'nullable' else ordered.raw_type(case['formal_members'], tag='NNameRelative'))
    param = 'NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    viewed = param.replace('NNameRelative (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    sequence = 'SEQUENCE ([phpType17])' if role == 0 else 'SEQUENCE ([phpType17, phpType17_last])'
    def proof(value=raw, context=env, checked=signature):
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + sequence.replace(raw, '(' + value + ')') + ', phpType18, ' + checked + ')'
    def converted(value=raw, context=env):
        return '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + value + ')'
    def typed(value, normalized):
        parameters = '[' + ('' if role == 0 else 'psparam, ') + parameter + '[.TYPE = ' + normalized + ']]'
        return proof(value, checked=signature + '[.PARAMETERS = ' + parameters + ']')
    lines = [converted() + ' = (' + viewed + ')', converted(viewed) + ' = (' + viewed + ')',
        '$reference_notice_producer_global_parameter_view(' + raw + ') = ' + raw, proof(), proof(viewed),
        '~' + typed(param, class_type('stdClass')),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for imports in ('eps', '[($ptascii("stdclass"), $ptascii("Other"))]', '[($ptascii("box"), $ptascii("stdClass"))]'):
        context = env + '[.CLASSES = ' + imports + ']'
        lines += [converted(context=context) + ' = (' + viewed + ')', proof(context=context)]
    context = env + '[.NAMESPACE = $ptascii("Other")]'
    lines += [converted(context=context) + ' = ' + raw, '~' + proof(context=context)]
    for name in ('Other', 'Other\\stdClass', '\\stdClass', 'namespace\\stdClass',
            'STDCLASS', 'sTdClAsS', 'stdClass\x00', '', 'int', 'mixed', 'self', 'parent', 'static'):
        changed = param.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()))
        expected = changed.replace('NNameRelative ', 'NNameFullyQualified ', 1) if name in ('STDCLASS', 'sTdClAsS') else changed
        lines += [converted(changed) + ' = (' + expected + ')', '~' + proof(changed)]
    for before, after in ((metadata, 'eps'), ('metadata_formal)', 'eps)'),
            ('metadata_nullable_formal', 'eps'), ('metadata_formal_union', 'eps')):
        lines += [converted(param.replace(before, after)) + ' = (' + viewed.replace(before, after) + ')', proof(param.replace(before, after))]
    for update in ('.BYREF = ' + ('true' if role == 0 else 'false'), '.VARIADIC = true',
            '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged relative wrapped formal default"'):
        parameters = '[' + ('' if role == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + proof(checked=signature + '[.PARAMETERS = ' + parameters + ']'))
    if shape == 'union':
        accepted = [['class', kind] for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true', 'callable', 'iterable')]
        accepted += [items[::-1] for items in accepted]
        accepted += [['class', 'array', 'int', 'float', 'string', 'null', 'false', 'callable'],
            ['iterable', 'int', 'float', 'class', 'string', 'null', 'true', 'callable']]
        for members in accepted:
            syntax = param.replace(typename, ordered.raw_type(members, tag='NNameRelative', indexed=False))
            normalized = ordered.branches(members, 'stdClass')
            lines += [typed(syntax, normalized), '~' + typed(syntax, ordered.branches(members[::-1], 'stdClass')),
                '~' + typed(syntax, ordered.branches(members, 'STDCLASS'))]
        invalid = (['class'], ['class', 'class'], ['class', 'array', 'iterable'],
            ['class', 'object'], ['class', 'mixed'], ['class', 'void'], ['class', 'never'],
            ['class', 'bool', 'false'], ['class', 'true', 'false'], ['class', 'int', 'int'],
            ['class', 'array', 'int', 'float', 'string', 'null', 'false', 'callable', 'iterable'])
        for members in invalid:
            lines.append('~' + typed(param.replace(typename, ordered.raw_type(members, tag='NNameRelative', indexed=False)), ordered.branches(members, 'stdClass')))
    else:
        for strict in ('true', 'false'):
            lines += ['$typed_conversion_at(S_receive, ' + driver.nullable_type('stdClass') + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)',
                '$typed_conversion_at(S_receive, ' + driver.nullable_type('stdClass') + ', PNULL, ' + strict + ') = TYPEVALUE PNULL',
                '$typed_conversion_at(S_receive, ' + driver.nullable_type('stdClass') + ', PINT 19, ' + strict + ') = TYPEREJECT']
    for stage in ('receive', 'return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    driver.CATALOGUE, driver.PREFIX = CATALOGUE, PREFIX
    driver.front_lines, driver.full_lines, driver.controls = front_lines, full_lines, controls
    driver.__doc__ = __doc__
    paths = sorted({Path(module.__file__).absolute() for module in sys.modules.values()
        if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    paths += [Path(__file__), CATALOGUE]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    passed = driver.main()
    report_path = args.output.resolve() / 'report.json'
    report = json.loads(report_path.read_bytes())
    assert all(path not in report['inputs'] or report['inputs'][path] == digest for path, digest in before.items())
    report['inputs'].update(before)
    report['inputs_stable'] = report['inputs_stable'] and before == fingerprints()
    report['passed'] = passed and report['inputs_stable']
    report['family'] = 'global-relative-nullable-ordered-stdclass-formal-producer-reference-notice'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
