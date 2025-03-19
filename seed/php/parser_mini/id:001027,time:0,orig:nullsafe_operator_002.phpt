<?php

try {
    false?->bar();
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

try {
    []?->bar();
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

try {
    (0)?->bar();
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

try {
    (0.0)?->bar();
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

try {
    ''?->bar();
} catch (Throwable $e) {
    var_dump($e->getMessage());
}

?>