#!/usr/bin/env python3
"""Reached Stringable returns feed genuine class queries and global recovery."""
import json
import os
from pathlib import Path

import query_stringable_name_protocol as cast
import query_stringable_class_name_sources as sources

common, text, b64 = cast.common, cast.text, cast.b64
driver, PREFIX = cast.driver, cast.PREFIX


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def loaded(state, class_name, member, kind, value=None):
    ready = state + '_ready'
    call = 'pconfigcall_converted_' + state
    valid = 'dynamic_class_constant_valid' if kind == 'INTRINSIC_CONSTANT' else 'dynamic_defined_valid'
    values = ['$' + valid + '(' + ready + ',' + call + ')',
        '$dynamic_defined_query(' + call + ') = ((' + text(class_name) + ',' + text(member) + '))',
        '$class_named(' + ready + '.CLASSNAMES,' + text(class_name.lower()) + ') = (porigin_class_' + state + ')',
        '$class_at(' + ready + '.CLASSES,porigin_class_' + state + ') = (pclassdesc_' + state + ')',
        'pclassdesc_' + state + '.KIND = "class"',
        '~$autoload_pending(' + ready + ',' + text(class_name) + ')']
    if value is None:
        values += ['$class_constant_lookup(' + ready + ',porigin_class_' + state + ',' + text(member) + ',|' + ready + '.CLASSES|) = eps']
    else:
        values += ['$class_constant_lookup(' + ready + ',porigin_class_' + state + ',' + text(member) + ',|' + ready + '.CLASSES|) = (pclassconstantdesc_' + state + ')',
            'pclassconstantdesc_' + state + '.FOLDED',
            '$class_constant_visible(' + ready + ',pclassconstantdesc_' + state + ')',
            '$compiled_read(' + ready + ',pclassconstantdesc_' + state + '.INITIALIZER) = (PINT ' + str(value) + ')']
    return values


def result_controls(state, kind, name):
    call, ready, returned = 'pconfigcall_converted_' + state, state + '_ready', state + '_returned'
    valid = 'dynamic_class_constant_valid' if kind == 'INTRINSIC_CONSTANT' else 'dynamic_defined_valid'
    values = []
    for index,value in enumerate(('PSTRING (' + text('A::B') + ' ++ [0])',
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
            'PSTRING_CARRIER (REQUEST_STRING (|' + returned + '.STRINGDATA|)) ' + text(name))):
        refused = state + '_refused_' + str(index)
        values += [refused + ' = $dynamic_query_string_finish(' + returned + ',pconfigcall_' + state + ',' + value + ')',
            refused + '.COMPLETION = UNSUPPORTED "Stringable query global name"']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 0',
            '.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|' + ready + '.STRINGDATA|)) ' + text(name) + '))]',
            '.SENT = [NAMED_SENT (KNOWN (PSTRING ' + text('A::B::C') + '))]'):
        values += ['~$' + valid + '(' + ready + ',' + call + '[' + field + '])']
    return values


def checks(program,path,name):
    selected = name == 'selected-stringable-class-query-keeps-converted-missing-member'
    recovery = name == 'missing-class-member-query-recovers-with-global-stringable-name'
    assert selected or recovery or name == 'stringable-loaded-class-value-and-existence'
    kind = 'INTRINSIC_DEFINED' if recovery else 'INTRINSIC_CONSTANT'
    query = 'MissingValueQuery58::MISSING' if selected else 'RecoveryValueQuery58::ABSENT' if recovery else 'LoadedValueQuery58::VALUE'
    result = None if selected else 'PBOOL false' if recovery else 'PINT 1693'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *cast.front('S','S_initial',kind),
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S.USERCONSTANTS = eps']
    if selected:
        values += ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$test_outputs(S.EVENTS) = ' + text('B|N|')]
    else:
        values += ['pconfigcall_S.SELECTION = eps']
    values += [*cast.weak('S',kind,query,result),
        *loaded('S',query.split('::')[0],query.split('::')[1],kind,None if selected or recovery else 1693),
        *cast.refusals('S'), *result_controls('S',kind,query), *cast.budget('S'), *cast.budget('S_returned')]
    if selected:
        values += ['pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text(query),
            '$lookup(S_ready.ENV,' + text('calls') + ') = (n_calls)', 'S_ready.STORE[n_calls] = DEFINED (PINT 1)',
            'S_ready.STORE[n_effects] = DEFINED (PINT 1)', 'S_ready.STORE[n_keep] = DEFINED (POBJECT n_object_S)']
        for variable,expected in [('call','defined'),('name','cast-live58')]:
            values += ['$lookup(S_ready.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
                'S_ready.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
                '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
        values += [*cast.error('S_error','S_ready','pconfigcall_converted_S','pvalue_string_S','Error',
                'Undefined constant MissingValueQuery58::MISSING','constant','classQueryCaller58'),
            '$node_children(S_error,HARRAY n_args_S_error) = eps',
            'S_error.OBJECTS[n_object_S] = S_ready.OBJECTS[n_object_S]',
            '$objectprops_at(S_error.OBJECTPROPS,n_object_S) = $objectprops_at(S_ready.OBJECTPROPS,n_object_S)',
            *unchanged('S_error','S_ready','CLASSES REFCELLS ERRORHANDLER'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *cast.budget('S_ready')]
    elif recovery:
        values += [*unchanged('S_done','S_ready','AUTOLOAD CLASSES CLASSNAMES CLASSCONSTANTCACHE EVENTS STRINGDATA SELECTEDCALLS ENV'),
            *cast.front('S_global','S_done','INTRINSIC_CONSTANT'), 'n_object_S_global = n_object_S',
            *cast.weak('S_global','INTRINSIC_CONSTANT','TRUE','PBOOL true'),
            '$dynamic_constant_global_name(' + text('TRUE') + ')',
            '~$dynamic_class_constant_valid(S_global_ready,pconfigcall_converted_S_global)',
            *unchanged('S_global_done','S_global_ready','AUTOLOAD CLASSES CLASSNAMES CLASSCONSTANTCACHE EVENTS STRINGDATA SELECTEDCALLS ENV'),
            '$lookup(S_global_done.ENV,' + text('calls') + ') = (n_calls_global)', 'S_global_done.STORE[n_calls_global] = DEFINED (PINT 2)',
            '$test_outputs(S_global_done.EVENTS) = ' + text('B|S|F|S|'),
            *common.public('S_global_done'), *cast.budget('S_global_ready')]
    else:
        values += [*unchanged('S_done','S_ready','AUTOLOAD CLASSES CLASSNAMES CLASSCONSTANTCACHE EVENTS STRINGDATA SELECTEDCALLS ENV'),
            *cast.front('S_defined','S_done','INTRINSIC_DEFINED'), 'n_object_S_defined = n_object_S',
            *cast.weak('S_defined','INTRINSIC_DEFINED',query,'PBOOL true'),
            *loaded('S_defined','LoadedValueQuery58','VALUE','INTRINSIC_DEFINED',1693),
            *unchanged('S_defined_done','S_defined_ready','AUTOLOAD CLASSES CLASSNAMES CLASSCONSTANTCACHE EVENTS STRINGDATA SELECTEDCALLS ENV'),
            '$lookup(S_defined_done.ENV,' + text('calls') + ') = (n_calls_defined)', 'S_defined_done.STORE[n_calls_defined] = DEFINED (PINT 2)',
            '$test_outputs(S_defined_done.EVENTS) = ' + text('B|S|1693|S|'),
            *common.public('S_defined_done'), *cast.budget('S_defined_ready')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(cast.__file__).relative_to(driver.ROOT)): sources.family.sha(cast.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
