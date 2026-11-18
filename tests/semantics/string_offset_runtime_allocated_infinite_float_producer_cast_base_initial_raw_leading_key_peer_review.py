"""Independent infinite-cast authority, emitted arithmetic and NaN refusals."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_infinite_float_producer_cast_base_initial_raw_leading_key_review import render as render_infinite
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def prefix(body):
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, control_program, control_filename_b64):
    body = prefix(render_infinite(program, filename_b64, reference=True)[0])
    checks = []
    for node in ('base', 'chain', 'inner', 'cast'):
        for label, line, flag in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    for node, expression in (
            ('cast', 'NExprCastString expression_integer eps'),
            ('integer', 'NExprUnaryMinus expression_atom eps'),
            ('atom', 'NScalarFloat (FLOAT "7ff0000000000000") eps'),
            ('inner_suffix', 'NScalarString (BYTES text_inner_suffix) eps')):
        state = f'S_peer_source_{node}'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
    checks += lines(r'''
S_peer_live = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$number_text(NFLOAT 18442240474082181120,17) = ($ptascii("-INF"),false)
~$string_read_allocated_value(S_peer_live,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_peer_live,porigin_base,pvalue_base)
S_peer_match = S_peer_live[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cast 17) :: (PCCPRECISION pcpath_integer 17) :: (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_value(S_peer_match,porigin_cast,pvalue_cast)
S_peer_sign = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_integer z_integer false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_peer_sign,porigin_integer) = eps
$string_read_runtime_value(S_peer_sign,porigin_integer) = (PFLOAT 18442240474082181120)
$string_read_allocated_value(S_peer_sign,porigin_cast,pvalue_cast)
$string_read_allocated_base(S_peer_sign,porigin_base,pvalue_base)
S_peer_short = S_capture[.PRECISIONINI = $ptascii("1")][.PRECISIONMODIFIED = true][.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cast 1) :: (PCCPRECISION pcpath_integer 1) :: (PCCPRECISION pcpath_atom 1) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("-"),$ptascii("-INFbc"),$ptascii("-INFbcde")]]
$number_text(NFLOAT 18442240474082181120,1) = ($ptascii("-"),false)
$string_read_allocated_value(S_peer_short,porigin_cast,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("-")))
~$string_read_allocated_base(S_peer_short,porigin_base,pvalue_base)
S_peer_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-INFbcde")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-INFbcde"))
$string_carrier_valid(S_peer_clone,pvalue_clone)
~$string_read_allocated_base(S_peer_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_peer_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
~$string_read_allocated_value(S_capture,porigin_cast,PSTRING ($ptascii("-INF")))
~$string_read_allocated_value(S_capture,porigin_cast,PSTRING_CARRIER INTERNED_STRING ($ptascii("-INF")))
S_peer_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-INFbcde")]]
$heap_graph(S_peer_later) = $heap_graph(S)
$string_read_raw_saved(S_peer_later,pstringread) = (3)
$string_read_ready(S_peer_later,pstringread)
$string_read_resume(S_peer_later,pstringread) = S_peer_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN PNULL)]) = eps
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-INF"),$ptascii("-INFbc"),[45,73,78,70,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([45,73,78,70,98,99,0,100,101])
$string_carrier_valid(S_peer_nul,pvalue_nul)
~$string_read_allocated_base(S_peer_nul,porigin_base,pvalue_nul)
$string_read_raw_capture(S_peer_nul[.RESULT = KNOWN pvalue_nul],poperand,pvalue_nul) = eps
expression_positive = NScalarFloat (FLOAT "7ff0000000000000") metadata_integer
expression_positive_cast = NExprCastString expression_positive metadata_cast
expression_positive_inner = NExprBinaryOpConcat expression_positive_cast expression_inner_suffix metadata_inner
expression_positive_chain = NExprBinaryOpConcat expression_positive_inner expression_suffix metadata_chain
expression_positive_base = NExprBinaryOpCoalesce expression_positive_chain expression_skipped metadata_base
pcoccurrence_positive* = $pcwalk([PCOCCURRENCE pcpath_base expression_positive_base])
pvalue_positive_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("INF"))
pvalue_positive_base = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("INFbcde"))
S_peer_positive = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_positive* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_integer (PFLOAT 9218868437227405312)) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("INF"),$ptascii("INFbc"),$ptascii("INFbcde")]][.RESULT = KNOWN pvalue_positive_base]
$string_read_runtime_value(S_peer_positive,porigin_integer) = (PFLOAT 9218868437227405312)
$string_read_allocated_value(S_peer_positive,porigin_cast,pvalue_positive_cast)
$string_read_allocated_base(S_peer_positive,porigin_base,pvalue_positive_base)
$string_read_raw_capture(S_peer_positive,poperand,pvalue_positive_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_plan(S_peer_positive) = (pstringread[.READ.BASE = pvalue_positive_base][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_positive_base)])
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    control = prefix(render_float(control_program, control_filename_b64)[0]).split('def $main() = true\n', 1)[1]
    control = control.replace('10.5', 'INF').replace('4622100592565682176', '9218868437227405312')
    control = control.replace('FINITE 0 n_float_num n_float_den', 'INFINITE 0')
    control = control.replace('([49])', '([73])').replace('R:1;K:', 'R:I;K:')
    old = 'expression_integer = NScalarFloat (FLOAT "4025000000000000") metadata_integer'
    assert control.count(old) == 1
    control = control.replace(old, 'expression_integer = NExprBinaryOpMul expression_selected expression_factor metadata_integer')
    control = control.replace('$code_expression(pcode.EXPRESSIONS,pcpath_integer) = ((z_integer,true))',
                              '$code_expression(pcode.EXPRESSIONS,pcpath_integer) = ((z_integer,false))')
    for helper in ('compiled_read', 'compiled_identity_value'):
        old = f'${helper}(S_capture,porigin_integer) = (PFLOAT 9218868437227405312)'
        assert control.count(old) == 1
        control = control.replace(old, f'${helper}(S_capture,porigin_integer) = eps')
    emitted = lines(r'''
expression_selected = NExprTernary expression_condition expression_large expression_two metadata_selected
expression_condition = NExprCastInt expression_one metadata_condition
expression_one = NScalarInt (INTEGER 1) metadata_one
expression_large = NScalarFloat (FLOAT text_large) metadata_large
expression_two = NScalarFloat (FLOAT "4000000000000000") metadata_two
expression_factor = NScalarFloat (FLOAT "4024000000000000") metadata_factor
$origin_child((porigin_integer),[PCFIELD 0]) = (porigin_selected)
$origin_child((porigin_integer),[PCFIELD 1]) = (porigin_factor)
$origin_child((porigin_selected),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_selected),[PCFIELD 1]) = (porigin_large)
$origin_child((porigin_selected),[PCFIELD 2]) = (porigin_two)
$origin_child((porigin_condition),[PCFIELD 0]) = (porigin_one)
n_large = $hex_bits(text_large,0)
$float_decode(n_large) = FINITE 0 n_num n_den
$string_read_runtime_value(S_capture,porigin_selected) = (PFLOAT n_large)
$string_read_runtime_value(S_capture,porigin_factor) = (PFLOAT 4621819117588971520)
$number_binary(MULTIPLY,NFLOAT n_large,NFLOAT 4621819117588971520) = NUM (NFLOAT 9218868437227405312)
$binary_apply(S_capture,MULTIPLY,PFLOAT n_large,PFLOAT 4621819117588971520,z_integer) = S_capture[.RESULT = KNOWN (PFLOAT 9218868437227405312)]
''')
    for node in ('selected', 'factor', 'condition', 'large', 'two', 'one'):
        emitted += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                    f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    emitted += lines(r'''
expression_nan_large = NScalarFloat (FLOAT "7ff0000000000000") metadata_large
expression_nan_factor = NScalarFloat (FLOAT "0000000000000000") metadata_factor
expression_nan_selected = NExprTernary expression_condition expression_nan_large expression_two metadata_selected
expression_nan_integer = NExprBinaryOpMul expression_nan_selected expression_nan_factor metadata_integer
expression_nan_cast = NExprCastString expression_nan_integer metadata_cast
expression_nan_inner = NExprBinaryOpConcat expression_nan_cast expression_inner_suffix metadata_inner
expression_nan_base = NExprBinaryOpConcat expression_nan_inner expression_suffix metadata_chain
pcoccurrence_nan* = $pcwalk([PCOCCURRENCE pcpath_base expression_nan_base])
pvalue_nan_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("NAN"))
pvalue_nan_base = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("NANbcde"))
S_peer_nan = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_nan* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_large (PFLOAT 9218868437227405312)) :: (PCONSTANT pcpath_factor (PFLOAT 0)) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("NAN"),$ptascii("NANbc"),$ptascii("NANbcde")]][.RESULT = KNOWN pvalue_nan_base]
$string_read_runtime_value(S_peer_nan,porigin_selected) = (PFLOAT 9218868437227405312)
$string_read_runtime_value(S_peer_nan,porigin_factor) = (PFLOAT 0)
$number_binary(MULTIPLY,NFLOAT 9218868437227405312,NFLOAT 0) = NUM (NFLOAT n_nan)
$float_decode(n_nan) = NOTNUMBER n_nan
$binary_apply(S_peer_nan,MULTIPLY,PFLOAT 9218868437227405312,PFLOAT 0,z_integer) = S_peer_nan[.RESULT = KNOWN (PFLOAT n_nan)]
$number_bool(NFLOAT n_nan) = (true,true)
$number_text(NFLOAT n_nan,14) = ($ptascii("NAN"),true)
$string_read_runtime_value(S_peer_nan,porigin_integer) = eps
$string_read_runtime_bytes(S_peer_nan,porigin_integer) = eps
$string_carrier_valid(S_peer_nan,pvalue_nan_cast)
~$string_read_allocated_value(S_peer_nan,porigin_cast,pvalue_nan_cast)
~$string_read_allocated_base(S_peer_nan,porigin_base,pvalue_nan_base)
$string_read_raw_capture(S_peer_nan,poperand,pvalue_nan_base) = eps
S_peer_nan_prefix = S_peer_nan[.STRINGDATA = S_peer_nan.STRINGDATA[0:1]]
S_peer_nan_cast = $cast_apply(S_peer_nan_prefix,CASTSTRING,PFLOAT n_nan,z_key)
S_peer_nan_cast =/= S_peer_nan_prefix[.STRINGDATA = S_peer_nan_prefix.STRINGDATA ++ [$ptascii("NAN")]][.RESULT = KNOWN pvalue_nan_cast]
''')
    control += ''.join('  -- if ' + check + '\n' for check in emitted)
    body = body.replace('dec $main() : bool',
                        'dec $peer_emitted_infinite() : bool\ndef $peer_emitted_infinite() = true\n' + control + '\ndec $main() : bool')
    body += '  -- if $peer_emitted_infinite()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(control.splitlines()), len(checks) + len(emitted)
