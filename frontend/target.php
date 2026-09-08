<?php declare(strict_types=1);

// PHP-Parser version targeting is best effort. These pinned Zend grammar/lexer
// restrictions are syntax checks, not compilation or evaluation.
function checkTargetSyntax(array $ast, array $tokens): void {
    $pending = [];
    foreach ($ast as $node) $pending[] = [$node, null, '', 0, 0];
    while ($pending) {
        [$node, $parent, $field, $index, $count] = array_pop($pending);
        $reject = null;
        if ($node instanceof PhpParser\Node\Expr\Cast\Double && $node->getAttribute('kind') === PhpParser\Node\Expr\Cast\Double::KIND_REAL) {
            $reject = 'The (real) cast is not PHP 8.5 syntax';
        } elseif ($node instanceof PhpParser\Node\Stmt\Function_ && in_array(strtolower($node->name->name), ['exit', 'die'], true)) {
            $reject = 'exit/die cannot be function declaration names';
        } elseif ($node instanceof PhpParser\Node\Stmt\Class_ && $node->name === null && ($node->flags & ~PhpParser\Modifiers::READONLY)) {
            $reject = 'Only readonly is an anonymous-class modifier';
        } elseif ($node instanceof PhpParser\Node\Stmt\ClassMethod && ($node->flags & PhpParser\Modifiers::READONLY)) {
            $reject = 'readonly is not a method modifier';
        } elseif ($node instanceof PhpParser\Node\Expr\Cast\Void_) {
            $statement = $parent instanceof PhpParser\Node\Stmt\Expression
                && $node->getStartTokenPos() === $parent->getStartTokenPos();
            $for = $parent instanceof PhpParser\Node\Stmt\For_
                && (in_array($field, ['init', 'loop'], true) || ($field === 'cond' && $index < $count - 1));
            if ($for) {
                $before = $node->getStartTokenPos() - 1;
                while ($before >= 0 && in_array($tokens[$before]->id, [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)) --$before;
                $for = $before >= 0 && in_array($tokens[$before]->text, [',', ';'], true);
                if (!$for && $before >= 0 && $tokens[$before]->text === '(') {
                    --$before;
                    while ($before >= 0 && in_array($tokens[$before]->id, [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)) --$before;
                    $for = $before >= 0 && $tokens[$before]->id === T_FOR;
                }
            }
            if (!$statement && !$for) $reject = '(void) is only allowed in statement/discarded for-expression positions';
        }
        if ($reject !== null) throw new PhpParser\Error($reject, $node->getAttributes());
        foreach ($node->getSubNodeNames() as $name) {
            $value = $node->{$name};
            if ($value instanceof PhpParser\Node) $pending[] = [$value, $node, $name, 0, 1];
            elseif (is_array($value)) foreach ($value as $i => $child) {
                if ($child instanceof PhpParser\Node) $pending[] = [$child, $node, $name, $i, count($value)];
            }
        }
    }
    $nowdoc = false;
    foreach ($tokens as $token) {
        if ($token->id === T_START_HEREDOC) $nowdoc = str_contains($token->text, "'");
        if ($token->id === T_END_HEREDOC) $nowdoc = false;
        $text = $token->text;
        $quoted = $token->id === T_CONSTANT_ENCAPSED_STRING
            && (str_starts_with($text, '"') || str_starts_with(strtolower($text), 'b"'));
        if (!$quoted && ($token->id !== T_ENCAPSED_AND_WHITESPACE || $nowdoc)) continue;
        for ($i = 0, $length = strlen($text); $i < $length; ++$i) {
            if ($text[$i] !== '\\') continue;
            ++$i;
            if ($i + 1 >= $length || $text[$i] !== 'u' || $text[$i + 1] !== '{') continue;
            $end = strpos($text, '}', $i + 2);
            $digits = $end === false ? '' : substr($text, $i + 2, $end - $i - 2);
            $significant = ltrim($digits, '0');
            if ($digits === '' || !ctype_xdigit($digits) || strlen($significant) > 6 || hexdec($significant ?: '0') > 0x10ffff) {
                throw new PhpParser\Error('Invalid Unicode code point escape', ['startLine' => $token->line]);
            }
            $i = $end;
        }
    }
}
