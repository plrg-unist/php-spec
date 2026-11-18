#!/usr/bin/env python3
"""Independent positive-INF boundary, parser epochs and actual retirement checks."""
import output_final_selected_parser_infinite_float_concat_cast_chain_return_modulo_error_state as current
import output_final_selected_parser_infinite_float_concat_cast_chain_return_modulo_error_sources as sources

CASES = {name: sources.CASES['native-selected-parser-infinite-float-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-left-empty-infinity', 'warning-deprecated-constant-float-infinity-finite']}
fields = ('DETAILS', 'TREES', 'CASTS', 'sources', 'raw', 'expression', 'modulo_line',
          'converted', 'return_proof', 'return_bindings')
pristine = [(module, {field: getattr(module, field) for field in fields if hasattr(module, field)})
            for module in [current.shared, current.shared.prior]]
bits, text = dict(current.prior.BITS), dict(current.prior.TEXT)
import output_final_selected_parser_float_concat_cast_chain_return_modulo_error_review_state as previous
for module, saved in pristine:
    for field, original in saved.items():
        setattr(module, field, original)
current.prior.BITS.clear(); current.prior.BITS.update(bits)
current.prior.TEXT.clear(); current.prior.TEXT.update(text)

runner, PREFIX, CONJ = current.runner, previous.PREFIX, current.CONJ
value, query, compiled = previous.value, previous.query, previous.compiled
floating, control = previous.floating, previous.control


def epoch(path):
    return ('S[.POOLS = ppool_handler[.CONSTANTS = (PCCPRECISION ' + path +
            ' 1) :: ppool_handler.CONSTANTS] :: S.POOLS]')


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 '$source_precision(S, (porigin_value)) = (14)',
                 'S_live = S[.PRECISIONINI = [49]][.PRECISIONMODIFIED = true]']
    expression = current.expression(name, 'value')
    result, raw = current.carrier(name), current.plain(name)
    checks += [('the actual parser tree retains its exact nonowning INTERNED NORMAL entry',
                current.parser_proof(name) + CONJ + value('S', expression) + ' = (' + result + ')'),
               ('a preset result cannot replace the genuine NORMAL parser entry',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the selected function UNIT must authenticate its parser root',
                value('S', expression, function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + ' = eps'),
               ('missing source precision cannot borrow existing pool bytes',
                '$source_precision(S[.DECLARATIONS = eps], (porigin_value)) = eps' + CONJ +
                value('S[.DECLARATIONS = eps]', expression) + ' = eps'),
               ('live precision1 leaves the already parsed source14 STRING unchanged',
                '$precision_value(S_live) = 1' + CONJ +
                '$source_precision(S_live, (porigin_value)) = (14)' + CONJ +
                value('S_live', expression) + ' = (' + result + ')')]
    for key, node in current.nodes(name).items():
        if key != 'value':
            child_epoch = epoch('pcpath_' + key)
            checks += [('a pruned child PCC1 cannot replace the source14 parser conversion',
                        '$compiled_precision(' + child_epoch + ', (porigin_' + key + ')) = (1)' + CONJ +
                        '$source_precision(' + child_epoch + ', (porigin_' + key + ')) = (14)' + CONJ +
                        value(child_epoch, expression) + ' = (' + result + ')')]
        if isinstance(node, float):
            checks += [('each raw FLOAT retains its own indexed SOURCE and parser-time bytes',
                        '$ob_object_parser_string(S, porigin_' + key + ', ' + current.expression(name, key) +
                        ') = ' + current.data(current.prior.TEXT[node]))]
    for key in ['cast', 'cast_1', *current.nodes(name)]:
        missing = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                   '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [('every proper indexed child and cast retains independent SOURCE authority',
                    value(missing, current.expression(name), origin='porigin_cast') + ' = eps')]
    root_epoch = epoch('pcpath_value')
    checks += [('root PCC1 changes INF bytes and downgrades the retained source14 pool to plain STRING',
                '$compiled_precision(' + root_epoch + ', (porigin_value)) = (1)' + CONJ +
                '$source_precision(' + root_epoch + ', (porigin_value)) = (14)' + CONJ +
                '$parser_literal_at(' + expression + ', 1) =/= (' + raw + ')' + CONJ +
                '$compiled_string_value(' + root_epoch + ', porigin_value, ' + raw + ') = ' + raw + CONJ +
                '$enter_compiled_task(' + root_epoch + ', porigin_value, EVAL (' + expression + '), ' +
                root_epoch + '.TODO) = ' + root_epoch + '[.RESULT = KNOWN (' + raw + ')]' + CONJ +
                value(root_epoch, expression) + ' = eps')]
    for line, flag in [('$(z_value + 1)', 'true'), ('z_value', 'false')]:
        checks += [('the own parser root keeps its exact concat line and true CODE flag',
                    value('S', expression, function=control.code_function('pcpath_value', line, flag)) + ' = eps')]
    for wrong in ['PINT 0', result, 'POBJECT 0', 'PSTRING ($ptascii("wrong"))']:
        checks += [('the own pool requires the exact plain STRING tag and bytes',
                    value(control.pool_state('pcpath_value', wrong), expression) + ' = eps')]
    absent = ('S[.POOLS = ppool_handler[.CONSTANTS = '
              '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_value)] :: S.POOLS]')
    effect = ('S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_value_left) :: '
              'pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]')
    checks += [('an absent root pool cannot borrow the parsed source spelling', value(absent, expression) + ' = eps'),
               ('pending effects cannot supply a whole-state parser constant entry', value(effect, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'left-empty-infinity':
        checks += [('the exact old149 positive-INF query is promoted through its original builder',
                    compiled(query((floating('7ff0000000000000'), b''), b'INF'))),
                   ('the previous maximum finite payload retains its original pure parser bytes',
                    compiled(query((floating('7fefffffffffffff'), b''), b'1.7976931348623E+308')))]
        for payload, answer in [('8000000000000000', b'-0'), ('bff8000000000000', b'-1.5'),
                                ('fff0000000000000', b'-INF')]:
            checks += [('signed raw payloads remain refused despite matching pool and INTERNED entry',
                        previous.previous.matched_refusal(query((floating(payload), b''), answer)))]
        for payload in ['7ff0000000000001', '7ff8000000000000', 'fff8000000000000']:
            state, tree, function, _, _ = query((floating(payload), b''), b'INF')
            checks += [('canonical NaN remains outside the quiet raw parser boundary',
                        value(state, tree, function=function) + ' = eps')]
        for payload in ['7FF0000000000000', '7ff000000000000', '07ff0000000000000', '7fg0000000000000']:
            state, tree, _, _, _ = query((floating(payload), b''), b'INF')
            checks += [('malformed infinity payloads use only the guarded parser-helper refusal route',
                        '$ob_object_parser_string(' + state + ', porigin_value, ' + tree + ') = eps')]
        state, tree, function, _, _ = query((b'\0', floating('7ff0000000000000')), b'\0INF')
        checks += [('an admitted infinity sibling cannot admit a NUL parser STRING',
                    value(state, tree, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('parser infinity bytes and strict scalar results retain actual formal/native retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ +
                'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 'value')) + ' = (' + current.carrier(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
