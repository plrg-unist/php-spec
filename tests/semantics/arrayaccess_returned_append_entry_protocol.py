"""Class-method derivative of the preserved entry recipe; no empty-registry mutation."""
import base64
import json


def render(main_fixture, source):
    filename = json.dumps(base64.b64encode(bytes(source)).decode())
    checks = [
        'S_initial = $php_run(' + main_fixture + ', 0, ' + filename + ')',
        'S_initial.COMPLETION = BUDGET',
        '$call_current_valid(S_initial)',
        '$call_frames_valid(S_initial, S_initial.FRAMES)',
        '$call_descriptors_valid(S_initial)',
        '$heap_valid($heap_graph(S_initial))',
        'S = S_initial[.COMPLETION = NORMAL]',
        'S.CODE = pcode :: pcode_tail*',
        'S.CLASSES = pclassdesc_cell :: pclassdesc_owner :: pclassdesc_tail*',
        'pclassdesc_owner.NAME = $ptascii("CompositionOwner309")',
        'pclassdesc_owner.METHODS = pmethoddesc :: pmethoddesc_tail*',
        '$scope_check(S) = S',
        '$call_entry_check(S) = S',
        'S_zero = $drive(S, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_zero.TODO = S.TODO',
        'S_bad_code = S[.CODE = pcode[.GLOBALS = eps :: pcode.GLOBALS] :: pcode_tail*]',
        '$heap_graph(S_bad_code) = $heap_graph(S)',
        'S_scope_rejected = $scope_check(S_bad_code)',
        'S_scope_rejected.COMPLETION = UNSUPPORTED "invalid compiled global designation"',
        'S_scope_rejected.TODO = eps',
        'S_entry_rejected = $call_entry_check(S_bad_code)',
        'S_entry_rejected.COMPLETION = UNSUPPORTED "invalid compiled global designation"',
        'S_entry_rejected.TODO = eps',
        '$drive(S_bad_code, 0).COMPLETION = UNSUPPORTED "invalid compiled global designation"',
        'S_bad_descriptor = S[.CLASSES = pclassdesc_cell :: pclassdesc_owner[.METHODS = eps] :: pclassdesc_tail*]',
        '$heap_graph(S_bad_descriptor) = $heap_graph(S)',
        '$scope_check(S_bad_descriptor) = S_bad_descriptor',
        'S_descriptor_rejected = $call_entry_check(S_bad_descriptor)',
        'S_descriptor_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_descriptor_rejected.TODO = eps',
        '$drive(S_bad_descriptor, 0).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_both_bad = S_bad_code[.CLASSES = pclassdesc_cell :: pclassdesc_owner[.METHODS = eps] :: pclassdesc_tail*]',
        '$call_entry_check(S_both_bad).COMPLETION = UNSUPPORTED "invalid compiled global designation"',
        'S_non_normal = S_both_bad[.COMPLETION = BUDGET]',
        '$call_entry_check(S_non_normal) = S_non_normal',
        'S_scope_non_normal = $scope_check(S_non_normal)',
        'S_scope_non_normal.COMPLETION = UNSUPPORTED "invalid compiled global designation"',
        'S_scope_non_normal.TODO = eps',
    ]
    fixture = 'dec $main() : bool\ndef $main() = true\n'
    fixture += ''.join('  -- if ' + check + '\n' for check in checks)
    return fixture, checks
