<?php echo "M|"; $x = include __DIR__ . "/child-shebang.php"; echo "R", $x, "|"; $y = include __DIR__ . "/child-bom.php"; echo "B", $y, "|";
