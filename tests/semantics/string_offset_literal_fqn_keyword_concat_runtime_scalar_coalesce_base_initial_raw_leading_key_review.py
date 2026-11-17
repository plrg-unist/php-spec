"""Fully qualified +false retains STRING0 and authentic original Name SOURCE."""

import base64

from string_offset_literal_unary_keyword_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_signed
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_signed(program, filename_b64)
    body = body.replace('NName (BYTES', 'NNameFullyQualified (BYTES')
    checks = lines(r'''
S_fqn_plain_name_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_name_false (NName (BYTES text_keyword_false) metadata_name_false)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_fqn_plain_name_shadow,porigin_left) = (PSTRING ($ptascii("0")))
$string_read_runtime_value(S_fqn_plain_name_shadow,porigin_left) = eps
~$string_read_raw_known_base(S_fqn_plain_name_shadow,porigin_base,pkeyread.BASE)
''')
    for constructor, sign in (('', ''), ('NExprUnaryPlus', ''), ('NExprUnaryMinus', '-')):
        for spelling, unsigned in (('TrUe', '1'), ('FALSE', ''), ('NuLl', '')):
            encoded = base64.b64encode(spelling.encode()).decode()
            expression = f'NExprConstFetch (NNameFullyQualified (BYTES "{encoded}") eps) eps'
            if constructor:
                expression = f'{constructor} ({expression}) eps'
            text = sign + unsigned if unsigned else ('0' if constructor else '')
            checks.append(f'$string_read_folded_concat_bytes({expression}) = ($ptascii("{text}"))')
        for spelling in ('\\true', 'foo', 'foo\\true'):
            encoded = base64.b64encode(spelling.encode()).decode()
            expression = f'NExprConstFetch (NNameFullyQualified (BYTES "{encoded}") eps) eps'
            if constructor:
                expression = f'{constructor} ({expression}) eps'
            checks.append(f'$string_read_folded_concat_bytes({expression}) = eps')
        expression = 'NExprConstFetch (NNameRelative (BYTES "dHJ1ZQ==") eps) eps'
        if constructor:
            expression = f'{constructor} ({expression}) eps'
        checks.append(f'$string_read_folded_concat_bytes({expression}) = eps')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
