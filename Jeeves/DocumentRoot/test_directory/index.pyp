"""
As you can see on this page, we can store our HTML in
another file and then write pages in almost entirely python.
"""
# With the following command you can expose the server root to your pages
# Mind you, ServerRoot is not a python module. We preprocess to serve it to you.
import ServerRoot

with open(ServerRoot + "/test_directory/header.html", "r") as f:
	for line in f.readlines():
		print(line)

<?
<div style="width:1000px; height:700px; margin-left:auto; margin-right: auto; background-color:grey; padding: 10px;">
	?>
print("<p>We have generated some page content here</p>")
import datetime
print("<p>To prove this, here is today's date: " + str(datetime.date.today()) + "</p>")
	<?
</div>
?>

with open(ServerRoot + "/test_directory/footer.html", "r") as f:
	for line in f.readlines():
		print(line)