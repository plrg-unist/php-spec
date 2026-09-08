<?php
// Evaluate only the trusted, pinned runner's container reader class, never its
// entrypoint or any PHPT FILE, SKIPIF, CLEAN, or REDIRECTTEST section.
class BorkageException extends Exception {}
$runner = file_get_contents(__DIR__ . '/../vendor/php-src/run-tests.php');
$start = strpos($runner, "class TestFile\n");
$end = strpos($runner, "\nfunction init_output_buffers", $start);
if ($start === false || $end === false) {
    throw new RuntimeException('Pinned TestFile boundary changed');
}
eval(substr($runner, $start, $end - $start));
while (($line = fgets(STDIN)) !== false) {
    $path = json_decode($line, true, flags: JSON_THROW_ON_ERROR);
    try {
        $test = new TestFile($path, false);
        $result = ['status' => $test->hasSection('REDIRECTTEST') ? 'redirect_container'
            : ($test->hasSection('FILE') ? 'source' : 'non_source')];
        if ($result['status'] === 'source') {
            $result['source_b64'] = base64_encode($test->getSection('FILE'));
        }
        $result['ini_b64'] = base64_encode($test->hasSection('INI') ? $test->getSection('INI') : '');
    } catch (BorkageException $error) {
        $result = ['status' => 'invalid_container', 'error' => $error->getMessage()];
    }
    echo json_encode($result, JSON_THROW_ON_ERROR), "\n";
}
