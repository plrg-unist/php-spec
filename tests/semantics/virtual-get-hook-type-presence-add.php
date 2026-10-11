<?php
class PresenceUntypedParent41 {
    public $value { get => 1; }
}
class PresenceAddedChild41 extends PresenceUntypedParent41 {
    public int $value { get => 2; }
}
echo "UNREACHED|";
