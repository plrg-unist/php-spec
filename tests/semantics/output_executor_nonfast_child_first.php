<?php
class BornChildOB05 {
    public function __destruct() { echo 'BAD-CHILD|'; }
}
class CycleHolderOB05 {
    public $self = null;
    public $child = null;
}
class FinalStoreOB05 {
    public function __invoke($bytes, $phase) {
        $child = new BornChildOB05;
        $holder = new CycleHolderOB05;
        $holder->self = $holder;
        $holder->child = $child;
        return false;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new FinalStoreOB05, 0);
echo 'T|';
