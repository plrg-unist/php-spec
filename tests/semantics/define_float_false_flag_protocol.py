#!/usr/bin/env python3
"""Reached finite float names preserve false flags and conversion authority."""
import json
import os
from pathlib import Path

import define_scalar_false_flag_protocol as scalar
import define_float_false_flag_sources as sources

driver, common, text, b64 = scalar.driver, scalar.common, scalar.text, scalar.b64
PREFIX = scalar.PREFIX
NEGZERO = 'PFLOAT 9223372036854775808'
POSZERO = 'PFLOAT 0'
TWO_HALF = 'PFLOAT 4612811918334230528'
TWO_THREE_QUARTERS = 'PFLOAT 4613374868287651840'


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'signed-zero-float-names-false-flags-and-default-duplicate':
        values += [*scalar.front('S', 'S_initial', NEGZERO, 'PINT 701'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            *scalar.publish('S_negative', 'S', NEGZERO, 'PINT 701', '-0'),
            *scalar.front('S_positive', 'S_negative', POSZERO, 'PINT 702'), '$string_bytes(pvalue_flag_S_positive) = (eps)',
            *scalar.publish('S_both', 'S_positive', POSZERO, 'PINT 702', '0'),
            *scalar.front('S_fraction', 'S_both', TWO_HALF, 'PINT 703'), 'pvalue_flag_S_fraction = ' + NEGZERO,
            *scalar.publish('S_three', 'S_fraction', TWO_HALF, 'PINT 703', '2.5'),
            *scalar.front('S_duplicate', 'S_three', NEGZERO, 'PINT 704'), '$string_bytes(pvalue_flag_S_duplicate) = (' + text('0') + ')',
            '$(|S_duplicate.USERCONSTANTS| = 3)', '~$error_handler_eligible(S_duplicate,2)',
            *scalar.converted('S_duplicate', NEGZERO, '-0'), 'z_precision = $precision_value(S_duplicate)',
            *common.step('S_warning', 'S_duplicate'),
            'S_warning.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received_S_duplicate z_precision 3) :: ptask_S_duplicate*',
            '$call_task_valid(S_warning,DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received_S_duplicate z_precision 3)',
            'S_warning.EVENTS = S_duplicate.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('-0') + ') pconfigcall_S_duplicate.LINE]',
            'S_warning.STRINGDATA = S_duplicate_converted.STRINGDATA',
            *scalar.unchanged('S_warning', 'S_duplicate', 'STORE ENV USERCONSTANTS ARRAYS OBJECTS SELECTEDCALLS'), *common.public('S_warning'),
            *common.step('S_return', 'S_warning', 'PBOOL false'), 'S_return.TODO = ptask_S_duplicate*',
            'S_return.USERCONSTANTS = S_warning.USERCONSTANTS',
            *scalar.front('S_integer', 'S_return', 'PINT 37', 'PINT 737'), 'pvalue_flag_S_integer = PINT 0',
            'pconfigcall_float_substitute = pconfigcall_S_integer[.SENT = $named_slot_set(pconfigcall_S_integer.SENT,0,KNOWN (' + TWO_HALF + '))]',
            '$dynamic_scalar_define_call(pconfigcall_float_substitute)', '~$dynamic_scalar_define_valid(S_integer,pconfigcall_float_substitute)',
            *scalar.publish('S_four', 'S_integer', 'PINT 37', 'PINT 737', '37'),
            'pconfigcall_other_zero = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + POSZERO + '))]',
            '$dynamic_scalar_define_call(pconfigcall_other_zero)', '~$dynamic_scalar_define_valid(S,pconfigcall_other_zero)',
            '~$dynamic_scalar_define_duplicate_valid(S_warning,pconfigcall_S_duplicate,pvalue_received_S_duplicate,z_precision,0)',
            '~$dynamic_scalar_define_duplicate_valid(S_warning,pconfigcall_S_duplicate,pvalue_received_S_duplicate,z_precision,4)',
            *scalar.budget('S'), *scalar.budget('S_warning')]
        for raw_name in ('PFLOAT 9218868437227405312', 'PFLOAT 18442240474082181120', 'PFLOAT 9221120237041090560', 'PNULL', 'POBJECT 0'):
            values += ['~$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + raw_name + '))])']
        for flag in ('PBOOL true', 'PNULL', 'PINT 1', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('false'), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        values += ['$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL false))])']
    elif name == 'captured-request-zero-before-float-name-live-effects':
        values += [*scalar.front('S', 'S_initial', TWO_THREE_QUARTERS, 'pvalue_candidate'), 'S.USERCONSTANTS = eps',
            'pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) preqbytes_flag', 'preqbytes_flag = ' + text('0'),
            '$string_carrier_valid(S,pvalue_flag_S)', '~$truth(S,pvalue_flag_S)',
            'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate', 'preqbytes_candidate = ' + text('captured-value42'),
            '$string_carrier_valid(S,pvalue_candidate)', '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_live_flag',
            '$string_bytes(pvalue_live_flag) = (' + text('false') + ')', '$truth(S,pvalue_live_flag)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *scalar.publish('S_published', 'S', TWO_THREE_QUARTERS, 'pvalue_candidate', '2.75'),
            'S_published.STORE[n_result] = DEFINED (PINT 99)',
            'n_bad_string = |S.STRINGDATA|', 'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_flag',
            '$dynamic_define_false_scalar_flag(pvalue_bad_flag)', '~$string_carrier_valid(S,pvalue_bad_flag)',
            '~$dynamic_scalar_define_flag_carrier_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])',
            '~$dynamic_scalar_define_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])', *scalar.budget('S')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_scalar_define_valid(S,pconfigcall_S[' + field + '])']
    else:
        assert name == 'strict-float-name-precedes-nonbool-flag-after-effects'
        values += [*scalar.front('S', 'S_initial', TWO_HALF, 'PINT 747'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'pconfigcall_S.SELECTION = (n_selection)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *scalar.strict_error('S_error', 'S', TWO_HALF, 'PINT 747', 'float'),
            *scalar.front('S_zero', 'S_error', NEGZERO, 'PINT 749'), '$string_bytes(pvalue_flag_S_zero) = (' + text('0') + ')',
            *scalar.strict_error('S_zero_error', 'S_zero', NEGZERO, 'PINT 749', 'float'),
            'S_zero_error.STORE[n_result] = DEFINED (PINT 99)', *scalar.budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(scalar.__file__).relative_to(driver.ROOT)): sources.family.sha(scalar.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
