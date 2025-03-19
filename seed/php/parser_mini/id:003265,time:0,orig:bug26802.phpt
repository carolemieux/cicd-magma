<?php

function global_func()
{
    echo __METHOD__ . "\n";
}

$function = 'global_func';
$function();

class foo
{
    static $method = 'global_func';

    static public function foo_func()
    {
        echo __METHOD__ . "\n";
    }
}

/* with PHP 4 where it would
 * call foo::fail. In PHP 5 we first evaluate static class
 * properties and then do the function call.
 */
$method = 'foo_func';
foo::$method();


?>