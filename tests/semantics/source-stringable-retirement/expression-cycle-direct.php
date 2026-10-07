<?php
class DirectCycle301 {
    public $self;
    public function __construct() { $this->self = $this; }
    public function __destruct() { echo "CYCLE|"; }
}
class DirectSource314 {
    public function __toString(): string {
        $GLOBALS['mixed_operand_314'] = null;
        echo "CAST\n";
        return __DIR__ . '/generator-expression-child.php';
    }
    public function __destruct() {
        compiled_ready_314();
        echo 'GC:', gc_collect_cycles(), ':', $GLOBALS['mixed_weak_301']->get() === null ? "gone\n" : "live\n";
        throw new Exception('retired');
    }
}
$mixed_object_314 = new stdClass();
$mixed_object_314->value = 'before';
$GLOBALS['mixed_object_314'] = $mixed_object_314;
$cycle = new DirectCycle301();
$GLOBALS['mixed_weak_301'] = WeakReference::create($cycle);
unset($cycle);
$GLOBALS['mixed_operand_314'] = new DirectSource314();
try { include ($GLOBALS['mixed_operand_314'] ?? null); }
catch (Exception $error) {
    $trace = $error->getTrace();
    echo 'D:', $trace[0]['line'], ':', $trace[0]['file'] === __DIR__ . '/generator-expression-child.php' ? 'child' : 'other', "\n";
    echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', $trace[1]['file'] === __FILE__ ? 'main' : 'other', ':', $trace[1]['args'][0] === __DIR__ . '/generator-expression-child.php' ? 'filename' : 'other', "\n";
    echo 'O:', $mixed_object_314->value, "\n";
}
echo "END\n";
