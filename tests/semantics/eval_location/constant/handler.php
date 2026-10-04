<?php
function filenameHandler($level,$message,$file,$line) {
    echo '[',$file,':',$line,']|';
    echo eval('return __FILE__;'),'|';
    try {eval('throw new Exception("inside");');}catch(Exception $e){echo $e->getFile(),':',$e->getLine(),'|';}
    try {eval('?');}catch(ParseError $e){echo $e->getFile(),':',$e->getLine(),'|';}
    return 0;
}
