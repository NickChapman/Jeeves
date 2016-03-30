import datetime
import RequestHeaders
todays_date_string = str(datetime.date.today())
<?
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title>Jeeves - Just HTML</title>
</head>
<body>
    <h1>This page just contains HTML</h1>
    <p>?>print("Today's date is " + todays_date_string, end="")<?</p>
	<p>?>print("Your user agent string is " + str(RequestHeaders["User-Agent"]), end="")<?</p>
	<p>?>print("The date above was generated server side. As was this text.", end="")<?</p>
	?>
print("<ul>")
	for i in range(1, 101):
	print("<li>Generated bullet point #" + str(i) + "</li>")
	
	<?</ul>
    <p>For a complete list of test pages please see the DocumentRoot project</p>
    <img src="/test_image.jpg" />
</body>
</html>
?>