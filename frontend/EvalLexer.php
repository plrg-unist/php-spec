<?php declare(strict_types=1);

// PHP eval starts after an opening tag. Tokenize in that state, then remove
// the synthetic tag before PHP-Parser assigns token and byte positions.
class EvalLexer extends PhpParser\Lexer {
    public function tokenize(string $code, ?PhpParser\ErrorHandler $errorHandler = null): array {
        $prefix = '<?php ';
        $errorHandler ??= new PhpParser\ErrorHandler\Throwing();
        $scream = ini_set('xdebug.scream', '0');
        try {
            $tokens = @PhpParser\Token::tokenize($prefix . $code);
            $opening = array_shift($tokens);
            if ($opening->id !== T_OPEN_TAG || $opening->text !== $prefix || $opening->pos !== 0) {
                throw new RuntimeException('Eval lexer lost its opening-tag state');
            }
            foreach ($tokens as $token) $token->pos -= strlen($prefix);
            $this->postprocessTokens($tokens, $errorHandler);
            return $tokens;
        } finally {
            if ($scream !== false) ini_set('xdebug.scream', $scream);
        }
    }
}

// These are PHP-Parser's post-parse namespace checks. Zend accepts their
// grammar and leaves the corresponding static errors to compilation.
function namespaceStructureErrorMatches(PhpParser\Error $error, array $ast): bool {
    $position = $error->getAttributes()['startTokenPos'] ?? null;
    if (!is_int($position)) return false;
    $message = $error->getRawMessage();
    if ($message === 'Namespace declaration statement has to be the very first statement in the script'
        || $message === 'Cannot mix bracketed namespace declarations with unbracketed namespace declarations') {
        foreach ($ast as $node) {
            if ($node instanceof PhpParser\Node\Stmt\Namespace_
                && $node->getStartTokenPos() === $position) return true;
        }
    } elseif ($message === 'Namespace declarations cannot be nested') {
        $pending = $ast;
        while ($pending !== []) {
            $node = array_pop($pending);
            if (!$node instanceof PhpParser\Node\Stmt\Namespace_) continue;
            foreach ($node->stmts ?? [] as $child) {
                if ($child instanceof PhpParser\Node\Stmt\Namespace_) {
                    if ($child->getStartTokenPos() === $position) return true;
                    $pending[] = $child;
                }
            }
        }
    } elseif ($message === 'No code may exist outside of namespace {}') {
        $afterBraced = false;
        foreach ($ast as $node) {
            if ($node instanceof PhpParser\Node\Stmt\Namespace_ && $node->stmts !== null) {
                $afterBraced = true;
            } elseif ($afterBraced && $node instanceof PhpParser\Node\Stmt
                && $node->getStartTokenPos() === $position) return true;
        }
    }
    return false;
}
