<?php

// Thnerate a binding for $GLOBALS
$a = 123;
$fn = fn() => $GLOBALS['a'];
var_dump($fn());

?>