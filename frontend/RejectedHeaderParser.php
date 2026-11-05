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

    protected function checkNamespace(PhpParser\Node\Stmt\Namespace_ $node): void {
        // Zend checks namespace nesting during compilation. Rejected units
        // never reach that phase; later grammar reductions still count.
    }

    // These restrictions also belong to compilation, after the full parse.
    protected function checkClass(PhpParser\Node\Stmt\Class_ $node, int $namePos): void {}
    protected function checkInterface(PhpParser\Node\Stmt\Interface_ $node, int $namePos): void {}
    protected function checkEnum(PhpParser\Node\Stmt\Enum_ $node, int $namePos): void {}
    protected function checkTryCatch(PhpParser\Node\Stmt\TryCatch $node): void {}
    protected function checkClassMethod(PhpParser\Node\Stmt\ClassMethod $node, int $modifierPos): void {}
    protected function checkPropertyHook(PhpParser\Node\PropertyHook $hook, ?int $paramListPos): void {}
    protected function checkEmptyPropertyHookList(array $hooks, int $hookPos): void {}
    protected function checkConstantAttributes(PhpParser\Node\Stmt\Const_ $node): void {}

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
        // Anonymous class modifiers reject before constructor arguments/body.
        // Match the NEW terminal, not a statement-list value beginning there.
        if ($this->ruleToLength[221] !== 2 || $this->reduceCallbacks[221] !== null) {
            throw new RuntimeException('Class entry reduction contract changed');
        }
        $this->reduceCallbacks[221] = static function (self $self, int $stackPos): void {
            $self->semValue = $self->semStack[$stackPos - 1];
            if ($self->tokens[$self->tokenStartStack[$stackPos]]->id !== T_CLASS) {
                throw new RuntimeException('Class entry reduction lost its class token');
            }
            $new = $self->tokenStartStack[$stackPos - 3] ?? null;
            if (($self->semValue & (PhpParser\Modifiers::ABSTRACT | PhpParser\Modifiers::FINAL))
                && $new !== null && $new >= 0 && $self->tokens[$new]->id === T_NEW
                && $self->tokenEndStack[$stackPos - 3] === $new
                && $self->semStack[$stackPos - 3] === $self->tokens[$new]->text) {
                throw new PhpParser\Error('Invalid modifier for anonymous class');
            }
        };
        // Methods/constants share this reduction before parameters/initializers.
        // Their actual lookahead selects the target-specific flag set.
        if ($this->ruleToLength[384] !== 1 || $this->reduceCallbacks[384] !== null) {
            throw new RuntimeException('Member modifier reduction contract changed');
        }
        $this->reduceCallbacks[384] = static function (self $self, int $stackPos): void {
            $self->semValue = $self->semStack[$stackPos];
            $allowed = PhpParser\Modifiers::PUBLIC | PhpParser\Modifiers::PROTECTED
                | PhpParser\Modifiers::PRIVATE | PhpParser\Modifiers::FINAL;
            $target = $self->tokens[$self->tokenPos]->id;
            if ($target === T_FUNCTION) $allowed |= PhpParser\Modifiers::STATIC | PhpParser\Modifiers::ABSTRACT;
            if (($target === T_FUNCTION || $target === T_CONST) && ($self->semValue & ~$allowed)) {
                // Only a foreign parse stop; the reply retains native diagnostics.
                throw new PhpParser\Error($target === T_FUNCTION
                    ? 'Invalid modifier for method' : 'Invalid modifier for class constant');
            }
        };
        // Zend validates a trait alias's single modifier while reducing the
        // alias, before parsing later declarations in a rejected unit.
        foreach ([372 => 5, 373 => 4] as $rule => $length) {
            if ($this->ruleToLength[$rule] !== $length || !is_callable($this->reduceCallbacks[$rule])) {
                throw new RuntimeException('Trait alias reduction contract changed');
            }
            $reduce = $this->reduceCallbacks[$rule];
            $this->reduceCallbacks[$rule] = static function (self $self, int $stackPos) use ($reduce, $length): void {
                $modifier = $self->semStack[$stackPos - ($length - 3)];
                $allowed = PhpParser\Modifiers::PUBLIC | PhpParser\Modifiers::PROTECTED
                    | PhpParser\Modifiers::PRIVATE | PhpParser\Modifiers::STATIC
                    | PhpParser\Modifiers::ABSTRACT | PhpParser\Modifiers::FINAL;
                if ($modifier & ~$allowed) {
                    throw new PhpParser\Error('Invalid modifier for trait alias');
                }
                $reduce($self, $stackPos);
            };
        }
        // Zend's hooked-property branch has one variable. After a comma,
        // its grammar rejects the opening brace before parsing any hook body.
        if ($this->ruleToLength[399] !== 3 || !is_callable($this->reduceCallbacks[399])) {
            throw new RuntimeException('Property list reduction contract changed');
        }
        $reduce = $this->reduceCallbacks[399];
        $this->reduceCallbacks[399] = static function (self $self, int $stackPos) use ($reduce): void {
            $reduce($self, $stackPos);
            if ($self->tokens[$self->tokenPos]->id === ord('{')) {
                throw new PhpParser\Error('Invalid multi-property hook syntax');
            }
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
