<?php
namespace {
    #[Deprecated] const X = [];
}
namespace Ns202Implicit {
    function notice202() { echo 'H|'; return true; }
    class Base202 {
        public $label = 'A';
        function run($value = X) {
            echo static::class, '|', $this->label, '|', ($value === [] ? 'E|' : 'BAD|');
        }
        function __destruct() { echo 'D|'; }
    }
    class Child202 extends Base202 {
        function register202() {
            register_shutdown_function('Ns202Implicit\\Base202::run');
            register_shutdown_function([Base202::class, 'run']);
            echo 'F|';
        }
    }
    set_error_handler('Ns202Implicit\\notice202');
    $receiver = new Child202;
    $receiver->register202();
    $receiver = null;
    echo 'M|';
}
