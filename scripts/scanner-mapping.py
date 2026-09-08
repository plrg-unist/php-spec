#!/usr/bin/env python3
"""Link every pinned scanner rule to emitted terminals and grammar productions."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
scanner = json.loads((ROOT / 'coverage/scanner.json').read_text())
grammar = json.loads((ROOT / 'coverage/grammar.json').read_text())
source = (ROOT / scanner['authority']).read_text()
lines = source.splitlines(keepends=True)
parser_source = (ROOT / grammar['authority']).read_text()
aliases = dict(re.findall(r'^%token\s+(?:<[^>]+>\s+)?(T_\w+)\s+("(?:[^"\\]|\\.)*")', parser_source, re.M))
constants = json.loads(subprocess.check_output([str(ROOT / '.tools/php/bin/php'), '-n', '-r',
    'echo json_encode(get_defined_constants(true)["tokenizer"]);'], text=True))
constants.update({name: int(number) for name, number in re.findall(r'\b(T_\w+)\s*=\s*(\d+)', (ROOT / 'vendor/php-src/Zend/zend_language_parser.h').read_text())})
terminal_rules = {}
for production in grammar['productions']:
    for terminal in set(production['rhs']):
        terminal_rules.setdefault(terminal, []).append(production['rule'])

punctuation = ';:,.|^&+-/*=%!~$<>?@'
dynamic = {1958: '])', 1963: '[(', 1968: punctuation, 2425: punctuation + '[](){}"`'}
goto_tokens = {'return_whitespace': 'T_WHITESPACE', 'inline_char_handler': 'T_INLINE_HTML'}
trivia = {
    'T_OPEN_TAG': 'ParserAbstract skips opening-tag trivia; the tag already selected scanner state.',
    'T_WHITESPACE': 'ParserAbstract skips grammar trivia; token positions remain available.',
    'T_COMMENT': 'CommentAnnotatingVisitor retains raw comment bytes and attachment metadata.',
    'T_DOC_COMMENT': 'CommentAnnotatingVisitor retains doc-comment identity, bytes and declaration association.',
    'T_ERROR': 'Native raw scanner error sentinel; the independent frontend reports lexical rejection.',
    'T_BAD_CHARACTER': 'Lexer::postprocessTokens reports an invalid lexical byte before grammar parsing.',
}
rows = []
for index, rule in enumerate(scanner['rules']):
    end = scanner['rules'][index + 1]['line'] - 1 if index + 1 < len(scanner['rules']) else len(lines)
    action = ''.join(lines[rule['line'] - 1:end])
    if index + 1 == len(scanner['rules']):
        action = action.split('\n*/', 1)[0]
    # Include all return-macro forms (including WITH_STR / OR_SKIP), not just
    # inventory token names. Some rules jump to a shared token-return action.
    emitted = set(re.findall(r'RETURN_(?:OR_SKIP_)?(?:EXIT_NESTING_)?TOKEN\w*\s*\(\s*(T_\w+)', action))
    emitted.update(rule['emitted_tokens'])
    for label, token in goto_tokens.items():
        if re.search(r'goto\s+' + label + r'\s*;', action): emitted.add(token)
    chars = set(re.findall(r"RETURN_(?:EXIT_NESTING_)?TOKEN\s*\(\s*'([^'\\])'", action))
    if re.search(r'RETURN_(?:EXIT_NESTING_)?TOKEN\s*\(\s*yytext\[0\]', action):
        if rule['line'] not in dynamic:
            raise RuntimeError(f'Unmapped dynamic character return: {rule["id"]}')
        chars.update(dynamic[rule['line']])
    if re.search(r'RETURN_END_TOKEN\b', action): emitted.add('EOF')
    returns = []
    for token in sorted(emitted):
        token_id = 0 if token == 'EOF' else constants[token]
        terminal = '"end of file"' if token == 'EOF' else aliases.get(token, token)
        if token == 'T_OPEN_TAG_WITH_ECHO': terminal = aliases['T_ECHO']
        if token == 'T_CLOSE_TAG': terminal = "';'"
        item = {'token': token, 'id': token_id, 'terminal': terminal,
                'productions': terminal_rules.get(terminal, [])}
        if token in trivia: item['frontend_role'] = trivia[token]
        elif token == 'EOF': item['frontend_role'] = 'Token sentinel completes the start production.'
        elif token == 'T_OPEN_TAG_WITH_ECHO': item['frontend_role'] = 'ParserAbstract::createTokenMap maps the short echo tag to T_ECHO.'
        elif token == 'T_CLOSE_TAG': item['frontend_role'] = 'ParserAbstract::createTokenMap maps the closing tag to a statement semicolon.'
        else: item['frontend_role'] = 'Named terminal passed through ParserAbstract token mapping to the independent Php8 grammar.'
        if not item['productions'] and token not in trivia:
            raise RuntimeError(f'Named terminal has no grammar mapping: {token}')
        returns.append(item)
    for char in sorted(chars):
        terminal = "'" + char + "'"
        returns.append({'token': char, 'id': ord(char), 'terminal': terminal,
                        'productions': terminal_rules.get(terminal, []),
                        'frontend_role': 'Character terminal passed to the independent Php8 grammar; illegal positions produce grammar rejection.'})
    transitions = re.findall(r'\b(?:BEGIN|yy_push_state|enter_nesting)\([^;\n]+\)|\byy_pop_state\(\)|\byyless\([^;\n]+\)|\bgoto\s+\w+\s*;|\bRESET_DOC_COMMENT\(\)', action)
    if rule['line'] == 1396:
        role = 'Shared re2c rule prologue computes matched token length before each action.'
    elif not returns:
        role = 'Rewinds/transitions scanner state and restarts without emitting a token.'
        if not transitions: raise RuntimeError(f'No role for non-emitting rule {rule["id"]}')
    else:
        role = 'Emits the listed token/character alternatives; state actions precede continued scanning.'
    rows.append({'id': rule['id'], 'line': rule['line'], 'states': rule['states'],
                 'pattern': rule['pattern'], 'action_sha256': hashlib.sha256(action.encode()).hexdigest(),
                 'role': role, 'state_actions': transitions, 'returns': returns,
                 'witnesses': rule.get('witnesses', []), 'status': rule['status']})
assert len(rows) == 191 and len({row['id'] for row in rows}) == 191
result = {'scanner': scanner['authority'], 'grammar': grammar['authority'],
          'implementation_path': ['native/php_file.c:php_spec_lex_file (raw lex_scan)',
             'frontend/FileLexer.php:FileLexer::tokenize',
             'vendor/php-parser/lib/PhpParser/Lexer.php:Lexer::postprocessTokens',
             'vendor/php-parser/lib/PhpParser/ParserAbstract.php:ParserAbstract::createTokenMap',
             'vendor/php-parser/lib/PhpParser/Parser/Php8.php (independent grammar)',
             'frontend/target.php:checkTargetSyntax (pinned lexical/grammar restrictions)'],
          'production_mapping': 'coverage/grammar.json production rule numbers; formal-domain mapping is recorded separately.',
          'rules': rows}
(ROOT / 'coverage/scanner-mapping.json').write_text(json.dumps(result, indent=2) + '\n')
print(f'Mapped {len(rows)} scanner actions, {sum(len(row["returns"]) for row in rows)} token/character alternatives')
