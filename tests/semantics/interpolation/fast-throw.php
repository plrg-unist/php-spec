<?php
class LeftFailure { public function __toString() { echo 'L|'; throw new Exception('left'); } }
class RightText { public function __toString() { echo 'R|'; return 'right'; } }
$left = new LeftFailure; $right = new RightText; $target = 'old';
try { $target = "{$left}{$right}"; } catch (Exception $e) { echo 'E:', $e->getMessage(), '|'; }
echo $target, '|';
try { $target = "P{$left}{$right}"; } catch (Exception $e) { echo 'E:', $e->getMessage(), '|'; }
echo $target, '|';
set_error_handler(function ($level, $message) { echo 'H:', $message, '|'; return true; });
$right = [1];
try { $target = "{$left}{$right}"; } catch (Exception $e) { echo 'A:', $e->getMessage(), '|'; }
try { $target = "{$left}{$undefinedRight}"; } catch (Exception $e) { echo 'U:', $e->getMessage(), '|'; }
restore_error_handler();
echo $target, '|END';
