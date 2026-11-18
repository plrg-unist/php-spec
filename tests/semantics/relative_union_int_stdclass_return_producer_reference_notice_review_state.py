#!/usr/bin/env python3
"""Ground exact ordered relative class/int unions after formal-alias normalization."""
import base64
import json
from pathlib import Path

import relative_nullable_stdclass_return_producer_reference_notice_review_state as previous
from relative_stdclass_return_producer_reference_notice_review_state import class_type
import scoped_stdclass_return_producer_reference_notice_review_state as driver

CATALOGUE = Path(__file__).with_name('relative_union_int_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = previous.PREFIX


def normal(initial, case, front):
    original, inherited = previous.normal(initial, case, front)
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    singleton = class_type('stdClass')
    class_first = singleton[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'
    int_first = '[(PTBRANCH ([PTBUILTIN "int"])), ' + singleton[1:]
    relative = 'NNameRelative (BYTES text_return) metadata_return'
    integer = 'NIdentifier (BYTES text_return_int) metadata_return_int'
    members = '[' + integer + ', ' + relative + ']'
    union = lambda items: 'NUnionType (SEQUENCE (' + items + ')) metadata_union_return'
    reached = []
    for line in original:
        if line.startswith(signature + '.RETURNS = '):
            line = signature + '.RETURNS = ' + int_first
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = ' + union(members)
        elif line.startswith(env + '.NAMESPACE = '):
            line = line.replace('PeerRelativeNullable131', 'PeerRelativeIntUnion133')
        reached.append(line)
    reached += ['$ptlc($base64(text_return_int)) = $ptascii("int")']
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith((
        '~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object('))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    viewed = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)

    def proof(raw='phpType18', formal='phpType17', context=env, returns=None):
        checked = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', SEQUENCE ([phpType7]), SEQUENCE ([' + formal + ']), ' + raw + ', ' + checked + ')'

    derived += ['$reference_notice_producer_scoped_parameter_view(' + env + ', phpType17) = (' + viewed + ')',
        proof(formal=viewed), proof(raw=union(members.replace('NNameRelative', 'NNameFullyQualified'))),
        '~' + proof(raw=union(members.replace('NNameRelative', 'NName'))),
        '~' + proof(raw=union(members.replace('NNameRelative', 'NIdentifier'))),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'),
        proof(formal=viewed, context=env + '[.CLASSES = eps]'),
        proof(formal=viewed, context=env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]]'),
        proof(returns='eps'), proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(raw=union(members).replace('metadata_union_return', 'eps')),
        proof(raw=union(members).replace('metadata_return_int', 'eps')),
        proof(formal=parameter.replace('metadata_parameter', 'eps')),
        '~' + proof(formal=parameter.replace('NName ', 'NNameRelative ', 1))]
    reversed_members = '[' + relative + ', ' + integer + ']'
    derived += [proof(raw=union(reversed_members), returns=class_first), '~' + proof(raw=union(reversed_members)),
        '~' + proof(returns=class_first), '~' + proof(raw=relative), proof(raw=relative, returns=singleton),
        '~' + proof(raw='NNullableType (' + relative + ') metadata_union_return'),
        proof(raw='NNullableType (' + relative + ') metadata_union_return', returns=class_first.replace('"int"', '"null"'))]
    for name in ('Other', 'STDCLASS', 'sTdClAsS', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', '', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NNameRelative (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=union('[' + integer + ', ' + raw + ']')))
    for raw in ('eps', '[' + relative + ']', '[' + integer + ', ' + relative + ', ' + integer + ']', '[' + relative + ', ' + relative + ']'):
        derived.append('~' + proof(raw=union(raw)))
    null_name = 'NIdentifier (BYTES "bnVsbA==") metadata_return_int'
    wider = int_first[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    derived += ['~' + proof(raw=union('[' + integer + ', ' + relative + ', ' + null_name + ']'), returns=wider),
        proof(raw=union('[' + relative + ', ' + null_name + ']'), returns=class_first.replace('"int"', '"null"'))]
    for name in ('float', 'bool', 'string', 'array', 'callable', 'false', 'true', 'iterable'):
        builtin = 'NIdentifier (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return_int'
        derived.append('~' + proof(raw=union('[' + relative + ', ' + builtin + ']'), returns=class_first.replace('"int"', json.dumps(name))))
    for returns in (singleton, class_type('Other')[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]',
            '[(PTBRANCH ([PTBUILTIN "int"])), ' + class_type('STDCLASS')[1:], wider):
        derived.append('~' + proof(returns=returns))
    for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged relative int-union formal default"'):
        derived.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived += ['$typed_conversion_at(S_return, ' + int_first + ', POBJECT n_old, ' + strict + ') = TYPEVALUE (POBJECT n_old)',
            '$typed_conversion_at(S_return, ' + int_first + ', PINT 7, ' + strict + ') = TYPEVALUE (PINT 7)',
            '$typed_conversion_at(S_return, ' + int_first + ', PNULL, ' + strict + ') = TYPEREJECT']
    for value in ('PBOOL false', 'PSTRING ($ptascii("17"))'):
        derived += ['$typed_conversion_at(S_return, ' + int_first + ', ' + value + ', true) = TYPEREJECT',
            '$typed_conversion_at(S_return, ' + int_first + ', ' + value + ', false) = TYPEINTEGER (' + value + ')']
    return reached, derived


def main():
    driver.CATALOGUE, driver.PREFIX, driver.normal = CATALOGUE, PREFIX, normal
    driver.__doc__ = __doc__
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
