#!/usr/bin/env python3
"""Independent raw-integer BOOL casts retain exact sources and strict return tags."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_integer_bool_cast_return_modulo_error_state as current
import output_final_selected_integer_bool_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-integer-bool-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or121_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or121_drop(eps, pcpath) = eps
def $or121_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or121_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or121_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def variant(integer='i_child', metadata='metadata_cast'):
    child = 'NScalarInt (INTEGER ' + integer + ') metadata_integer'
    cast = 'NExprCastBool (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                                  ('pcpath_integer', child)])
    return state, statement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    tail = control.tail
    abrupt = ('S[.COMPLETION = UNSUPPORTED "peer121 completion"]'
              '[.RESULT = KNOWN (PBOOL b_return)]')
    expected = str(current.VALUES[name] != 0).lower()
    checks += [
        ('the emitted BOOL root has no folded value while its exact signed64 child is pooled',
         tail() + r' /\ $pool_value(S.POOLS, porigin_cast) = eps /\ '
         r'$compiled_read(S, porigin_integer) = (PINT i_child) /\ $long_range(i_child)'),
        ('the quiet cast returns the expected Boolean and preserves every other state field',
         'b_return = ' + expected + r' /\ '
         r'$cast_apply(S, CASTBOOL, PINT i_child, z_cast) = S[.RESULT = KNOWN (PBOOL b_return)]'),
        ('zero or nonzero BOOL results never become numeric zero or NULL',
         r'$cast_apply(S, CASTBOOL, PINT i_child, z_cast) =/= S[.RESULT = KNOWN (PINT 0)] /\ '
         r'$cast_apply(S, CASTBOOL, PINT i_child, z_cast) =/= S[.RESULT = KNOWN PNULL]'),
        ('NORMAL remains required even when an abrupt cast already has its expected result',
         '$cast_apply(' + abrupt + ', CASTBOOL, PINT i_child, z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', CASTBOOL, PINT i_child, z_cast) = ' +
         abrupt + r'[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail(abrupt)),
        ('the handler CODE unit must match its real source',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('the handler BODY must retain its exact source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for label, source_path, line, flag in [
            ('emitted root flag', 'pcpath_cast', 'z_cast', 'true'),
            ('pooled child flag', 'pcpath_integer', 'z_integer', 'false'),
            ('cast line', 'pcpath_cast', '$(z_cast + 1)', 'false'),
            ('integer line', 'pcpath_integer', '$(z_integer + 1)', 'true')]:
        checks += [(label + ' cannot be forged independently of the actual child/source',
                    '~' + tail(function=control.code_function(source_path, line, flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('root', 'pcpath_cast'),
                               ('raw integer', 'pcpath_integer')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or121_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the own ' + label + ' source occurrence refuses the tail', '~' + tail(state))]
    shadow = control.source_state([('pcpath_integer',
        'NScalarInt (INTEGER $(i_child + 1)) metadata_integer')])
    checks += [('an earlier indexed-child shadow defeats unchanged Return/root rows', '~' + tail(shadow))]
    for label, metadata in [('BOOLEAN alias', '(Mkind 2) :: metadata_cast'), ('missing kind', 'eps')]:
        state, statement = variant(metadata=metadata)
        checks += [(label + ' cannot certify the canonical bool cast', '~' + tail(state, statement=statement))]
    wrong_integer = 'PINT 1' if current.VALUES[name] == 0 else 'PINT 0'
    for value in ['PBOOL false', 'PBOOL true', 'PNULL', 'PFLOAT 0', wrong_integer]:
        checks += [('child pool ' + value + ' cannot replace the exact raw PINT',
                    '~' + tail(control.pool_state('pcpath_integer', value)))]
    checks += [('a missing child pool is not a value certificate', '~' + tail('S[.POOLS = eps]'))]
    for integer in ['9223372036854775808', '$(-9223372036854775809)']:
        state, statement = variant(integer=integer)
        state += control.pool_state('pcpath_integer', 'PINT ' + integer)[1:]
        checks += [('raw integer outside signed64 refuses even though generic truth is quietly true',
                    '$cast_apply(' + state + ', CASTBOOL, PINT ' + integer + ', z_cast) = ' +
                    state + r'[.RESULT = KNOWN (PBOOL true)] /\ ~' + tail(state, statement=statement))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    state = control.pool_state('pcpath_cast', 'PBOOL b_return')
    checks += [('a folded-root forgery cannot replace the emitted BOOL certificate',
                '~' + tail(state + '[.CODE = ' + global_code + ' :: S.CODE]'))]
    if current.VALUES[name] == 0:
        checks += [('the actual false BOOL result retains both real default diagnostics',
                    r'S_handler.RESULT = KNOWN (PBOOL false) /\ '
                    r'S_handler_right.RESULT = KNOWN (PBOOL false) /\ ' +
                    current.no.fallback_proof('S_default', 'perrorcall_return',
                                             current.no.diagnostics(name)[0], 'S_resume') + r' /\ ' +
                    current.no.fallback_proof('S_default_right', 'perrorcall_return_right',
                                             current.no.diagnostics(name)[1], 'S'))]
    else:
        checks += [('the actual nonzero BOOL result is strict TRUE and suppresses fallback',
                    r'S_handler.RESULT = KNOWN (PBOOL true) /\ '
                    r'S_handler.RESULT =/= KNOWN (PBOOL false)')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual frame retirement preserves BOOL type rather than numeric zero or NULL',
                r'S_handler.RESULT = KNOWN (PBOOL b_return) /\ '
                r'S_handler.RESULT =/= KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN PNULL /\ '
                r'S.RESULT = KNOWN PNULL')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
