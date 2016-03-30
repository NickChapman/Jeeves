import RequestHeaders
import html
<?
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title></title>
</head>
<body>
?>
if len(RequestHeaders["GET"]) > 0:
    print("<p>You sent the GET variables:</p>")
    print("<ul>")
    for var in RequestHeaders["GET"]:
        print("<li>" + var + "=" + str(RequestHeaders["GET"][var]) + "</li>")
    print("</ul>")
if "message" in RequestHeaders["POST"]:
    print("<p>You said ", end="")
    print(html.unescape(RequestHeaders["POST"]["message"]), end="")
    print("</p>")
    <?
    <form action="" method="post">
        <input type="text" name="message" /><br />
        <input type="submit" />
    </form>
</body>
</html>
?>