<?php declare(strict_types=1);
// Extract pinned public node contracts. Generated output is reviewed and committed.
require __DIR__ . '/../frontend/autoload.php';
$root = realpath(__DIR__ . '/..');
$files = glob($root . '/vendor/php-parser/lib/PhpParser/Node/*.php');
$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/vendor/php-parser/lib/PhpParser/Node'));
$classes = [];
foreach ($iterator as $file) {
    if (!$file->isFile() || $file->getExtension() !== 'php') continue;
    $source = file_get_contents($file->getPathname());
    if (!preg_match('/namespace ([^;]+);/', $source, $ns) || !preg_match('/^class (\w+)/m', $source, $name)) continue;
    $class = $ns[1] . '\\' . $name[1];
    $reflection = new ReflectionClass($class);
    if (!$reflection->isAbstract()) $classes[$class] = $reflection;
}
ksort($classes);
function resolveType(string $name, ReflectionClass $class): string {
    if (in_array($name, ['string', 'int', 'float', 'bool', 'null'], true)) return $name;
    if (str_contains($name, '::')) return 'int';
    preg_match_all('/^use ([^;]+);/m', file_get_contents($class->getFileName()), $uses);
    $parts = explode('\\', $name);
    foreach ($uses[1] as $use) {
        $full = explode(' as ', $use); $path = explode('\\', $full[0]);
        if ($parts[0] === ($full[1] ?? end($path))) {
            array_shift($parts);
            return $full[0] . ($parts ? '\\' . implode('\\', $parts) : '');
        }
    }
    return $class->getNamespaceName() . '\\' . $name;
}
function descriptor(string $text, ReflectionClass $class): array {
    // Split unions only outside list/parenthesis delimiters.
    $parts = []; $level = 0; $start = 0;
    for ($i = 0; $i < strlen($text); ++$i) {
        if ($text[$i] === '(' || $text[$i] === '<') ++$level;
        if ($text[$i] === ')' || $text[$i] === '>') --$level;
        if ($text[$i] === '|' && $level === 0) { $parts[] = substr($text, $start, $i - $start); $start = $i + 1; }
    }
    $parts[] = substr($text, $start);
    if (count($parts) > 1) return ['union' => array_map(fn($p) => descriptor($p, $class), $parts)];
    if (str_ends_with($text, '[]')) return ['list' => descriptor(substr($text, 0, -2), $class)];
    if (preg_match('/^(?:list|array)<(.+)>$/', $text, $m)) return ['list' => descriptor($m[1], $class)];
    if ($text[0] === '(' && str_ends_with($text, ')')) return descriptor(substr($text, 1, -1), $class);
    return ['atom' => resolveType($text, $class)];
}
$nodes = [];
foreach ($classes as $class => $reflection) {
    $node = $reflection->newInstanceWithoutConstructor();
    if ($node instanceof PhpParser\Node\Expr\Error) continue;
    $fields = [];
    foreach ($node->getSubNodeNames() as $field) {
        $property = $reflection->getProperty($field);
        if (preg_match('/@var ([^\s]+)/', $property->getDocComment() ?: '', $match)) {
            $type = descriptor($match[1], $property->getDeclaringClass());
        } else {
            $native = $property->getType();
            if (!$native instanceof ReflectionNamedType) throw new RuntimeException("Missing contract: $class.$field");
            $type = ['atom' => $native->getName()];
        }
        $fields[] = ['name' => $field, 'type' => $type];
    }
    $parents = [];
    for ($p = $reflection; $p; $p = $p->getParentClass()) $parents[] = $p->getName();
    $nodes[$node->getType()] = ['class' => $class, 'parents' => $parents, 'source' => substr($reflection->getFileName(), strlen($root) + 1), 'fields' => $fields];
}
ksort($nodes);
echo json_encode(['version' => 1, 'nodes' => $nodes], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR), "\n";
