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
