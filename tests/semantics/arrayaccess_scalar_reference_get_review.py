"""Check strict scalar promotion before a CV becomes the Get result reference."""
import json

from arrayaccess_typed_reference_get_review import PREFIX, guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_paused = $aatyped_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")',
        'paccess.MODE = ACCESS_READ KEY_R',
        'paccess.OFFSET = PINT 17',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))]',
        'pfunction.CODE.STRICT',
        '$reference_verifies(S)',
        '~$access_reference_signature(pfunction.SIGNATURE)',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetGet"))',
    ]
    for member in ('offsetExists', 'offsetSet', 'offsetUnset'):
        checks.append(f'$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("{member}"))')
    for builtin in ('bool', 'true', 'false', 'null'):
        checks.append('$access_reference_call_signature(pfunction.SIGNATURE[.RETURNS = '
                      f'[(PTBRANCH ([PTBUILTIN "{builtin}"]))]], $ptascii("offsetGet"))')
    checks += [
        'pssignature_nullable = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]]',
        '$access_reference_call_signature(pssignature_nullable, $ptascii("offsetGet"))',
        'pssignature_union = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]]',
        '$access_reference_call_signature(pssignature_union, $ptascii("offsetGet"))',
    ]
    for builtin in ('string', 'callable', 'void', 'never', 'array', 'object'):
        checks.append('~$access_reference_call_signature(pfunction.SIGNATURE[.RETURNS = '
                      f'[(PTBRANCH ([PTBUILTIN "{builtin}"]))]], $ptascii("offsetGet"))')
    checks += [
        'pssignature_class = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTCLASS ($ptascii("Other"))])), (PTBRANCH ([PTBUILTIN "float"]))]]',
        '~$access_reference_call_signature(pssignature_class, $ptascii("offsetGet"))',
        'pssignature_intersection = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTCLASS ($ptascii("A")), PTCLASS ($ptascii("B"))])), (PTBRANCH ([PTBUILTIN "float"]))]]',
        '~$access_reference_call_signature(pssignature_intersection, $ptascii("offsetGet"))',
        '~$access_reference_call_signature(pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTSTATIC]))]], $ptascii("offsetGet"))',
        '~$access_reference_call_signature(pfunction.SIGNATURE[.RETURNS = [(PTBRANCH eps)]], $ptascii("offsetGet"))',
        '$access_frame(S, pcallcontext, pframe)',
        '$access_reference_get(S, paccess)',
        '$reference_callback_used(S, pcallcontext) = (true)',
        '$reference_return_used(S)',
        '$reference_return_fetch_valid(S, z)',
        '~$call_task_valid(S, RETURN_REF_FETCH $(z + 1))',
        'pframe_bad = pframe[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_saved*]',
        'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$access_frame(S_bad, pcallcontext, pframe_bad)',
        '$reference_callback_used(S_bad, pcallcontext) = eps',
        '~$call_frames_valid(S_bad, S_bad.FRAMES)',
        'S.BASE = BASE_VALUE (VARIABLE ($ptascii("value")) z_name)',
        '$lookup(S.ENV, $ptascii("value")) = (n_value)',
        'S.STORE[n_value] = DEFINED (PINT 17)',
        '~(n_value <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_value) = 1',
        '~$typed_reference_name_source(S, $ptascii("value"))',
        'S_read = $read_name(S, $ptascii("value"), z)',
        'S_read.RESULT = KNOWN (PINT 17)',
        'S_checked = $typed_return_checked(S_read, z, false)',
        'S_checked.COMPLETION = NORMAL',
        'S_checked.RESULT = KNOWN (PFLOAT ($float_of_int(17)))',
        'S_checked.STORE = S.STORE',
        *guards('S'),
        'PhpStep: S ~> S_unwind',
        'S_unwind.COMPLETION = NORMAL',
        'S_unwind.TODO = (RETURN_REF_UNWIND (REFERENCE n_value) z false porigin_return) :: ptask_unwind*',
        'S.ORIGIN = (porigin_return)',
        'S_unwind.RESULT = KNOWN PNULL',
        'S_unwind.REFCELLS = n_value :: S.REFCELLS',
        'S_unwind.STORE = $set_cell(S.STORE, n_value, DEFINED (PFLOAT ($float_of_int(17))))',
        'S_unwind.ALLOCATIONS = S.ALLOCATIONS',
        'S_unwind.PROPREFS = S.PROPREFS',
        'S_unwind.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_unwind), HCELL n_value) = 2',
        '~$typed_reference_name_source(S_unwind, $ptascii("value"))',
        *guards('S_unwind'),
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = S_unwind.TODO',
        'S_one.RESULT = S_unwind.RESULT',
        'S_one.CURRENT = S_unwind.CURRENT',
        'S_one.FRAMES = S_unwind.FRAMES',
        'S_one.STORE = S_unwind.STORE',
        'S_one.REFCELLS = S_unwind.REFCELLS',
        'S_one.PROPREFS = S_unwind.PROPREFS',
        'S_one.EVENTS = S_unwind.EVENTS',
        '$call_descriptors_valid(S_one)',
        '$heap_valid($heap_graph(S_one))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
