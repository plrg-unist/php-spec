<?php declare(strict_types=1);
require __DIR__ . '/../frontend/autoload.php';
require __DIR__ . '/../frontend/FileLexer.php';
function check(bool $condition, string $message): void {
    if (!$condition) throw new RuntimeException($message);
}
function parsed(string $source): bool {
    try { return withPhpSourceFile($source, 'php_spec_parse_file'); }
    catch (CompileError $error) { return false; }
}
foreach (['Shift_JIS' => 'SJIS', 'BIG5' => 'BIG-5', 'HZ-GB-2312' => 'HZ',
          'x-uuencode' => 'UUENCODE', "uTf-8\0ignored" => 'UTF-8'] as $name => $expected) {
    check(php_spec_encoding_name($name) === $expected, 'Native encoding lookup lost a MIME/case/NUL spelling');
}
foreach (['', 'pass', 'none', 'raw', ' UTF-8', 'UTF-8 ', "\0UTF-8"] as $name) {
    check(php_spec_encoding_name($name) === null, 'Unknown encoding name was accepted');
}
$ordinary = [
    '<?php echo 1 + 2;',
    "\xef\xbb\xbf<?php echo 1;",
    "<?php // comment\n\$value = 'bytes'; ?>\nhtml",
    "<?php __halt_compiler();\xff\0payload",
    "<?php echo <<<TXT\ntext \$value\nTXT;\n",
];
foreach ($ordinary as $source) {
    $native = withPhpSourceFile($source, 'php_spec_lex_file');
    $expected = array_map(static fn(PhpToken $t): array => [$t->id, $t->text, $t->line, $t->pos], PhpToken::tokenize($source));
    check($native['tokens'] === $expected, 'Raw file tokens differ from raw tokenizer on ordinary PHP');
    check(parsed($source), 'Valid ordinary source rejected');
    check($native['initial_source'] === $source, 'Initial raw buffer unexpectedly changed');
    if (str_starts_with($source, "\xef\xbb\xbf") && ini_get('zend.multibyte')) {
        check($native['original_source'] === substr($source, 3),
            'Native no-filter BOM distinction lost');
    }
}
check(!parsed('<?php $x=;'), 'Invalid source accepted');
check(parsed('<?php echo 1;'), 'Parser state did not recover after rejection');
check(parsed('<?php class RepeatedMethod { function f() {} function f() {} }'),
    'Native oracle incorrectly performed compilation checks');
$sentinel = tempnam(sys_get_temp_dir(), 'not-executed-');
unlink($sentinel);
check(parsed('<?php file_put_contents(' . var_export($sentinel, true) . ', "executed");'), 'Side-effect source parse failed');
check(!file_exists($sentinel), 'Source was executed');
$shebang = "#!/usr/bin/php\n<?php declare(strict_types=1); echo 1;";
$native = withPhpSourceFile($shebang, 'php_spec_lex_file');
check($native['preamble'] === "#!/usr/bin/php\n" && $native['tokens'][0][2] === 2,
    'Shebang or following token location lost');
check(parsed($shebang), 'Shebang before strict_types rejected');
if (ini_get('zend.multibyte')) {
    foreach (['UTF-16LE' => "\xff\xfe", 'UTF-16BE' => "\xfe\xff"] as $encoding => $bom) {
        $good = $bom . mb_convert_encoding('<?php $x=1;', $encoding, 'UTF-8');
        $bad = $bom . mb_convert_encoding('<?php $x=;', $encoding, 'UTF-8');
        check(parsed($good) && !parsed($bad), 'File BOM grammar not recognized');
        $lexer = new FileLexer();
        $parser = new PhpParser\Parser\Php8($lexer);
        $ast = $parser->parse($good);
        check($ast[0] instanceof PhpParser\Node\Stmt\Expression, 'BOM file treated as inline HTML');
        check($lexer->info['source_encoding'] === $encoding, 'BOM encoding metadata lost');
    }
    $sjis = '<?php declare(encoding="SJIS"); echo "' . mb_convert_encoding('あ', 'SJIS', 'UTF-8') . '";';
    $tokens = PhpToken::tokenize($sjis);
    $closing = array_find_key($tokens, static fn(PhpToken $token): bool => $token->text === ')');
    $events = [['token' => $closing, 'encoding' => 'SJIS']];
    $native = withPhpSourceFile($sjis, static fn(string $path): array => php_spec_lex_file($path, $events));
    check($native['final_encoding'] === 'SJIS' && $native['source'] === '<?php declare(encoding="SJIS"); echo "あ";',
        'Independent declaration encoding event did not rescan source');
    check($native['events'][0]['token'] === $closing && $native['events'][0]['offset'] === strpos($sjis, ')') + 1,
        'Declaration rescan event offset changed');
    // Bytes already lexed before a declaration retain their original meaning.
    $prefixed = str_replace('<?php ', "<?php /*\xff*/ ", $sjis);
    $closing += 2;
    $native = withPhpSourceFile($prefixed, static fn(string $path): array =>
        php_spec_lex_file($path, [['token' => $closing, 'encoding' => 'SJIS']]));
    check(str_contains($native['source'], "/*\xff*/") && !str_contains($native['filtered_source'], "/*\xff*/"),
        'Declaration incorrectly transformed previously emitted comment bytes');

}
echo "Native file scanner/oracle: grammar, raw tokens, BOM, shebang, isolation and no execution passed\n";
