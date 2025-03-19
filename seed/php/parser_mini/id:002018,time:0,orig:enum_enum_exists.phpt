<?php

enum Foo {
    case Bar;
}

class Baz {}

spl_autoload_register(function ($className) {
    echo "Triggered autoloader with class $className\n";

    if ($className === 'Quux') {
        enum Quux {}
    }
});

var_dump(enum_exists(Foo::class));
var_dump(enum_exists(Foo::Bar::class));
var_dump(enum_exists(Baz::class));
var_dump(enum_exists(Qux::class));
var_dump(enum_exists(Quux::class, false));
var_dump(enum_exists(Quux::class, true));
var_dump(enum_exists(Quuz::class, false));
var_dump(enum_exists(Quuz::class, true));

?>