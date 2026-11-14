"""Folded string complement truth preserves exact bytes and the frozen offset."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBitwiseNot expression_byte_not metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PSTRING ([49]))')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PSTRING ([49]))')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBitwiseNot expression_byte_not metadata_cond)
expression_byte_not = NScalarString (BYTES text_byte_not) metadata_byte_not
$base64(text_byte_not) = [206]
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_byte_not)
$origin_node(S_capture.SOURCES,porigin_byte_not) = (expression_byte_not)
$compiled_read(S_capture,porigin_byte_not) = (PSTRING ([206]))
$string_read_raw_truth(S_capture,porigin_byte_not,PSTRING ([206]))
$bitnot_value(S_capture,PSTRING ([206]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_raw_truth(S_capture,porigin_cond,PSTRING ([49]))
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_byte_not = PORIGIN n_unit pcpath_byte_not
S_budget_byte_not = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING ([0]))]
$string_read_raw_truth(S_budget_byte_not,porigin_cond,PSTRING ([49]))
$string_read_raw_known_base(S_budget_byte_not,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own_byte', 'pcpath_cond', 'PSTRING ([48])'),
            ('own_tag', 'pcpath_cond', 'PINT 1'),
            ('own_carrier', 'pcpath_cond', 'PSTRING_CARRIER INTERNED_STRING ([49])'),
            ('child_byte', 'pcpath_byte_not', 'PSTRING ([207])'),
            ('child_tag', 'pcpath_byte_not', 'PINT 206')):
        own = value if path == 'pcpath_cond' else 'PSTRING ([49])'
        checks += [f'S_bad_byte_not_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_byte_not_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_byte_not_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('root', 'pcpath_cond', 'NExprBitwiseNot expression_byte_not eps'),
            ('child', 'pcpath_byte_not', 'NScalarString (BYTES text_byte_not) eps')):
        checks += [f'S_bad_byte_not_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_byte_not_{label}_source,porigin_cond,PSTRING ([49]))',
                   f'~$string_read_raw_known_base(S_bad_byte_not_{label}_source,porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
