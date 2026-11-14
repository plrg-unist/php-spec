"""Falsey computed strings keep the literal fallback and frozen raw offset."""

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBitwiseNot expression_string_child metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 0)', '$compiled_read(S_capture,porigin_cond) = (PSTRING ([48]))')
    body = body.replace('$compiled_read(S_other,porigin_cond) = (PINT 0)', '$compiled_read(S_other,porigin_cond) = (PSTRING ([48]))')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PSTRING ([48]))')
    body = body.replace('pvalue_condition = PINT 0', 'pvalue_condition = PSTRING_CARRIER INTERNED_STRING ([48])')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBitwiseNot expression_string_child metadata_cond)
expression_string_child = NScalarString (BYTES text_string_child) metadata_string_child
$base64(text_string_child) = [207]
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_string_child)
$origin_node(S_capture.SOURCES,porigin_string_child) = (expression_string_child)
$compiled_read(S_capture,porigin_string_child) = (PSTRING ([207]))
$string_read_raw_truth(S_capture,porigin_string_child,PSTRING ([207]))
$bitnot_value(S_capture,PSTRING ([207]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))]
$string_read_raw_truth(S_capture,porigin_cond,PSTRING ([48]))
$truth_value(S_capture,PSTRING ([48]),0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_budget_string = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 7)]
$string_read_raw_truth(S_budget_string,porigin_cond,PSTRING ([48]))
$string_read_raw_known_base(S_budget_string,porigin_base,pkeyread.BASE)
porigin_string_child = PORIGIN n_unit pcpath_string_child
porigin_false = PORIGIN n_unit pcpath_false
''')
    for label, path, value in (
            ('own_byte', 'pcpath_cond', 'PSTRING ([49])'),
            ('own_int', 'pcpath_cond', 'PINT 0'),
            ('own_carrier', 'pcpath_cond', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('child_byte', 'pcpath_string_child', 'PSTRING ([206])'),
            ('child_int', 'pcpath_string_child', 'PINT 207')):
        checks += [f'S_bad_string_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_known_base(S_bad_string_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprBitwiseNot expression_string_child eps'),
            ('child', 'pcpath_string_child', 'NScalarString (BYTES text_string_child) eps'),
            ('fallback', 'pcpath_false', 'NScalarString (BYTES text_false) eps')):
        checks += [f'S_bad_string_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_string_{label}_source,porigin_base,pkeyread.BASE)']
    for label, path in (('condition', 'pcpath_cond'), ('child', 'pcpath_string_child')):
        checks += [f'S_bad_string_{label}_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 12 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_bad_string_{label}_code,porigin_base,pkeyread.BASE)']
    for label, encoded, child, result in (('ascii_one', 'zg==', 206, 49), ('nul', '/w==', 255, 0)):
        checks += lines(f'''
expression_string_{label}_child = NScalarString (BYTES "{encoded}") metadata_string_child
expression_string_{label} = NExprBitwiseNot expression_string_{label}_child metadata_cond
expression_base_string_{label} = NExprTernary expression_string_{label} ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_string_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_string_{label}) :: (PCOCCURRENCE pcpath_cond expression_string_{label}) :: (PCOCCURRENCE pcpath_string_child expression_string_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ([{result}]))) :: (PCONSTANT pcpath_string_child (PSTRING ([{child}]))) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_string_{label},porigin_cond,PSTRING ([{result}]))
$truth_value(S_string_{label},PSTRING ([{result}]),0) = S_string_{label}[.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_known_base(S_string_{label},porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_string_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ([{result}]))
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
