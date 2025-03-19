<?php

interface A {}
interface B {}
interface C {}

class Test implements A, B, C {}

class Foo {
    public function foo(): A&B&C {
    return new Test();
    }
}

/*because just A&B larger than A&B&C */
class FooChild extends Foo {
    public function foo(): A&B {
        return new Test();
    }
}

?>