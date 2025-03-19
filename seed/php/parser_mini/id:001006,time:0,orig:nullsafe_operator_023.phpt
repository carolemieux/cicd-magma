<?php

class Foo {
    public $bar;
}

$foo = new Foo();

foreach ($foo?->bar as &$value) {
    var_dump($value);
}

// Don't convert $foo->bar into a reference.
$foo->bar = [42];
foreach ($foo?->bar as &$value) {
    var_dump($value);
    $value++;
}
var_dump($foo->bar);

// But respect interior references.
$ref =& $foo->bar[0];
foreach ($foo?->bar as &$value) {
    var_dump($value);
    $value++;
}
var_dump($foo->bar);

?>