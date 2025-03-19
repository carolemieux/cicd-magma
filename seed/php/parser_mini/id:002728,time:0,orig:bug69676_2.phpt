<?php

class Foo {
    const A = 'Fo';
    const B = self::A . ' and ' . self::C;
    const C = 'Foo::C';

}

class Bar extends Foo {
    const A = 'Bar::A';
    const C = 'Bar::C';
}

var_dump(Bar::B);

?>