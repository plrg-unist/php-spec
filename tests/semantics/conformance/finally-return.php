<?php
function f(){try{echo "T";return 1;}finally{echo "F";return 2;}} echo f();
