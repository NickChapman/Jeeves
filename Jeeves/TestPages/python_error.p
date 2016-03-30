import sys
error_message = str(sys.argv[1])
error_reporting_enabled = bool(int(sys.argv[2]))

<?
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title></title>
</head>
<body>
    <h1>500 - Internal Server Error</h1>
?>

if error_reporting_enabled:
    print("<p>The error message is:</p>")
    print("<pre>" + error_message + "</pre>")

<?
</body>
</html>
?>