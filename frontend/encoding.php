<?php declare(strict_types=1);
require_once __DIR__ . '/FileLexer.php';

// The raw file lexer and independent PHP-Parser grammar use the same real file
// profile as the reference parser. Declaration discovery never calls zendparse.
function parseWithEncoding(PhpParser\Parser &$parser, string $source): ?array {
    global $phpSyntaxFileInfo;
    $phpSyntaxFileInfo = null;
    $events = [];
    if (ini_get('zend.multibyte')) {
        $prefixParser = (new PhpParser\ParserFactory())->createForVersion(PhpParser\PhpVersion::fromComponents(8, 5));
        $cursor = 0;
        while (true) {
            $initial = withPhpSourceFile($source, static fn(string $path): array => php_spec_lex_file($path, $events));
            $tokens = $initial['tokens'];
            $found = false;
            for ($i = $cursor; $i < count($tokens); ++$i) {
                if ($tokens[$i][0] !== T_DECLARE) continue;
                $prefix = '<?php ';
                $depth = 0;
                do {
                    $token = $tokens[$i++];
                    if (in_array($token[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)) continue;
                    $prefix .= $token[1] . ' ';
                    if ($token[1] === '(') ++$depth;
                    if ($token[1] === ')') --$depth;
                } while ($i < count($tokens) && !($token[1] === ')' && $depth === 0));
                $cursor = $i;
                $declared = null;
                try {
                    $declarations = withLexerEncoding('UTF-8', static fn() =>
                        $prefixParser->parse($prefix . ';', new PhpParser\ErrorHandler\Throwing()));
                    foreach ($declarations[0]->declares as $item) {
                        if (strcasecmp($item->key->name, 'encoding') === 0 && $item->value instanceof PhpParser\Node\Scalar\String_) {
                            try { $declared = declarationEncoding($item->value->value); } catch (ValueError $error) {}
                        }
                    }
                } catch (PhpParser\Error $error) {
                    --$i;
                    continue; // The complete independent parse diagnoses malformed syntax.
                }
                if ($declared !== null) {
                    $events[] = ['token' => $i - 1, 'encoding' => $declared];
                    $found = true;
                    break; // Discover the next declaration from the correctly rescanned continuation.
                }
                --$i; // The header loop already advanced to the next token.
            }
            if (!$found) break;
        }
    }
    $lexer = new FileLexer();
    $lexer->encodingEvents = $events;
    $parser = new PhpParser\Parser\Php8($lexer, PhpParser\PhpVersion::fromComponents(8, 5));
    $ast = $parser->parse($source, new PhpParser\ErrorHandler\Throwing());
    $phpSyntaxFileInfo = $lexer->info;
    return $ast;
}

function withLexerEncoding(string $encoding, callable $action) {
    // mb_internal_encoding() changes current_internal_encoding only. Zend's lexer
    // getter reads internal_encoding, updated by this INI handler (mbstring.c:477,793).
    $previous = (string)ini_get('mbstring.internal_encoding');
    $set = static function (string $value): void {
        // Suppress only the helper's own deprecated-INI notice, not source diagnostics.
        set_error_handler(static fn(int $severity): bool => $severity === E_DEPRECATED);
        try {
            if (ini_set('mbstring.internal_encoding', $value) === false) {
                throw new RuntimeException('Cannot configure isolated lexer encoding');
            }
        } finally {
            restore_error_handler();
        }
    };
    $set($encoding);
    try {
        return $action();
    } finally {
        $set($previous);
    }
}

// Preserve actual filtered lexer bytes, including noninjective conversions.
// Original spelling provenance is metadata only and is never used to print.
function sourceEncoding(string $source, array $tokens, array $ast): ?array {
    global $phpSyntaxFileInfo;
    if ($phpSyntaxFileInfo === null) throw new RuntimeException('Missing file lexer provenance');
    $info = $phpSyntaxFileInfo;
    $selected = $info['source_encoding'];
    $events = $info['events'];
    $preamble = $info['preamble'];
    if ($selected === null && !$events && $preamble === '' && $info['source'] === $source) return null;
    $encoding = $selected === null ? 'raw' : canonicalEncoding($selected);
    $lexer = $selected === null ? 'raw' : lexerEncoding($encoding);
    $original = $info['original_source'];
    $initial = $info['initial_source'];
    $bom = '';
    if ($original !== $source) {
        $prefixLength = strlen($source) - strlen($original);
        if ($prefixLength <= 0 || substr($source, $prefixLength) !== $original) {
            throw new RuntimeException('Native original buffer is not a BOM-stripped source');
        }
        $signature = substr($source, 0, $prefixLength);
        if (!in_array($signature, ["\x00\x00\xfe\xff", "\xff\xfe\x00\x00", "\xfe\xff", "\xff\xfe", "\xef\xbb\xbf"], true)) {
            throw new RuntimeException('Unrecognized native source signature');
        }
        // With no filter Zend initially scans the unstripped file buffer. Such
        // a BOM is an InlineHTML payload; only a stripped initial BOM is metadata.
        if ($initial !== $source) $bom = $signature;
    }
    $active = $encoding;
    $filtered = convertEncoding($original, $lexer, $active);
    if ($initial === $source) $filtered = $source;
    elseif ($filtered !== $initial) throw new RuntimeException('Native initial encoding transform differs');
    if (substr($filtered, 0, strlen($preamble)) !== $preamble) {
        throw new RuntimeException('Native file preamble differs from its declared encoding');
    }
    $eventIndex = 0;
    foreach ($info['tokens'] as $ordinal => $token) {
        if (substr($filtered, $token[3], strlen($token[1])) !== $token[1]) {
            throw new RuntimeException('Native lexer token differs from its active encoding at token ' . $ordinal);
        }
        if (isset($events[$eventIndex]) && $events[$eventIndex]['token'] === $ordinal) {
            $active = canonicalEncoding($events[$eventIndex++]['encoding']);
            $filtered = convertEncoding($original, lexerEncoding($active), $active);
        }
    }
    if ($filtered !== $info['filtered_source']) {
        throw new RuntimeException('Native final buffer differs from its declared encoding');
    }
    $result = ['source' => base64_encode($encoding), 'lexer' => base64_encode($lexer),
        'bom' => base64_encode($bom), 'preamble' => base64_encode($preamble)];
    if ($events || convertEncoding($info['source'], $encoding, $lexer) !== $original) {
        $result['original'] = base64_encode($source);
    }
    return $result;
}

function convertEncoding(string $source, string $to, string $from): string {
    if ($to === $from || canonicalEncoding($to) === canonicalEncoding($from)) return $source;
    return withEncodingHelperDiagnostics(static fn() => mb_convert_encoding($source, $to, $from));
}

function withEncodingHelperDiagnostics(callable $action) {
    // Transfer codecs remain accepted by Zend's encoding fetcher; suppress only
    // deprecations raised by our own mbstring inspection/conversion calls.
    set_error_handler(static fn(int $severity): bool => $severity === E_DEPRECATED);
    try { return $action(); } finally { restore_error_handler(); }
}

function convertEncodingExact(string $source, string $to, string $from): string {
    $converted = convertEncoding($source, $to, $from);
    // An inserted NUL can change file-wide encoding detection. Prefer an
    // invalid-byte preimage when the configured replacement produced that NUL.
    $avoidNul = $to !== 'raw' && $to !== $from && ini_get('zend.multibyte')
        && ini_get('zend.detect_unicode') && str_contains($source, "\0") && str_contains($converted, "\0");
    if (!$avoidNul && convertEncoding($converted, $from, $to) === $source) return $converted;
    // mbstring's transfer encoder canonicalizes bare LF to CRLF. The standard
    // byte encoder escapes bare LF and retains the exact decoded source bytes.
    if (canonicalEncoding($to) === 'Quoted-Printable') {
        $converted = quoted_printable_encode($source);
        if (convertEncoding($converted, $from, $to) === $source) return $converted;
    }
    // A configured illegal-character replacement can occur in identifiers or
    // comments even when the source charset cannot normally encode that value.
    // Derive a byte preimage from the pinned converter, never from original text.
    $converted = '';
    $cache = [];
    $probe = convertEncoding(' A', $to, $from);
    foreach (mb_str_split($source, 1, $from) as $character) {
        if (isset($cache[$character])) { $converted .= $cache[$character]; continue; }
        $encoded = convertEncoding($character, $to, $from);
        $normal = convertEncoding($encoded, $from, $to) === $character ? $encoded : null;
        if ($normal === null || ($avoidNul && $character === "\0")) {
            $encoded = null;
            for ($byte = 0; $byte < 256; ++$byte) {
                $candidate = chr($byte);
                if ($avoidNul && $candidate === "\0") continue;
                if (convertEncoding($candidate, $from, $to) === $character
                    && convertEncoding($candidate . $probe, $from, $to) === $character . ' A'
                    && convertEncoding($probe . $candidate, $from, $to) === ' A' . $character) {
                    $encoded = $candidate;
                    break;
                }
            }
            if ($encoded === null) $encoded = $normal;
            if ($encoded === null) throw new RuntimeException('No exact source encoding preimage for checked payload');
        }
        $cache[$character] = $encoded;
        $converted .= $encoded;
    }
    if (convertEncoding($converted, $from, $to) !== $source) {
        throw new RuntimeException('Printed source encoding would lose checked payload bytes');
    }
    return $converted;
}

function printEncoding(array $chunks, ?object $encoding): string {
    $output = '';
    foreach ($chunks as $index => $chunk) {
        $source = $chunk['source'];
        if ($index === 0 && $encoding !== null) $source = bytes($encoding->preamble) . $source;
        $selected = $chunk['encoding'];
        $output .= convertEncodingExact($source, $selected, $selected === 'raw' ? 'raw' : lexerEncoding($selected));
        if (isset($chunks[$index + 1])) {
            $next = $chunks[$index + 1]['encoding'];
            $currentPrefix = convertEncoding($output, $selected === 'raw' ? 'raw' : lexerEncoding($selected), $selected);
            $nextPrefix = convertEncoding($output, $next === 'raw' ? 'raw' : lexerEncoding($next), $next);
            // Zend reconverts the whole buffer but retains the numeric cursor.
            // When the new prefix is shorter, absorb the skipped bytes in fresh
            // whitespace after the header rather than losing the next token.
            $skip = strlen($currentPrefix) - strlen($nextPrefix);
            if ($skip > 0) $output .= convertEncodingExact(str_repeat(' ', $skip), $next,
                $next === 'raw' ? 'raw' : lexerEncoding($next));
        }
    }
    if ($encoding === null) return $output;
    $bom = bytes($encoding->bom);
    // A wide encoding needs an unambiguous canonical signature: Zend's BOMless
    // UTF heuristic can select a different width after whitespace formatting.
    if ($bom === '' && bytes($encoding->source) !== bytes($encoding->lexer)) $bom = ['UTF-16LE' => "\xff\xfe", 'UTF-16BE' => "\xfe\xff",
        'UTF-32LE' => "\xff\xfe\x00\x00", 'UTF-32BE' => "\x00\x00\xfe\xff"][bytes($encoding->source)] ?? '';
    return $bom . $output;
}

function canonicalEncoding(string $name): string {
    static $aliases = null;
    if ($aliases === null) {
        $aliases = [];
        foreach (mb_list_encodings() as $encoding) {
            foreach (array_merge([$encoding], withEncodingHelperDiagnostics(static fn() => mb_encoding_aliases($encoding))) as $alias) {
                $aliases[strtolower($alias)] = $encoding;
            }
        }
    }
    return $aliases[strtolower($name)] ?? throw new ValueError('Unknown encoding');
}

function declarationEncoding(string $name): string {
    // zend_handle_encoding_declaration passes the literal to a C-string lookup.
    return canonicalEncoding(explode("\0", $name, 2)[0]);
}

function lexerEncoding(string $source): string {
    static $unsafe = null;
    if ($unsafe === null) {
        $unsafe = array_fill_keys(array_column(json_decode(file_get_contents(__DIR__ . '/../spec/lexer-encodings.json'), true), 'name'), true);
    }
    $source = canonicalEncoding($source);
    $internal = canonicalEncoding(mb_internal_encoding());
    // Zend/zend_language_scanner.l: zend_multibyte_set_filter().
    if ($source === $internal) return isset($unsafe[$source]) ? 'UTF-8' : $source;
    if (!isset($unsafe[$internal])) return $internal;
    return isset($unsafe[$source]) ? 'UTF-8' : $source;
}
