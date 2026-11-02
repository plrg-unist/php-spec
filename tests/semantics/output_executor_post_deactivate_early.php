<?php
register_shutdown_function(static function () {
    echo "Q1|";
    echo ob_start() ? "T|" : "F|";
    echo ob_get_level(), "|";
    echo "Q2|";
    ob_end_flush();
});
echo "M|";
