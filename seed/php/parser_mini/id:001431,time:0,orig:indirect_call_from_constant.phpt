<?php

class Test
{
public static function method()
{
        echo "Method cd!\n";
    }
}

['Test', 'me']();

'Test::method'();

(['Test', 'method'])();

('Test::method')();

?>