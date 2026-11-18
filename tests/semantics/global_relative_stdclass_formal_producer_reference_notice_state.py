#!/usr/bin/env python3
"""Ground canonical relative FORMALs before reception, retirement and private Notices."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_plain_stdclass_formal_producer_reference_notice_state as driver

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = driver.PREFIX
class_type = driver.prior.class_type
base_front = driver.front_lines


def front_lines(index, case):
    lines = []
    for line in base_front(index, case):
        line = line.replace(class_type('sTdClAsS'), class_type('stdClass'))
        line = line.replace('NName (BYTES text_formal)', 'NNameRelative (BYTES text_formal)')
        line = line.replace('$ptascii("sTdClAsS")', '$ptascii("stdClass")')
        if line == 'pfunction_producer.ENV.CLASSES = eps' and case['import_target']:
            line = 'pfunction_producer.ENV.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(case['import_target']) + '))]'
        lines.append(line)
    return lines


def controls(index, case):
    raw = 'phpType17' if index == 0 else 'phpType17_last'
    byref = 'false' if index == 0 else 'true'
    variable = 'phpType10' if index == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if index == 0 else 'metadata_parameter_last'
    parameter = 'psparam' if index == 0 else 'psparam_last'
    shape = 'NParam (SEQUENCE eps) (INTEGER 0) (NNameRelative (BYTES text_formal) metadata_formal) (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    view = shape.replace('NNameRelative (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    sequence = 'SEQUENCE ([phpType17])' if index == 0 else 'SEQUENCE ([phpType17, phpType17_last])'
    def proof(value=raw, context=env, checked=signature):
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + sequence.replace(raw, '(' + value + ')') + ', phpType18, ' + checked + ')'
    def converted(value=raw, context=env):
        return '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + value + ')'
    lines = [converted() + ' = (' + view + ')', converted(view) + ' = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + raw + ') = ' + raw,
        proof(), proof(view),
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.RETURNS = eps])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for imports in ('eps', '[($ptascii("stdclass"), $ptascii("Other"))]', '[($ptascii("box"), $ptascii("stdClass"))]'):
        context = env + '[.CLASSES = ' + imports + ']'
        lines += [converted(context=context) + ' = (' + view + ')', proof(context=context)]
    context = env + '[.NAMESPACE = $ptascii("Other")]'
    lines += [converted(context=context) + ' = ' + raw, '~' + proof(context=context)]
    for name in ('Other', 'Other\\stdClass', '\\stdClass', 'namespace\\stdClass',
            'STDCLASS', 'sTdClAsS', 'stdClass\x00', '', 'int', 'mixed', 'self', 'parent', 'static'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()))
        lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    changed = shape.replace('NNameRelative ', 'NIdentifier ')
    lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    for wrapper in ('NNullableType (NNameRelative (BYTES text_formal) metadata_formal) metadata_formal',
            'NUnionType (SEQUENCE ([NNameRelative (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_formal'):
        changed = shape.replace('NNameRelative (BYTES text_formal) metadata_formal', wrapper)
        lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    for before, after in (('metadata_formal)', 'eps)'), (metadata, 'eps')):
        lines += [converted(shape.replace(before, after)) + ' = (' + view.replace(before, after) + ')', proof(shape.replace(before, after))]
    for update in ('.BYREF = ' + ('true' if index == 0 else 'false'), '.VARIADIC = true',
            '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged relative formal default"',
            '.TYPE = ' + class_type('STDCLASS')):
        parameters = '[' + ('' if index == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + proof(checked=signature + '[.PARAMETERS = ' + parameters + ']'))
    for strict in ('true', 'false'):
        lines.append('$typed_conversion_at(S_receive, ' + class_type('stdClass') + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
        for value in ('PNULL', 'PINT 19', 'PBOOL false'):
            lines.append('$typed_conversion_at(S_receive, ' + class_type('stdClass') + ', ' + value + ', ' + strict + ') = TYPEREJECT')
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
    driver.front_lines, driver.controls = front_lines, controls
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
    report['family'] = 'global-relative-stdclass-formal-producer-reference-notice'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
