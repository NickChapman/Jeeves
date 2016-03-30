import sys
directory = str(sys.argv[1])

<?
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title></title>
</head>
<body>
    <h1>403 - Forbidden</h1>
?>

print("<p>You do not have permission to view the directory listing for " + directory + "</p>")

<?
</body>
</html>
?>