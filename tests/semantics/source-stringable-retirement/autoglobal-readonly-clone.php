<?php
class ReadonlySourcePayload316 { public $value = 'initial'; }
class ReadonlySourceOperand316 {
    public readonly string $path;
    public $active = false;
    public function __construct() { $this->path = __DIR__ . '/unused.php'; }
    public function __clone() { $this->path = __DIR__ . '/autoglobal-readonly-clone-child.php'; $this->active = true; echo 'clone|'; }
    public function __toString(): string { echo 'cast|'; $_GET->value = 'cast'; return $this->path; }
    public function __destruct() {
        if (!$this->active) { return; }
        source_readonly_ready_316();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $_GET->value, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/autoglobal-readonly-clone-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/autoglobal-readonly-clone-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
$_GET = new ReadonlySourcePayload316;
$seed = new ReadonlySourceOperand316;
$value = 'before';
try {
    $value = include clone $seed;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'G:', $_GET->value, '|V:', $value, '|S:', ($seed->path === __DIR__ . '/unused.php' ? 'seed' : 'changed'), '|END';
