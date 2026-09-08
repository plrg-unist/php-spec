<?php declare(strict_types=1);
// This tooling file always starts with the default source encoding. Apply a
// source-only script_encoding profile after compilation, around native parsing.
$profile = json_decode($argv[2], true, 512, JSON_THROW_ON_ERROR);
if (isset($profile['zend.script_encoding'])) ini_set('zend.script_encoding', $profile['zend.script_encoding']);
fwrite(STDERR, "SOURCE_BEGIN\n");
try {
    echo php_spec_parse_file($argv[1]) ? 'accept' : 'reject';
} catch (Throwable $error) {
    echo 'reject';
}
fwrite(STDERR, "SOURCE_END\n");
