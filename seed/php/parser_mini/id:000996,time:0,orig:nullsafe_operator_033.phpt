<?php

class Foo {
    public $bar = 'bar';

    function qux() {
        return 'qux';
    }
}

$null = null;
$foo = new Foo();

var_dump("{$null?->foo}");
var_dump("{$null?->bar()}");
var_dump("$null?->foo");
var_dump("$null?->bar()");

var_dump("{$foo?->bar}");
var_dump("{$foo?->baz}");
var_dump("{$foo?->qux()}");
try {
    var_dump("{$foo?->quux()}");
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

var_dump("$foo?->bar");
var_dump("$foo?->baz");
var_dump("$foo?->qux()");
try {
    var_dump("$foo?->quux()");
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

?>