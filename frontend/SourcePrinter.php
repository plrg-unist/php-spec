<?php declare(strict_types=1);

// Encoded source files can contain ASCII escapes whose decoded literal bytes
// have no character representation in the source encoding. Emit those bytes as
// escapes before converting the freshly printed file back to its encoding.
final class SourcePrinter extends PhpParser\PrettyPrinter\Standard {
    public ?object $sourceEncoding = null;
    private string $marker = '';
    private array $switches = [];

    public function printChunks(array $nodes): array {
        for ($attempt = 0; ; ++$attempt) {
            $this->marker = "\0PHP_SPEC_ENCODING_{$attempt}_";
            $this->switches = [];
            $printed = $nodes === [] && $this->sourceEncoding !== null
                && bytes($this->sourceEncoding->preamble) !== '' ? '' : parent::prettyPrintFile($nodes);
            // A source byte string can contain any marker. Retry deterministically
            // with another marker until only the inserted boundaries remain.
            if (substr_count($printed, $this->marker) === count($this->switches)) break;
        }
        $chunks = [];
        $offset = 0;
        $encoding = $this->sourceEncoding === null ? 'raw' : bytes($this->sourceEncoding->source);
        foreach ($this->switches as $index => $next) {
            $marker = $this->marker . $index . "\0";
            $position = strpos($printed, $marker, $offset);
            if ($position === false) throw new RuntimeException('Missing generated encoding boundary');
            $chunks[] = ['source' => substr($printed, $offset, $position - $offset), 'encoding' => $encoding];
            $encoding = $next;
            $offset = $position + strlen($marker);
        }
        $chunks[] = ['source' => substr($printed, $offset), 'encoding' => $encoding];
        return $chunks;
    }

    protected function pStmt_Declare(PhpParser\Node\Stmt\Declare_ $node): string {
        $header = 'declare (' . $this->pCommaSeparated($node->declares) . ')';
        $selected = null;
        if (ini_get('zend.multibyte')) foreach ($node->declares as $item) {
            if (strcasecmp($item->key->name, 'encoding') === 0 && $item->value instanceof PhpParser\Node\Scalar\String_) {
                // Zend's encoding lookup consumes a C string; retain the full
                // literal payload but select the prefix before its first NUL.
                try { $selected = canonicalEncoding(explode("\0", $item->value->value, 2)[0]); } catch (ValueError $error) {}
            }
        }
        if ($selected !== null) {
            $header .= $this->marker . count($this->switches) . "\0";
            $this->switches[] = $selected;
        }
        return $header . ($node->stmts !== null ? ' {' . $this->pStmts($node->stmts) . $this->nl . '}' : ';');
    }

    protected function pScalar_String(PhpParser\Node\Scalar\String_ $node): string {
        if ($this->sourceEncoding !== null && preg_match('/[\x80-\xff]/', $node->value)) {
            return '"' . $this->escapeString($node->value, '"') . '"';
        }
        return parent::pScalar_String($node);
    }

    protected function escapeString(string $string, ?string $quote): string {
        $escaped = parent::escapeString($string, $quote);
        if ($this->sourceEncoding === null) return $escaped;
        return preg_replace_callback('/[\x80-\xff]/', static fn(array $match): string =>
            sprintf('\\x%02x', ord($match[0])), $escaped);
    }
}
