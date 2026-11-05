<?php declare(strict_types=1);

// Rejected eval units need the real string scanner's stopping point. The raw
// tokenizer can retain later tokens after a malformed Unicode escape.
final class RejectedEvalLexer extends PhpParser\Lexer {
    public function tokenize(string $code, ?PhpParser\ErrorHandler $errorHandler = null): array {
        $tokens = array_map(static fn(array $token): PhpParser\Token =>
            new PhpParser\Token(...$token), php_spec_lex_eval($code));
        $this->postprocessTokens($tokens, $errorHandler ?? new PhpParser\ErrorHandler\Throwing());
        return $tokens;
    }
}

final class RejectedFileLexer extends PhpParser\Lexer {
    public function tokenize(string $code, ?PhpParser\ErrorHandler $errorHandler = null): array {
        $raw = withPhpSourceFile($code, static fn(string $path): array => php_spec_lex_file_rejected($path));
        $tokens = array_map(static fn(array $token): PhpParser\Token =>
            new PhpParser\Token(...$token), $raw);
        $this->postprocessTokens($tokens, $errorHandler ?? new PhpParser\ErrorHandler\Throwing());
        return $tokens;
    }
}

// Rejected sources have no complete AST. Preserve foreign grammar reductions,
// rather than scanning later tokens or constructing a provisional statement.
final class RejectedHeaderParser extends PhpParser\Parser\Php8 {
    public array $headers = [];
    public bool $parsingStarted = false;

    protected function doParse(): ?array {
        // Lexing inspects the complete source before grammar reductions start.
        // Retain only tokens before its first error, then let the real parser
        // stop at any earlier syntax error without recovery past either fault.
        if ($this->errorHandler instanceof PhpParser\ErrorHandler\Collecting
            && $this->errorHandler->hasErrors()) {
            $positions = [];
            foreach ($this->errorHandler->getErrors() as $error) {
                $position = $error->getAttributes()['startFilePos'] ?? null;
                if (!is_int($position) || $position < 0) {
                    throw new RuntimeException('Lexical error has no checked source position');
                }
                $positions[] = $position;
            }
            $boundary = min($positions);
            $index = 0;
            while (isset($this->tokens[$index]) && $this->tokens[$index]->pos < $boundary) ++$index;
            $token = $this->tokens[$index] ?? null;
            if ($token === null || $token->pos !== $boundary) {
                throw new RuntimeException('Lexical error lost its token boundary');
            }
            $this->tokens = array_slice($this->tokens, 0, $index);
            $this->tokens[] = new PhpParser\Token(0, "\0", $token->line, $token->pos);
        }
        $this->errorHandler = new PhpParser\ErrorHandler\Throwing();
        $this->parsingStarted = true;
        return parent::doParse();
    }

    protected function initReduceCallbacks(): void {
        parent::initReduceCallbacks();
        // Pinned PHP-Parser 5.8 grammar: declare_list is
        // non_empty_declare_list no_comma (rule 243, default $$ = $1).
        if ($this->ruleToLength[243] !== 2 || $this->reduceCallbacks[243] !== null) {
            throw new RuntimeException('Declare header reduction contract changed');
        }
        $this->reduceCallbacks[243] = static function (self $self, int $stackPos): void {
            $self->semValue = $self->semStack[$stackPos - 1];
            $close = $self->tokens[$self->tokenPos];
            if ($close->id !== ord(')')) return;
            $begin = $self->tokenStartStack[$stackPos - 3];
            if ($self->tokens[$begin]->id !== T_DECLARE
                || $self->tokens[$self->tokenStartStack[$stackPos - 2]]->id !== ord('(')) {
                throw new RuntimeException('Declare header reduction lost its prefix');
            }
            $self->headers[] = ['beginLine' => $self->tokens[$begin]->line,
                'beginTokenPos' => $begin, 'closeLine' => $close->line,
                'closeTokenPos' => $self->tokenPos, 'items' => $self->semValue];
        };
    }
}

function rejectedHeaderFacts(string $source, bool $evalMode, PhpParser\PhpVersion $version): array {
    $parser = new RejectedHeaderParser($evalMode ? new RejectedEvalLexer() : new RejectedFileLexer(), $version);
    try {
        $parser->parse($source, new PhpParser\ErrorHandler\Collecting());
    } catch (PhpParser\Error $error) {
        // A later syntax error leaves earlier completed reductions available.
        // Lexical errors bound the token prefix before these reductions.
    }
    if (!$parser->parsingStarted || $parser->headers === []) return [];
    return ['headers' => array_map(static function (array $header): array {
        $header['items'] = encode($header['items']);
        return $header;
    }, $parser->headers)];
}
