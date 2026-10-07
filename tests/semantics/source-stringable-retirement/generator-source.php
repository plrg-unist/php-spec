<?php
class CombinedSource16 {
    public function __toString(): string {
        echo "cast\n";
        $GLOBALS['combined_operand_16'] = null;
        return __DIR__ . '/generator-source-child.php';
    }
    public function __destruct() {
        combined_child_ready_16();
        echo "destroy\n";
        throw new Exception("deferred");
    }
}
function combined_inner_16() {
    global $combined_operand_16;
    set_error_handler(function ($level, $message) { echo "warning\n"; return true; });
    eval($undefined_source_16);
    restore_error_handler();
    $value = 'before';
    try {
        $value = include ($combined_operand_16 ?? null);
        echo "body-entered\n";
    } catch (Exception $exception) {
        $trace = $exception->getTrace();
        echo "caught:", $value, ":", $trace[0]['line'], ":", $trace[1]['line'], "\n";
        echo "file:", ($trace[0]['file'] === __DIR__ . '/generator-source-child.php' ? 'child' : 'main'), "\n";
        echo "keyword:", $trace[1]['function'], ":", (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/generator-source-child.php' ? 'filename' : 'none'), "\n";
    }
    yield $value;
}
function combined_outer_16() { yield from combined_inner_16(); }
$combined_operand_16 = new CombinedSource16;
$generator = combined_outer_16();
echo "value:", $generator->current(), "\n";
$generator->next();
echo "end\n";
