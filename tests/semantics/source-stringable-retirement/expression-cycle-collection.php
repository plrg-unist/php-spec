<?php
class MixedCycle301 {
    public $self;
    public function __construct() { $this->self = $this; }
    public function __destruct() { echo "CYCLE|"; }
}
class MixedSource314 {
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
function mixed_inner_314() {
    $mixed_object_314 = new stdClass();
    $mixed_object_314->value = 'before';
    $GLOBALS['mixed_object_314'] = $mixed_object_314;
    $value = 'before';
    try { $value = include ($GLOBALS['mixed_operand_314'] ?? null); }
    catch (Exception $error) {
        $trace = $error->getTrace();
        echo 'D:', $trace[0]['line'], ':', $trace[0]['file'] === __DIR__ . '/generator-expression-child.php' ? 'child' : 'other', "\n";
        foreach ($trace as $frame) {
            if ($frame['function'] === 'include') {
                echo 'K:include:', $frame['line'], ':', $frame['file'] === __FILE__ ? 'main' : 'other', ':', $frame['args'][0] === __DIR__ . '/generator-expression-child.php' ? 'filename' : 'other', "\n";
            }
        }
        echo 'O:', $mixed_object_314->value, "\n";
    }
    echo 'V:', $value, "\n";
    yield 'done';
}
function mixed_outer_314() { yield from mixed_inner_314(); }
$cycle = new MixedCycle301();
$GLOBALS['mixed_weak_301'] = WeakReference::create($cycle);
unset($cycle);
$GLOBALS['mixed_operand_314'] = new MixedSource314();
foreach (mixed_outer_314() as $value) { echo 'Y:', $value, "\n"; }
echo "END\n";
