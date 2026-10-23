import urllib.request

content = urllib.request.urlopen("http://127.0.0.1:8765/").read().decode("utf-8")
print("Served length:", len(content))
print("Has app-sidebar:", "aside class=\"app-sidebar" in content)
print("data-toggled in html:", "data-toggled=\"open\"" in content)
