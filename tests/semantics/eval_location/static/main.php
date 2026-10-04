<?php
include __DIR__.'/owner.php';
class StaticEvalChild extends StaticEvalOwner {}
StaticEvalHandler::run();
restore_error_handler();
StaticEvalHandler::again();
echo '|done';
