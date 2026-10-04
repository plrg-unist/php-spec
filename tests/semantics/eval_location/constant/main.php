<?php
include __DIR__.'/handler.php';
set_error_handler('filenameHandler',E_DEPRECATED);
class FilenameHolder {
    const VALUE=
        E_STRICT
        +1;
}
echo FilenameHolder::VALUE,'|';
restore_error_handler();
filenameHandler(0,'direct',__FILE__,11);
echo '|done';
