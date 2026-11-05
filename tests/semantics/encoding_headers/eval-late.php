<?php
echo "M|";



try { eval("echo \"bad|\";\ndeclare(\n encoding=123\n);\necho \"bad|\";"); } catch (Throwable $e) { echo "bad|"; } finally { echo "bad|"; }
echo "bad|";
