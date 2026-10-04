<?php
class MovingOperand {
    public function __toString(): string {
        echo "PATH:", ini_set("include_path", __DIR__ . "/late"), "|";
        echo "CD:", chdir(__DIR__ . "/cwd"), "|";
        return "target.php";
    }
}
echo "V:", require new MovingOperand(), "|", ini_get("include_path"), "|END";
