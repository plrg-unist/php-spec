<?php declare(strict_types=1);
// A JSON-line worker. It never evaluates submitted PHP programs.
require __DIR__ . '/autoload.php';
require __DIR__ . '/FileLexer.php';
require __DIR__ . '/encoding-literal.php';
require __DIR__ . '/encoding.php';
require __DIR__ . '/wire.php';
require __DIR__ . '/target.php';
require __DIR__ . '/SourcePrinter.php';
ini_set('display_errors', 'stderr');
ini_set('log_errors', '0');
ini_set('memory_limit', '-1');
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8) throw new RuntimeException('PHP 8.5.10, 64-bit required');
if (!function_exists('php_spec_parse_file')) throw new RuntimeException('Load the local .tools/php-file.so syntax helper');
$schema = json_decode(file_get_contents(__DIR__ . '/../spec/schema.json'), true, 512, JSON_THROW_ON_ERROR);
$version = PhpParser\PhpVersion::fromComponents(8, 5);
$parser = (new PhpParser\ParserFactory())->createForVersion($version);
$printer = new SourcePrinter(['phpVersion' => $version, 'newline' => "\n", 'indent' => '    ']);

function bytes(string $encoded): string {
    $value = base64_decode($encoded, true);
    if ($value === false || base64_encode($value) !== $encoded) throw new RuntimeException('Noncanonical base64');
    return $value;
}
function encode($value) {
    global $schema;
    if ($value instanceof PhpParser\Node) {
        $tag = $value->getType();
        if (!isset($schema['nodes'][$tag])) throw new RuntimeException("Unsupported node $tag");
        $contract = $schema['nodes'][$tag];
        if ($value->getSubNodeNames() !== array_column($contract['fields'], 'name')) throw new RuntimeException("Field contract changed: $tag");
        $fields = [];
        foreach ($contract['fields'] as $field) $fields[] = encode($value->{$field['name']});
        $meta = [];
        foreach ($value->getAttributes() as $key => $item) {
            if (!isset($schema['metadata'][$key])) throw new RuntimeException("Unknown metadata $key");
            $meta[$key] = encode($item);
        }
        ksort($meta);
        return ['node' => $tag, 'fields' => $fields, 'meta' => (object)$meta];
    }
    if ($value instanceof PhpParser\Comment) {
        return ['comment' => [$value instanceof PhpParser\Comment\Doc, base64_encode($value->getText()),
            (string)$value->getStartLine(), (string)$value->getStartFilePos(), (string)$value->getStartTokenPos(),
            (string)$value->getEndLine(), (string)$value->getEndFilePos(), (string)$value->getEndTokenPos()]];
    }
    if (is_string($value)) return ['bytes' => base64_encode($value)];
    if (is_int($value)) return ['int' => (string)$value];
    if (is_float($value)) return ['float' => bin2hex(pack('E', $value))];
    if (is_array($value)) return array_map('encode', $value);
    if (is_bool($value) || $value === null) return $value;
    throw new RuntimeException('Unsupported transport value');
}
function decode($value) {
    global $schema;
    if (is_bool($value) || $value === null) return $value;
    if (is_array($value)) return array_map('decode', $value);
    if (!$value instanceof stdClass) throw new RuntimeException('Expected tagged value');
    $keys = array_keys(get_object_vars($value));
    if ($keys === ['bytes']) return bytes($value->bytes);
    if ($keys === ['int']) {
        if (!is_string($value->int) || !preg_match('/^(0|-?[1-9][0-9]*)$/D', $value->int) || (string)(int)$value->int !== $value->int) throw new RuntimeException('Invalid integer');
        return (int)$value->int;
    }
    if ($keys === ['float']) {
        if (!is_string($value->float) || !preg_match('/^[0-9a-f]{16}$/D', $value->float)) throw new RuntimeException('Invalid float bits');
        return unpack('E', hex2bin($value->float))[1];
    }
    if ($keys === ['comment']) {
        $args = $value->comment;
        if (count($args) !== 8 || !is_bool($args[0])) throw new RuntimeException('Malformed comment');
        $class = array_shift($args) ? PhpParser\Comment\Doc::class : PhpParser\Comment::class;
        $args[0] = bytes($args[0]);
        for ($i = 1; $i < count($args); ++$i) $args[$i] = decode((object)['int' => $args[$i]]);
        return new $class(...$args);
    }
    if ($keys !== ['node', 'fields', 'meta'] || !isset($schema['nodes'][$value->node])) throw new RuntimeException('Unknown node/fields');
    $contract = $schema['nodes'][$value->node];
    if (count($value->fields) !== count($contract['fields']) || !$value->meta instanceof stdClass) throw new RuntimeException('Wrong node arity/metadata');
    // Construct a fresh instance using only the validated fields. Constructors normalize or
    // supply defaults, so bypass them and assign every declared field explicitly.
    $node = (new ReflectionClass($contract['class']))->newInstanceWithoutConstructor();
    foreach ($contract['fields'] as $i => $field) $node->{$field['name']} = decode($value->fields[$i]);
    $attributes = [];
    foreach ($value->meta as $key => $item) {
        if (!isset($schema['metadata'][$key])) throw new RuntimeException("Unknown metadata $key");
        $attributes[$key] = decode($item);
    }
    $node->setAttributes($attributes);
    return $node;
}
$diagnostics = [];
set_error_handler(static function (int $severity, string $message) use (&$diagnostics): bool {
    if (error_reporting() & $severity) $diagnostics[] = ['severity' => $severity, 'message' => base64_encode($message)];
    return true;
});
while (($line = fgets(STDIN)) !== false) {
    $diagnostics = [];
    try {
        $request = wireDecode(json_decode($line, false, 131072, JSON_THROW_ON_ERROR));
        switch ($request->op) {
            case 'version':
                $result = ['php' => PHP_VERSION, 'parser' => '5.8.0', 'short_open_tag' => (bool)ini_get('short_open_tag')];
                break;
            case 'oracle':
            case 'oracle-string':
                try {
                    if ($request->op === 'oracle-string') token_get_all(bytes($request->source), TOKEN_PARSE);
                    else {
                        if (!withPhpSourceFile(bytes($request->source), 'php_spec_parse_file')) {
                            throw new RuntimeException('File parser returned false without an exception');
                        }
                    }
                    $result = ['accepted' => true];
                }
                catch (CompileError $error) { $result = ['accepted' => false, 'category' => $error instanceof ParseError ? 'parser_rejection' : 'parser_static_rejection', 'message' => base64_encode($error->getMessage())]; }
                break;
            case 'parse':
                try { $ast = parseWithEncoding($parser, bytes($request->source)); checkTargetSyntax($ast, $parser->getTokens()); }
                catch (PhpParser\Error $error) { $result = ['accepted' => false, 'category' => 'parser_rejection', 'message' => base64_encode($error->getMessage())]; break; }
                $transport = ['version' => 1, 'program' => encode($ast)];
                $encoding = sourceEncoding(bytes($request->source), $parser->getTokens(), $ast);
                if ($encoding !== null) $transport['encoding'] = $encoding;
                $comments = [];
                foreach ($parser->getTokens() as $index => $token) {
                    if ($token->id === T_COMMENT || $token->id === T_DOC_COMMENT) {
                        $comments[] = ['doc' => $token->id === T_DOC_COMMENT, 'text' => base64_encode($token->text), 'token' => $index];
                    }
                }
                $result = ['accepted' => true, 'ast' => $transport, 'token_comments' => $comments];
                break;
            case 'print':
                if ($request->ast->version !== 1) throw new RuntimeException('Transport version mismatch');
                $fresh = decode($request->ast->program);
                $transport = ['version' => 1, 'program' => encode($fresh)];
                if (isset($request->ast->encoding)) $transport['encoding'] = $request->ast->encoding;
                $printer->sourceEncoding = $request->ast->encoding ?? null;
                $result = ['source' => base64_encode(printEncoding($printer->printChunks($fresh), $printer->sourceEncoding)), 'ast' => $transport];
                break;
            default: throw new RuntimeException('Unknown operation');
        }
        echo json_encode(wireEncode(['ok' => true, 'diagnostics' => $diagnostics] + $result), JSON_THROW_ON_ERROR | JSON_INVALID_UTF8_SUBSTITUTE, 131072), "\n";
    } catch (Throwable $error) {
        echo json_encode(['ok' => false, 'category' => 'frontend_error', 'message' => base64_encode(get_class($error) . ': ' . $error->getMessage())], JSON_THROW_ON_ERROR), "\n";
    }
}
