#!/usr/bin/env python3
"""Independent exact numeric returns preserve raw-string and carrier authority."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_string_numeric_cast_return_modulo_error_state as current
import output_final_selected_string_numeric_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-string-numeric-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or125_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or125_drop(eps, pcpath) = eps
def $or125_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or125_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or125_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''
LOCAL = {
    'int': [(b'', '0'), (b'x', '0'), (b'-4.75tail', '$(-4)'),
            (b'9223372036854775808', '9223372036854775807'),
            (b'-9223372036854775809', '$(-9223372036854775808)'),
            (b'1e999', '0'), (b'\0', '0')],
    'float': [(b'', '0'), (b'x', '0'), (b'0.125tail', str(0x3fc0000000000000)),
              (b'-0', str(0x8000000000000000)), (b'1e999', str(0x7ff0000000000000)),
              (b'-1e999', str(0xfff0000000000000)), (b'\0', '0')]}


def shape(name):
    return (('NExprCastInt', 'CASTINT', 'PINT i_return', '1') if current.KINDS[name] == 'int'
            else ('NExprCastDouble', 'CASTFLOAT', 'PFLOAT n_return', '2'))


def variant(name, data, metadata='metadata_cast'):
    child = 'NScalarString (BYTES "' + base64.b64encode(data).decode() + '") metadata_string'
    cast = shape(name)[0] + ' (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                                  ('pcpath_string', child)])
    return state, statement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    _, operator, result, kind = shape(name)
    tail = control.tail
    carrier = 'PSTRING_CARRIER INTERNED_STRING n_string*'
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]'
    checks += [
        ('exact raw pool and mandatory nonowning carrier produce the actual typed numeric result',
         tail() + r' /\ $compiled_read(S, porigin_string) = (PSTRING n_string*) /\ '
         r'$compiled_string_value(S, porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string* /\ '
         '$cast_apply(S, ' + operator + ', ' + carrier + ', z_cast) = S[.RESULT = KNOWN (' + result + r')] /\ '
         r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps'),
        ('numeric returns including zero remain distinct from strict FALSE and resumed NULL',
         'S_handler.RESULT = KNOWN (' + result + r') /\ '
         r'S_handler.RESULT =/= KNOWN (PBOOL false) /\ S_handler.RESULT =/= KNOWN PNULL /\ S.RESULT = KNOWN PNULL'),
        ('NORMAL remains required when an abrupt cast already has its expected typed scratch',
         '$cast_apply(' + abrupt + ', ' + operator + ', ' + carrier + ', z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', ' + operator + ', ' + carrier + ', z_cast) = ' +
         abrupt + '[.RESULT = KNOWN (' + result + r')] /\ ~' + tail(abrupt)),
        ('the original silent strict-type value witness emitted no failure marker',
         r'S.EVENTS = [OUTPUT ([80])] /\ S_handler.RESULT =/= KNOWN (PBOOL false)'),
        ('handler CODE unit must retain its source identity',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('handler BODY must retain its actual source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for label, source_path, line, flag in [
            ('emitted root flag', 'pcpath_cast', 'z_cast', 'true'),
            ('raw child flag', 'pcpath_string', 'z_string', 'false'),
            ('cast line', 'pcpath_cast', '$(z_cast + 1)', 'false'),
            ('string line', 'pcpath_string', '$(z_string + 1)', 'true')]:
        checks += [(label + ' cannot be forged independently of actual source',
                    '~' + tail(function=control.code_function(source_path, line, flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('root', 'pcpath_cast'),
                               ('raw string', 'pcpath_string')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or125_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the own ' + label + ' source refuses the tail', '~' + tail(state))]
    shadow = control.source_state([('pcpath_string',
        'NScalarString (BYTES "b3RoZXIxMjU=") metadata_string')])
    checks += [('an indexed-child shadow defeats unchanged Return/root and raw pool', '~' + tail(shadow))]
    for label, metadata in [('alias', '(Mkind ' + ('2' if kind == '1' else '1') + ') :: metadata_cast'),
                            ('missing kind', 'eps')]:
        state, statement = variant(name, current.STRINGS[name].encode(), metadata)
        checks += [(label + ' cannot replace the canonical cast kind ' + kind, '~' + tail(state, statement=statement))]
    for value in ['PBOOL false', 'PNULL', 'PINT 0', 'PFLOAT 0', carrier,
                  'PSTRING ($ptascii("other"))']:
        checks += [('child pool ' + value + ' cannot replace exact raw string bytes',
                    '~' + tail(control.pool_state('pcpath_string', value)))]
    checks += [('missing child pool refuses', '~' + tail('S[.POOLS = eps]'))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    root_pool = control.pool_state('pcpath_cast', result)
    checks += [('a genuinely folded root refuses even with the correct numeric pool',
                '~' + tail(root_pool + '[.CODE = ' + global_code + ' :: S.CODE]')),
               ('an ignored raw root pool does not replace emitted read-eps authority',
                '$compiled_read(' + root_pool + r', porigin_cast) = eps /\ ' + tail(root_pool))]
    bindings += ['S_no_precision = S[.DECLARATIONS = eps][.POOLS = '
                 'ppool_handler[.CONSTANTS = [(PCONSTANT pcpath_string (PSTRING n_string*))]] :: S.POOLS]']
    checks += [('missing precision refuses despite exact raw bytes and matching quiet numeric cast',
                r'$compiled_read(S_no_precision, porigin_string) = (PSTRING n_string*) /\ '
                r'$compiled_precision(S_no_precision, (porigin_string)) = eps /\ '
                r'$compiled_string_value(S_no_precision, porigin_string, PSTRING n_string*) = PSTRING n_string* /\ '
                '$cast_apply(S_no_precision, ' + operator + ', PSTRING n_string*, z_cast) = '
                'S_no_precision[.RESULT = KNOWN (' + result + r')] /\ ~' + tail('S_no_precision'))]
    for data, expected in LOCAL[current.KINDS[name]]:
        state, statement = variant(name, data)
        raw = '($base64("' + base64.b64encode(data).decode() + '"))'
        state += control.pool_state('pcpath_string', 'PSTRING ' + raw)[1:]
        tag = 'PINT' if kind == '1' else 'PFLOAT'
        helper = '$string_cast_integer' if kind == '1' else '$string_cast_float'
        expected_value = tag + ' ' + expected
        checks += [('source0 ' + repr(data) + ' preserves dedicated ' + operator + ' result and nonNUL boundary',
                    helper + '(' + raw + ') = ' + expected + r' /\ '
                    '$compiled_read(' + state + ', porigin_string) = (PSTRING ' + raw + r') /\ '
                    '$compiled_string_value(' + state + ', porigin_string, PSTRING ' + raw + ') = '
                    'PSTRING_CARRIER INTERNED_STRING ' + raw + r' /\ '
                    '$cast_apply(' + state + ', ' + operator + ', PSTRING_CARRIER INTERNED_STRING ' + raw + ', z_cast) = ' +
                    state + '[.RESULT = KNOWN (' + expected_value + r')] /\ ' +
                    ('~' if 0 in data else '') + tail(state, statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    result = shape(name)[2]
    checks += [('actual retirement keeps numeric result distinct from FALSE and preserves nonowning carrier identity',
                'S_handler.RESULT = KNOWN (' + result + r') /\ '
                r'S_handler.RESULT =/= KNOWN (PBOOL false) /\ S_handler.RESULT =/= KNOWN PNULL /\ '
                r'S.RESULT = KNOWN PNULL /\ $value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps /\ '
                r'$compiled_string_value(S_report, porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string*')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
