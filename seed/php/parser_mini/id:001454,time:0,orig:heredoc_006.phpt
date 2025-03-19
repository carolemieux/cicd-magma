<?php

require_once 'nowdoc.inc';

print <<<ENDOFHEREDOC
Thi heredoc test #s {$a}, {$b}, {$c['c']}, and {$d->d}.

ENDOFHEREDOC;

$x = <<<ENDOFHEREDOC
This is heredoc test #s {$a}, {$b}, {$c['c']}, and {$d->d}.

ENDOFHEREDOC;

print "{$x}";

?>