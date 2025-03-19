<?php

enum Foo: string {
    case Bar = <<<BAR
    Bar
    bar
    bar
    BAR;

    case Baz = <<<'BAZ'
    Baz
    baz
    baz
    BAZ;
}

echo Foo::Bar->value . "\n";
echo Foo::Baz->value . "\n";

?>