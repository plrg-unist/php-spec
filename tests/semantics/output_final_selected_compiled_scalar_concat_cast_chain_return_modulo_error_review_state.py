#!/usr/bin/env python3
"""Independent compiler epoch, child authority, quiet bytes and retirement checks."""
import output_final_selected_compiled_scalar_concat_cast_chain_return_modulo_error_state as current
import output_final_selected_compiled_scalar_concat_cast_chain_return_modulo_error_sources as sources

CASES = {name: sources.CASES['native-selected-compiled-scalar-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-positive-both', 'deprecated-both-cv-pair-negative-zero-right',
                      'warning-deprecated-constant-float-keyword-suffix', 'deprecated-both-cv-pair-negative-infinity']}
runner, CONJ = current.runner, current.CONJ
PREFIX = current.PREFIX + r'''
dec $or150_source_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or150_source_drop(eps, pcpath) = eps
def $or150_source_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = $or150_source_drop(pcoccurrence*, pcpath)
def $or150_source_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or150_source_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
dec $or150_value_at(pconstant, pcpath) : bool
def $or150_value_at(PCONSTANT pcpath_fact pvalue, pcpath) = (pcpath_fact = pcpath)
def $or150_value_at(pconstant, pcpath) = false -- otherwise
dec $or150_value_drop(pconstant*, pcpath) : pconstant*
def $or150_value_drop(eps, pcpath) = eps
def $or150_value_drop(pconstant :: pconstant_tail*, pcpath) = $or150_value_drop(pconstant_tail*, pcpath)
  -- if $or150_value_at(pconstant, pcpath)
def $or150_value_drop(pconstant :: pconstant_tail*, pcpath) = pconstant :: $or150_value_drop(pconstant_tail*, pcpath)
  -- if ~$or150_value_at(pconstant, pcpath)
'''


def value(state, name, key='value', function='pfunction_handler', expression=None):
    return ('$ob_object_cast_chain_value(' + state + ', ' + function + ', porigin_' + key + ', ' +
            (current.expression(name, key) if expression is None else expression) + ')')


def epoch(paths, precision='1', state='S'):
    facts = ', '.join('PCCPRECISION pcpath_' + key + ' ' + precision for key in paths)
    return state + '[.POOLS = ppool_handler[.CONSTANTS = [' + facts + '] ++ ppool_handler.CONSTANTS] :: S.POOLS]'


def pool(state, rows):
    facts = ', '.join('PCONSTANT pcpath_' + key + ' (' + result + ')' for key, result in rows)
    return state + '[.POOLS = ppool_handler[.CONSTANTS = [' + facts + '] ++ ppool_handler.CONSTANTS] :: S.POOLS]'


def source(rows):
    facts = ', '.join('PCOCCURRENCE pcpath_' + key + ' (' + expression + ')' for key, expression in rows)
    return 'S[.SOURCES = pcunit_handler[.OCCURRENCES = [' + facts + '] ++ pcunit_handler.OCCURRENCES] :: S.SOURCES]'


def code(key, line, flag):
    return ('pfunction_handler[.CODE.EXPRESSIONS = (CODEEXPR pcpath_' + key + ' ' + line + ' ' + flag +
            ') :: pfunction_handler.CODE.EXPRESSIONS]')


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    result = nodes['value'][3]
    expression = current.expression(name, 'value')
    raw = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING')
    checks += [('the real compiler tree has exact plain bytes and one INTERNED NORMAL entry',
                '$parser_literal_at(' + expression + ', 14) = eps' + CONJ +
                '$compiled_read(S, porigin_value) = (' + raw + ')' + CONJ +
                value('S', name) + ' = (' + result + ')'),
               ('an abrupt preset INTERNED result cannot replace the genuine NORMAL entry',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', name) + ' = eps'),
               ('the selected function UNIT authenticates every compiled child',
                value('S', name, function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + ' = eps'),
               ('later live INI does not reformat the already compiled scalar tree',
                value('$precision_memory(S, 1)', name) + ' = (' + result + ')')]
    missing = epoch(['value', 'value_left', 'value_right'], '14', 'S[.DECLARATIONS = eps]')
    checks += [('explicit PCC14 rows cannot replace missing declaration source precision',
                '$source_precision(' + missing + ', (porigin_value)) = eps' + CONJ +
                '$compiled_precision(' + missing + ', (porigin_value)) = (14)' + CONJ +
                value(missing, name) + ' = eps')]
    for key, node in nodes.items():
        dropped = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                   '$or150_source_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [('every indexed child and cast retains its own SOURCE authority',
                    value(dropped, name, 'cast') + ' = eps')]
        if node[0] == 'constant':
            dropped = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                       '$or150_source_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ' ++ [PCFIELD 0])] :: S.SOURCES]')
            checks += [('a keyword cannot borrow its proper NName SOURCE from its pool',
                        value(dropped, name) + ' = eps')]
        if node[0] != 'NExprBinaryOpConcat':
            continue
        own = node[3]
        for child in [key, key + '_left', key + '_right']:
            checks += [('each root or child PCC must match source14 even when bytes coincide',
                        value(epoch([child]), name, key) + ' = eps'),
                       ('parent and both child CODE flags remain true independently',
                        value('S', name, key, code(child, 'z_' + child, 'false')) + ' = eps')]
        checks += [('the folded parent retains the positive terminal RHS compiler line',
                    value('S', name, key, code(key, '$(z_' + key + ' + 1)', 'true')) + ' = eps')]
        absent = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                  '$or150_value_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
        checks += [('an absent own byte pool cannot borrow its children or source text',
                    value(absent, name, key) + ' = eps')]
        for wrong in ['PINT 0', own, 'POBJECT 0', 'PSTRING ($ptascii("wrong"))']:
            checks += [('the own compiler pool requires the exact plain STRING tag and bytes',
                        value(pool('S', [(key, wrong)]), name, key) + ' = eps')]
        effect = ('S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key +
                  '_left) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]')
        checks += [('unconsumed child effects cannot supply a quiet whole-state constant entry',
                    value(effect, name, key) + ' = eps')]
        for child in [key + '_left', key + '_right']:
            checks += [('an owning child pool cannot borrow an otherwise intact parent certificate',
                        value(pool('S', [(child, 'POBJECT 0')]), name, key) + ' = eps')]
    if current.DETAILS[name][1] == 'positive-both':
        left = current.expression(name, 'value_left')
        nul = 'NScalarString (BYTES "AA==") metadata_value_right'
        concat = 'NExprBinaryOpConcat (' + left + ') (' + nul + ') metadata_value'
        state = pool(source([('value', concat), ('value_right', nul)]),
                     [('value_right', 'PSTRING ([0])'), ('value', 'PSTRING ([49, 46, 53, 0])')])
        checks += [('exact compiled NUL bytes cannot bypass the existing child VALUE refusal',
                    '$compiled_special_concat_bytes(' + state + ', porigin_value) = ([49, 46, 53, 0])' + CONJ +
                    value(state, name, expression=concat) + ' = eps')]
        nan = 'NScalarFloat (FLOAT "7ff8000000000000") metadata_value_left'
        right = current.expression(name, 'value_right')
        concat = 'NExprBinaryOpConcat (' + nan + ') (' + right + ') metadata_value'
        state = pool(source([('value', concat), ('value_left', nan)]),
                     [('value_left', 'PFLOAT 9221120237041090560'), ('value', 'PSTRING ($ptascii("NAN0"))')])
        checks += [('canonical NaN has a numeric child but no quiet compiler STRING certificate',
                    value(state, name, 'value_left', expression=nan) + ' = (PFLOAT 9221120237041090560)' + CONJ +
                    '$parser_literal_text_at(PFLOAT 9221120237041090560, 14) = eps' + CONJ +
                    '$compiled_special_concat_bytes(' + state + ', porigin_value) = eps' + CONJ +
                    value(state, name, expression=concat) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the compiled bytes and strict scalar result survive real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ +
                'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', name) + ' = (' + current.nodes(name)['value'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
