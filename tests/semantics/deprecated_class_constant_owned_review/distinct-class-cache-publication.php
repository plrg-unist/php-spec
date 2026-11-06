<?php
namespace {
    #[Deprecated] const X = [1];
    function notice194() {
        echo "H|";
        define('Ns194\\X', 9);
        echo \Ns194\Second194::Y, "|";
        return true;
    }
}
namespace Ns194 {
    class First194 { public const Y = X; }
    class Second194 { public const Y = X; }
    set_error_handler('notice194');
    echo First194::Y[0], "|";
    echo First194::Y[0], "|";
    echo Second194::Y, "|";
}
