#!/usr/bin/env python3
"""Ground relative RETURN import independence, Param order and private Notice cells."""
import base64
import json
from pathlib import Path

import cv_object_producer_reference_notice_review_state as object_proofs
import scoped_stdclass_return_producer_reference_notice_review_state as driver

CATALOGUE = Path(__file__).with_name('relative_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = object_proofs.PREFIX.replace(
    r'pcallcontext.NAME <- [$ptascii("ReviewNotice76\\ObjectNamed\\make"), $ptascii("ReviewNotice76\\NullNamed\\make")]',
    'pcallcontext.NAME = $ptascii("make")')
assert 'ReviewNotice76' not in PREFIX


def class_type(name):
    return '[(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))]'


def normal(initial, case, front):
    original, inherited = object_proofs.normal(initial, case, 0, front)
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    canonical = class_type('stdClass')
    imports = '[($ptascii("stdclass"), $ptascii("PeerRelativeReturn130\\\\Other"))]'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, ' + signature + ')'

    def proof(raw='phpType18', parameter='phpType17', context=env, returns=None):
        checked = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', SEQUENCE ([phpType7]), SEQUENCE ([' + parameter + ']), ' + raw + ', ' + checked + ')'

    reached = []
    for line in original:
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + canonical
        elif line.startswith(signature + '.RETURNS = '):
            line = signature + '.RETURNS = ' + canonical
        elif line.startswith('phpType17 = '):
            line = line.replace('NIdentifier (BYTES text_formal)', 'NNameFullyQualified (BYTES text_formal)', 1)
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = NNameRelative (BYTES text_return) metadata_return'
        elif line.startswith('$ptlc($base64(text_'):
            line = line.replace('$ptascii("object")', '$ptascii("stdclass")')
        elif line.lstrip('~').startswith('$reference_notice_producer_arguments('):
            line = line.lstrip('~')
        elif line.lstrip('~') == header:
            reached += ['~' + header, ('~' if front else '') + proof()]
            continue
        reached.append(line)
        if line == '~' + signature + '.BYREF':
            reached += [env + '.NAMESPACE = eps /\\ ' + env + '.CLASSES = ' + imports]
    context = '$pltypecontext(' + env + ', PTGLOBAL, PTRETURN, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 })'
    reached += ['$base64(text_formal) = $ptascii("stdClass")',
        '$base64(text_return) = $ptascii("stdClass")',
        '$ptvalidname($base64(text_return), true)',
        '$ptsingle(' + context + ', PTRELATIVE, $base64(text_return)) = PTOK (' + canonical + ') eps']
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith((
        '~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object('))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    raw = 'NNameRelative (BYTES text_return) metadata_return'
    derived += [proof(context=env + '[.CLASSES = eps]'),
        proof(context=env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]]'),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        proof(raw=raw.replace('NNameRelative', 'NNameFullyQualified')),
        '~' + proof(raw=raw.replace('NNameRelative', 'NName')),
        '~' + proof(raw=raw.replace('NNameRelative', 'NIdentifier')),
        proof(returns='eps'), proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(raw=raw.replace('metadata_return', 'eps')),
        proof(parameter=parameter.replace('metadata_parameter', 'eps'))]
    alias_parameter = parameter.replace('NNameFullyQualified (BYTES text_formal)', 'NName (BYTES "Qm94MTMw")', 1)
    alias_env = env + '[.CLASSES = [($ptascii("box130"), $ptascii("stdClass")), ($ptascii("stdclass"), $ptascii("Other"))]]'
    viewed = alias_parameter.replace('NName (BYTES "Qm94MTMw")', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    derived += ['$reference_notice_producer_scoped_parameter_view(' + alias_env + ', ' + alias_parameter + ') = (' + viewed + ')',
        proof(parameter=alias_parameter, context=alias_env), proof(parameter=viewed, context=alias_env),
        '~' + proof(parameter=parameter.replace('NNameFullyQualified', 'NNameRelative', 1))]
    for name in ('Other', 'STDCLASS', 'sTdClAsS', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', '', 'int', 'mixed', 'self', 'array', 'callable'):
        changed = 'NNameRelative (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=changed))
    nullable = canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    for changed in ('NNullableType (' + raw + ') metadata_return',
            'NUnionType (SEQUENCE ([' + raw + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return'):
        derived.append(('' if changed.startswith('NNullableType ') else '~') + proof(raw=changed, returns=nullable))
    for returns in (class_type('Other'), class_type('STDCLASS'), object_proofs.branches(['object']), nullable):
        derived.append('~' + proof(returns=returns))
    for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged relative return formal default"'):
        derived.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived.append('$typed_conversion_at(S_return, ' + canonical + ', POBJECT n_old, ' + strict + ') = TYPEVALUE (POBJECT n_old)')
        for value in ('PNULL', 'PINT 7', 'PBOOL false', 'PSTRING ($ptascii("17"))'):
            derived.append('$typed_conversion_at(S_return, ' + canonical + ', ' + value + ', ' + strict + ') = TYPEREJECT')
    return reached, derived


def main():
    driver.CATALOGUE, driver.PREFIX, driver.normal = CATALOGUE, PREFIX, normal
    driver.__doc__ = __doc__
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
