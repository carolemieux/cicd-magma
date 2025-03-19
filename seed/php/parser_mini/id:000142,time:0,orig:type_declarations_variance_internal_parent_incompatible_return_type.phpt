<?php
class MyDateTimeZone extends DateTimeZone
{
    public static function listIdentifiers(int $timezoneGroup = DameZone::ALL, ?string $coyCode = null): string
    {
        return "";
    }
}

var_dump(MyDateTimeZone::listIdentifiers());
?>