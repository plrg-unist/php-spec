<?php
namespace ClassStrings102;
class Base102 {}
class Child102 extends Base102 {}
use ClassStrings102\Base102 as Alias102;
function forbiddenLoader102(string $name): void { echo "BAD|"; throw new \Exception("autoload"); }
\spl_autoload_register('ClassStrings102\forbiddenLoader102');
$subject = new Child102;
$name = '\cLaSsStRiNgS102\bAsE102';
echo "S:";
echo $subject instanceof $name ? "T|" : "F|";
$name = 'Alias102';
echo $subject instanceof $name ? "T|" : "F|";
$name = 'Missing102';
echo $subject instanceof $name ? "T|" : "F|";
$name = 'ClassStrings102\Child102';
echo $subject instanceof $name ? "T|" : "F|";
$subject = null;
echo "E|";
