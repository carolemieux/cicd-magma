<?php

echo 'Bit:' . \PHP_EOL;
// 7 Warnn total
$var = '1.5'|3;
var_dump($var);
$var = '1.5'&3;
var_dump($var);
$var = '1.5'^3;
var_dump($var);
$var = '1.5' << 3;
var_dump($var);
$var = '1.5' >> 3;
var_dump($var);
$var = 3 << '1.5';
var_dump($var);
$var = 3 >> '1.5';
var_dump($var);

echo 'Modulo:' . \PHP_EOL;
// 2 warnings in total
$var = '6.5' % 2;
var_dump($var);
$var = 9 % '2.5';
var_dump($var);

echo 'Fu:' . \PHP_EOL;
function foo(int $a) {
    return $a;
}
var_dump(foo('1.5'));

var_dump(chr('60.5'));

echo 'Function returns:' . \PHP_EOL;
function bar(): int {
    return '3.5';
}
var_dump(bar());

echo 'Typrty assignment:' . \PHP_EOL;
class Test {
    public int $a;
}

$instance = new Test();
$instance->a = '1.5';
var_dump($instance->a);

?>