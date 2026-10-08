<?php
class ThisHost323 {
    private $value = 'before';
    public function castValue() { $this->value = 'cast'; }
    public function readyValue() { $this->value = 'ready'; }
    public function getValue() { return $this->value; }
    public function __toString(): string { echo 'HOST|'; return $this->value; }
    public function run() {
        $value = 'before';
        try {
            $value = include new ThisOperand323($this);
            echo 'AFTER-BODY|';
        } catch (Throwable $error) { echo 'caught|'; }
        echo 'H:', $this->value, '|V:', $value, '|END';
    }
}
class ThisOperand323 {
    public $host;
    public function __construct($host) { $this->host = $host; }
    public function __toString(): string { echo 'cast|'; $this->host->castValue(); return __DIR__ . '/this-property-nonthrow-child.php'; }
    public function __destruct() {
        source_this_ready_323($this->host);
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $this->host->getValue(), '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/this-property-nonthrow-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/this-property-nonthrow-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
$host = new ThisHost323;
$host->run();
