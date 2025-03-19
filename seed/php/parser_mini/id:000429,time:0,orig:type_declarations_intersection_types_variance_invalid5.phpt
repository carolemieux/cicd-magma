<?php

interface X {}
interface Y {}

class Test {
    function method(): iterable {}
}
class Test2 extends Test {
    function method(): X&Y {}
}

?>