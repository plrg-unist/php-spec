<?php
declare(encoding=1);
$x=<<<TXT
{$a[(function(){
 declare(encoding=2);
 return 0;
})()]}\u{}
TXT;
declare(encoding=3);
echo ;