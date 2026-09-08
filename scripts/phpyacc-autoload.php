<?php
spl_autoload_register(static function (string $class): void {
    if (str_starts_with($class, 'PhpYacc\\')) {
        require __DIR__ . '/../vendor/php-yacc/lib/'
            . str_replace('\\', '/', substr($class, 8)) . '.php';
    }
});
require __DIR__ . '/../vendor/php-yacc/lib/functions.php';
