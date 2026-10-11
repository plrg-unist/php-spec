<?php
class PresenceTypedParent41 {
    public int $value { get => 1; }
}
class PresenceMissingChild41 extends PresenceTypedParent41 {
    public $value { get => 2; }
}
echo "UNREACHED|";
