




import requests
import webbrowser
import random
import json
f = open("file_uploader.html", "r")
example=f.read()
f.close()

path = "http://localhost:8000/doit"


random_string =""
for x in range(30):
	random_integer = random.randint(66, 89)
	# Keep appending random characters using chr(x)
	random_string += (chr(random_integer))
value=random_string
myobj = {"user":"u1","password":"top","temmplate_name":"mygame"+value,"replace":"!","type":"!" ,'template': example}


x = requests.post(path, data = myobj)
val=x.content.decode('utf-8')

outputval=json.loads(val)


webbrowser.get("firefox").open(path+"?action_type=makepage&var1=W&rep=&usertemplate_name="+"u1_mygame"+value)








