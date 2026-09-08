<?php declare(strict_types=1);

function withSourceEncodingProfile(callable $action) {
    $selected = getenv('PHP_SPEC_SCRIPT_ENCODING');
    if ($selected === false || !ini_get('zend.multibyte')) return $action();
    // Match CLI -d's INI builder, including quoted values, before relocating
    // this one setting away from startup loading of the tooling itself.
    if ($selected !== '' && !ctype_alnum($selected[0]) && $selected[0] !== '"' && $selected[0] !== "'") $selected = '"' . $selected . '"';
    $settings = parse_ini_string('zend.script_encoding=' . $selected, false, INI_SCANNER_NORMAL);
    $selected = $settings['zend.script_encoding'] ?? '';
    $previous = ini_get('zend.script_encoding');
    // Zend warns and keeps the preceding/default value for an invalid encoding.
    if (ini_set('zend.script_encoding', $selected) === false) return $action();
    try {
        return $action();
    } finally {
        // The Zend handler rejects an empty list; restore its original null
        // default through the INI restoration API rather than ini_set('').
        if ($previous === false || $previous === '') ini_restore('zend.script_encoding');
        elseif (ini_set('zend.script_encoding', $previous) === false) throw new RuntimeException('Cannot restore source script_encoding profile');
    }
}

// Materialize bytes only for Zend's native file-scanning API. Never include or
// execute this temporary source; the scanner and parser helper only read it.
function withPhpSourceFile(string $source, callable $action) {
    $file = tmpfile();
    if ($file === false) throw new RuntimeException('Cannot create syntax input');
    try {
        if (fwrite($file, $source) !== strlen($source)) throw new RuntimeException('Cannot write syntax input');
        fflush($file);
        return withSourceEncodingProfile(static fn() => $action(stream_get_meta_data($file)['uri']));
    } finally {
        fclose($file);
    }
}

class FileLexer extends PhpParser\Lexer {
    public array $encodingEvents = [];
    /** Native lexer tokens, filtered source, selected encoding and skipped preamble. */
    public array $info = [];

    public function tokenize(string $code, ?PhpParser\ErrorHandler $errorHandler = null): array {
        $this->info = withPhpSourceFile($code, fn(string $path): array =>
            php_spec_lex_file($path, $this->encodingEvents));
        $tokens = array_map(static fn(array $token): PhpParser\Token =>
            new PhpParser\Token(...$token), $this->info['tokens']);
        // Reuse upstream bad-character/comment checks, ampersand handling and EOF.
        $this->postprocessTokens($tokens, $errorHandler ?? new PhpParser\ErrorHandler\Throwing());
        return $tokens;
    }
}
