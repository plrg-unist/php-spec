<?php
class StartupRestoreOption {
    public function __toString() {
        set_include_path('callback-path');
        echo 'H:', get_include_path(), '|';
        return 'include_path';
    }
}
set_include_path('runtime-path');
ini_restore(new StartupRestoreOption);
echo 'R:', get_include_path(), '|';
echo include 'selected.php';
echo '|DONE';
