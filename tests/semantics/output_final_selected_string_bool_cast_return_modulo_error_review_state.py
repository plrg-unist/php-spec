#!/usr/bin/env python3
"""Independent raw string pools and nonowning runtime BOOL carriers stay distinct."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_string_bool_cast_return_modulo_error_state as current
import output_final_selected_string_bool_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-string-bool-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or124_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or124_drop(eps, pcpath) = eps
def $or124_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or124_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or124_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def bytes_value(data):
    return '($base64("' + base64.b64encode(data).decode() + '"))'


def variant(data, metadata='metadata_cast'):
    payload = base64.b64encode(data).decode()
    child = 'NScalarString (BYTES "' + payload + '") metadata_string'
    cast = 'NExprCastBool (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                                  ('pcpath_string', child)])
    return state, statement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    tail = control.tail
    carrier = 'PSTRING_CARRIER INTERNED_STRING n_string*'
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL b_return)]'
    checks += [
        ('raw compiled bytes and the actual nonowning INTERNED carrier are separately authenticated',
         tail() + r' /\ $compiled_read(S, porigin_cast) = eps /\ '
         r'$compiled_read(S, porigin_string) = (PSTRING n_string*) /\ '
         r'$compiled_read(S, porigin_string) =/= (PSTRING_CARRIER INTERNED_STRING n_string*) /\ '
         r'$compiled_string_value(S, porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string* /\ '
         r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps'),
        ('the full carrier cast has exact Boolean truth and preserves every other state field',
         '$cast_apply(S, CASTBOOL, ' + carrier + ', z_cast) = S[.RESULT = KNOWN (PBOOL b_return)]'),
        ('NORMAL remains necessary when an abrupt cast already has its expected Boolean scratch',
         '$cast_apply(' + abrupt + ', CASTBOOL, ' + carrier + ', z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', CASTBOOL, ' + carrier + ', z_cast) = ' +
         abrupt + r'[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail(abrupt)),
        ('handler CODE unit must match its real source',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('handler BODY must retain its actual source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for label, source_path, line, flag in [
            ('emitted root flag', 'pcpath_cast', 'z_cast', 'true'),
            ('raw string child flag', 'pcpath_string', 'z_string', 'false'),
            ('cast line', 'pcpath_cast', '$(z_cast + 1)', 'false'),
            ('string line', 'pcpath_string', '$(z_string + 1)', 'true')]:
        checks += [(label + ' cannot be forged independently of actual source',
                    '~' + tail(function=control.code_function(source_path, line, flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('root', 'pcpath_cast'),
                               ('raw string', 'pcpath_string')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or124_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the own ' + label + ' source refuses the tail', '~' + tail(state))]
    shadow = control.source_state([('pcpath_string',
        'NScalarString (BYTES "b3RoZXIxMjQ=") metadata_string')])
    checks += [('an earlier indexed child shadow defeats unchanged Return/root and raw pool', '~' + tail(shadow))]
    for label, metadata in [('BOOLEAN alias', '(Mkind 2) :: metadata_cast'), ('missing kind', 'eps')]:
        state, statement = variant(current.STRINGS[name].encode(), metadata)
        checks += [(label + ' cannot certify the canonical bool cast', '~' + tail(state, statement=statement))]
    for value in ['PBOOL false', 'PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 0', carrier,
                  'PSTRING ($ptascii("other"))']:
        checks += [('child pool ' + value + ' cannot replace exact raw PSTRING bytes',
                    '~' + tail(control.pool_state('pcpath_string', value)))]
    checks += [('missing child pool cannot certify a literal string', '~' + tail('S[.POOLS = eps]'))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    root_pool = control.pool_state('pcpath_cast', 'PBOOL b_return')
    checks += [('a genuinely folded root refuses even with its correct Boolean result',
                '~' + tail(root_pool + '[.CODE = ' + global_code + ' :: S.CODE]')),
               ('an ignored raw root pool does not replace emitted read-eps authority',
                '$compiled_read(' + root_pool + r', porigin_cast) = eps /\ ' + tail(root_pool))]
    bindings += ['S_no_precision = S[.DECLARATIONS = eps][.POOLS = '
                 'ppool_handler[.CONSTANTS = [(PCONSTANT pcpath_string (PSTRING n_string*))]] :: S.POOLS]']
    checks += [('missing precision refuses the mandatory carrier despite exact raw pool and both quiet cast answers',
                r'S_no_precision.COMPLETION = NORMAL /\ S_no_precision.SOURCES = S.SOURCES /\ '
                r'S_no_precision.CODE = S.CODE /\ $compiled_read(S_no_precision, porigin_cast) = eps /\ '
                r'$compiled_read(S_no_precision, porigin_string) = (PSTRING n_string*) /\ '
                r'$compiled_precision(S_no_precision, (porigin_string)) = eps /\ '
                r'$compiled_string_value(S_no_precision, porigin_string, PSTRING n_string*) = PSTRING n_string* /\ '
                r'$cast_apply(S_no_precision, CASTBOOL, PSTRING n_string*, z_cast) = S_no_precision[.RESULT = KNOWN (PBOOL b_return)] /\ '
                '$cast_apply(S_no_precision, CASTBOOL, ' + carrier + ', z_cast) = '
                r'S_no_precision[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail('S_no_precision'))]
    for data in [b'', b'0', b'00', b'x', b'false', b'0.0', b' ', b'\xff', b'\0', b'0\0']:
        state, statement = variant(data)
        value = bytes_value(data)
        state += control.pool_state('pcpath_string', 'PSTRING ' + value)[1:]
        truth = 'false' if data in [b'', b'0'] else 'true'
        checks += [('source0 local ' + repr(data) + ' follows byte-string truth and the unchanged nonNUL boundary',
                    '$compiled_read(' + state + ', porigin_string) = (PSTRING ' + value + r') /\ '
                    '$compiled_string_value(' + state + ', porigin_string, PSTRING ' + value + ') = '
                    'PSTRING_CARRIER INTERNED_STRING ' + value + r' /\ '
                    '$value_nodes(PSTRING_CARRIER INTERNED_STRING ' + value + r') = eps /\ '
                    '$cast_apply(' + state + ', CASTBOOL, PSTRING_CARRIER INTERNED_STRING ' + value + ', z_cast) = ' +
                    state + '[.RESULT = KNOWN (PBOOL ' + truth + r')] /\ ' +
                    ('~' if 0 in data else '') + tail(state, statement=statement))]
        if data in [b'', b'0']:
            other = 'PSTRING ($ptascii("0"))' if not data else 'PSTRING eps'
            wrong = state + control.pool_state('pcpath_string', other)[1:]
            checks += [('source0 empty and sole-zero strings refuse exchanged raw pools despite equal FALSE casts',
                        '$cast_apply(' + wrong + ', CASTBOOL, ' + other + ', z_cast) = ' +
                        wrong + r'[.RESULT = KNOWN (PBOOL false)] /\ ~' + tail(wrong, statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual retirement preserves Boolean output, NULL scratch and the nonowning literal header',
                r'S_handler.RESULT = KNOWN (PBOOL b_return) /\ '
                r'S_handler.RESULT =/= KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN PNULL /\ '
                r'S.RESULT = KNOWN PNULL /\ $value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps /\ '
                r'$compiled_string_value(S_report, porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string*')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
