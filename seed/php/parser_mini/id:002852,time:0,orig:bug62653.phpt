<?php
$array = array("5"=>"bar");
$foo = "10.0000"; // gfoo) = "string"
$foo /= 2; //Makoo) = "double"
unset($array[$foo]);
print_r($array);

$array = array("5"=>"bar");
$foo = "5";
unset($array[(float)$foo]);
print_r($array);

$array = array("5"=>"bar");
$foo = "10.0000";
$foo /= 2; //Makes $fogettype($foo) = "double"
$name = "foo";
unset($array[$$name]);
print_r($array);

?>