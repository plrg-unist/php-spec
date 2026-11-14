"""Quiet signed64 modulo, shifts, bitwise and power trees retain a literal base."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpBitwiseXor expression_or_group expression_xor_two_group metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_root_group)
porigin_root_group = porigin_cond
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    nodes = (
        ('root', 'BitwiseXor', 'BITXOR', 'or', 'xor_two', 1),
        ('or', 'BitwiseOr', 'BITOR', 'and', 'or_one', 3),
        ('and', 'BitwiseAnd', 'BITAND', 'shr', 'and_three', 2),
        ('shr', 'ShiftRight', 'SHIFTRIGHT', 'shl', 'shr_one', 2),
        ('shl', 'ShiftLeft', 'SHIFTLEFT', 'mod', 'shl_one', 4),
        ('mod', 'Mod', 'MODULO', 'power', 'mod_three', 2),
        ('power', 'Pow', 'POWER', 'power_two', 'power_three', 8))
    leaves = dict(power_two=2, power_three=3, mod_three=3, shl_one=1,
                  shr_one=1, and_three=3, or_one=1, xor_two=2)
    values = {name: value for name, _, _, _, _, value in nodes} | leaves
    for name, constructor, operator, left, right, value in nodes:
        metadata = 'metadata_cond' if name == 'root' else f'metadata_{name}_group'
        checks += lines(f'''
expression_{name}_group = NExprBinaryOp{constructor} expression_{left}_group expression_{right}_group {metadata}
$origin_node(S_capture.SOURCES,porigin_{name}_group) = (expression_{name}_group)
$origin_child((porigin_{name}_group),[PCFIELD 0]) = (porigin_{left}_group)
$origin_child((porigin_{name}_group),[PCFIELD 1]) = (porigin_{right}_group)
$origin_node(S_capture.SOURCES,porigin_{left}_group) = (expression_{left}_group)
$origin_node(S_capture.SOURCES,porigin_{right}_group) = (expression_{right}_group)
$compiled_read(S_capture,porigin_{name}_group) = (PINT {value})
$string_read_raw_unary_integer(S_capture,porigin_{name}_group,{value})
$binary_apply(S_capture,{operator},PINT {values[left]},PINT {values[right]},0) = S_capture[.RESULT = KNOWN (PINT {value})]
''')
    for name, value in leaves.items():
        checks += lines(f'''
expression_{name}_group = NScalarInt (INTEGER {value}) metadata_{name}_group
$compiled_read(S_capture,porigin_{name}_group) = (PINT {value})
''')
    checks += lines(r'''
$string_read_raw_truth(S_capture,porigin_cond,PINT 1)
porigin_power_group = PORIGIN n_unit pcpath_power_group
porigin_mod_group = PORIGIN n_unit pcpath_mod_group
porigin_power_two_group = PORIGIN n_unit pcpath_power_two_group
S_budget_group = S_capture[.COMPLETION = BUDGET]
$string_read_raw_unary_integer(S_budget_group,porigin_cond,1)
$string_read_raw_known_base(S_budget_group,porigin_base,pkeyread.BASE)
S_precision_group = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision_group,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PINT 0'),
            ('power', 'pcpath_power_group', 'PINT 9'),
            ('mod', 'pcpath_mod_group', 'PINT 0'),
            ('type', 'pcpath_power_group', 'PFLOAT 4620693217682128896')):
        checks += lines(f'''
S_pool_{label}_group = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label}_group,porigin_cond,{'PINT 0' if label == 'own' else 'PINT 1'})
~$string_read_raw_known_base(S_pool_{label}_group,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('power', 'pcpath_power_group', 'NExprBinaryOpPow expression_power_two_group expression_power_three_group eps'),
            ('leaf', 'pcpath_power_two_group', 'NScalarInt (INTEGER 2) eps')):
        checks += lines(f'''
S_metadata_{label}_group = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_metadata_{label}_group,porigin_cond,PINT 1)
~$string_read_raw_known_base(S_metadata_{label}_group,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
