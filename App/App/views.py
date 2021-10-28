from django.shortcuts import render
from django.http import HttpResponse
import time
from django.core.files import File
from django.shortcuts import redirect
from django.shortcuts import render
import mysql.connector
import requests
import pymysql
import random
import string
import requests
import hashlib
import json
import braintree
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

#Connection
def try_to_connect():
    cnx = pymysql.connect(user='root', password='secret',host='mysql-server',database='app1')
    return cnx

#Path Getter
def path_getter():
  return "http://localhost:8000"

#Home Page
def print_user(req):
    f = open("home.html", "r")
    out= f.read()
    f.close()
    return HttpResponse( out )

#Payment Gateway For Items and Keys
def payment_gateway(req):
    gateway = braintree.BraintreeGateway(
      braintree.Configuration(
          environment=braintree.Environment.Sandbox,
          merchant_id="x7h65pb7jq88w5qw",
          public_key="5pw64887tvj3qjym",
          private_key="500e0113aac551b7715d01cbc218c0f0",
      )
    )
    client_token=gateway.client_token.generate()
    f = open("new.html", "r")
    out= f.read()
    f.close()
    item = "";
    try:
        item=req.GET["item"]
    except:
        pass
    cnx = try_to_connect()
    sql= "SELECT `path`,`url` FROM `items` WHERE `itemname` LIKE %s;"
    temp = (item)
    cursor = cnx.cursor()
    cursor.execute(sql,temp)
    counter=0
    for row in cursor:
        counter=counter+1
        amount = row[0]
    if counter==0:
        return HttpResponse("noitem")
    out = out.replace('(!C???C!)',  client_token )
    out = out.replace('(!A???A!)',  amount )
    out = out.replace('(!I???I!)',  item )
    cnx = try_to_connect()
    return HttpResponse(out)

#Payment retun
def create_checkout(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
        environment=braintree.Environment.Sandbox,
        merchant_id="x7h65pb7jq88w5qw",
        public_key="5pw64887tvj3qjym",
        private_key="500e0113aac551b7715d01cbc218c0f0",
        )
    )
    result = gateway.transaction.sale({
        'amount': request.POST['amount'],
        'payment_method_nonce': request.POST['payment_method_nonce'],
        'options': {
        "submit_for_settlement": True
        }
    })
    if result.is_success or result.transaction:
        print("in here")
        TRANSACTION_SUCCESS_STATUSES = [
        braintree.Transaction.Status.Authorized,
        braintree.Transaction.Status.Authorizing,
        braintree.Transaction.Status.Settled,
        braintree.Transaction.Status.SettlementConfirmed,
        braintree.Transaction.Status.SettlementPending,
        braintree.Transaction.Status.Settling,
        braintree.Transaction.Status.SubmittedForSettlement
        ]
        print(request.POST['amount'])
        val = gateway.transaction.find(result.transaction.id)
        lastcheck = val.status in TRANSACTION_SUCCESS_STATUSES
        item = "";
        cnx = try_to_connect()
        sql = "SELECT `url` FROM `items` WHERE `itemname` LIKE %s AND `path` LIKE %s"
        temp = (request.POST['Item'],request.POST['amount'])
        cursor = cnx.cursor()
        cursor.execute(sql)
        counter=0
        myvalue=""
        for row in cursor:
            counter=counter+1
            url  = row[0]
            x = requests.get(url)
            myvalue = x.content.decode('utf-8')
        f = open("done.html", "r")
        out= f.read()
        f.close()
        if result.is_success:
            out = out.replace('(!I???I!)',  str(myvalue) )
            return HttpResponse( out )
        else:
          return HttpResponse("Failed to prossess")
    else:
      return HttpResponse("Failed to prossess")

#Gets Randome Sting of Chars to be Hashed
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str=""
    for x in range(length):
      result_str=result_str+random.choice(letters)
    return result_str

#not called by user
def usercheck_conect(uname,password,cnx):
  if uname=="NULL":
    return "False"
  Q1=("SELECT * FROM `users` WHERE `uname` LIKE %s AND `hashword` LIKE %s")
  tuple1 = (uname,password)
  cursor = cnx.cursor()
  cursor.execute(Q1,tuple1)
  counter=0
  for row in cursor:
    counter=counter+1
  if counter!=0:
    return "True"
  return "False"

#Adds user to database
def add_user(uname,password,email,cnx,return_var_type):
  newname=uname.replace("_","")
  if newname!=uname:
    return "No _"
  sql1 = "SELECT * FROM `users` WHERE `uname` LIKE %s";
  cursor = cnx.cursor()
  tuple1 = (uname)
  cursor.execute(sql1,tuple1)
  counter=0
  for row in cursor:
    counter=counter+1
  #adds fame money to there acount
  if counter==0:
    sql="INSERT INTO `users` (`hashword`, `uname`, `email`,`time`) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);";
    tuple1 = (password,uname,email)
    cursor = cnx.cursor()
    cursor.execute(sql,tuple1)
    cnx.commit()
    dictionary ={ 
      "response": "ADDED_USER"
    }
    query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (%s, %s, 'money1', '1000');")
    tuple1 = (uname,uname+"_money1")
    cursor = cnx.cursor()
    cursor.execute(query2,tuple1)
    cnx.commit()
    query3=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (%s, %s, 'money2', '1000');")
    tuple1 = (uname,uname+"_money2")
    cursor = cnx.cursor()
    cursor.execute(query3,tuple1)
    cnx.commit()
    return json.dumps(dictionary, indent = 4)
  dictionary ={ 
    "response": "USER_TAKEN"
  } 
  return json.dumps(dictionary, indent = 4)

#adds a post to the database and returens a post id by witch it can be foind
def add_post(uname,password,tital,text,body,photo,catagoy,catagoy_2,iframe,cnx,return_var_type):
  letsgo = usercheck_conect(uname,password,cnx)
  if letsgo!="True" and uname!="":
    dictionary ={ 
      "id": "NA "+uname+" "+password+" "+letsgo
    } 
    return json.dumps(dictionary, indent = 4)
  myrandom = get_random_string(128)
  post_id = hashlib.sha256(myrandom.encode()).hexdigest()
  sql="INSERT INTO `posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s);";
  tuple1 = (uname,text,body,tital,photo,iframe,catagoy,catagoy_2,post_id)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()

  dictionary ={ 
    "id": post_id
  } 
  return json.dumps(dictionary, indent = 4)

#Checks to see if a post is private
def check_priavate(key,private,cnx):
  if private=="":
    return "True"
  sql="SELECT * FROM `posts` WHERE `uname` LIKE 'addmin' AND `catagoy_2` LIKE %s AND `postkey` LIKE %s;"
  tuple1 = (private,key)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  counter=0
  for row in cursor:
    counter=counter+1
  if (counter==1):
    return "True"
  return "False"

#Given a post id it reterns a post
def getpost(key,usekkey,cnx,return_var_type):
  Q1=("SELECT `uname`,`text`,`body`,`tital`,`time`,`photo`,`iframe`,`catagoy`,`catagoy_2` FROM `posts` WHERE `postkey` LIKE %s;")
  tuple1= (key)
  cursor = cnx.cursor()
  cursor.execute(Q1,tuple1)
  counter=0
  out="NULL"
  private= ""
  for row in cursor:
    counter=counter+1
    out=row
    private=row[8]
  if(counter==0):
    dictionary ={ 
      "id": "post_is_NA",
      "username": str("NA"),
      "text": str("NA"),
      "body": str("NA"),
      "tital": str("NA"),
      "time" : str("NA"),
      "photo": str("NA"),
      "iframe": str("NA"),
      "catagoy": str("NA"),
      "catagoy_2": str("NA")

    } 
    return json.dumps(dictionary, indent = 4)
  if (check_priavate(usekkey,private,cnx)=="True"):
    dictionary ={ 
      "id": key,
      "username":   str(out[0])  ,
      "text":       str(out[1])  ,
      "body":       str(out[2])  ,
      "tital":      str(out[3])  ,
      "time" :      str(out[4])  ,
      "photo":      str(out[5])  ,
      "iframe":     str(out[6])  ,
      "catagoy":    str(out[7])  ,
      "catagoy_2":  str(out[8])  

    } 
    return json.dumps(dictionary, indent = 4)
  else:
    dictionary ={ 
      "id": "post_is_private+"+private,
      "username": str("NA"),
      "text": str("NA"),
      "body": str("NA"),
      "tital": str("NA"),
      "time" : str("NA"),
      "photo": str("NA"),
      "iframe": str("NA"),
      "catagoy": str("NA"),
      "catagoy_2": str("NA")

    } 
    return json.dumps(dictionary, indent = 4)

#adds a ledgure to the post
def add_ledgure(uname,password,email,hashword,Ledgure,cnx,return_var_type):
  letsgo = usercheck_conect(uname,password,cnx)
  if (letsgo=="False"):
    dictionary ={ 
      "output": "Wrong_User_Name",
    } 
    return json.dumps(dictionary, indent = 5)
  try:
    sql="INSERT INTO `Acounts` (`Ledgurename`, `Ledgurepassword`, `email`, `time`) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);";
    tuple1= (uname+"_"+Ledgure,hashword,email)
    cursor = cnx.cursor()
    cursor.execute(sql,tuple1)
    cnx.commit()
    dictionary ={ 
      "output": "added "+uname+"_"+Ledgure,
    } 
    return json.dumps(dictionary, indent = 5)
  except:
    dictionary ={ 
      "output": "taken",
    }
    return json.dumps(dictionary, indent = 5)
  return uname+"_"+Ledgure

#adds a Post key given creads and a ledgure
def add_key(ledgure,password,email,message,key_message,keyfroward,cnx,return_var_type):
  path = path_getter()+"/doit?"
  Q1=("SELECT `email` FROM `Acounts` WHERE `Ledgurename` LIKE %s and `Ledgurepassword` LIKE %s;")
  tuple1= (ledgure,password)
  cursor = cnx.cursor()
  cursor.execute(Q1,tuple1)
  counter=0
  for row in cursor:
    counter=counter+1
    email_to = row[0]
  #case no leddudurename_password
  if(counter==0):
    dictionary ={ 
      "post_id": "NA",
      "solution": "NA",
      "SQL":Q1
    }
    return json.dumps(dictionary, indent = 5)
  myrandom = get_random_string(128)
  post_id = hashlib.sha256(myrandom.encode()).hexdigest()
  randome2 = get_random_string(128)
  solution = hashlib.sha256(randome2.encode()).hexdigest()
  hashs = hashlib.sha256(solution.encode()).hexdigest()
  sql="INSERT INTO `c_key` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (%s, %s, %s, 'key', %s, CURRENT_TIMESTAMP,%s,%s);";
  tuple1= (post_id,ledgure,hashs,email,keyfroward,key_message)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  #removes key
  dictionary ={ 
    "post_id": post_id,
    "solution": solution,
    "email":email,
    "message":key_message,
    "ledgure_ownder_email":email_to,
    "land_url":path+"action_type=makepage&usertemplate_name=u1_mygameSEHTRJFCNLVXNRNSFVJXITPCKPKBPH&var1="+post_id+"?"+solution,
    "ledgure": ledgure,
    "path":path
  }
  #where add key funtion would go
  return json.dumps(dictionary, indent = 5)

#changes a post text fild OF post
def change_post(user,password,key,text,cnx,return_var_type):
  sql="SELECT `uname` FROM `posts` WHERE `postkey` LIKE %s;"
  tuple1= (key)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  counter=0
  for row in cursor:
    counter=counter+1
    uname=row[0]
  if counter==0:
    dictionary ={ 
      "output": "NO_Post_Found"+" "+sql,
    }
    return json.dumps(dictionary, indent = 5)
  letsgo = usercheck_conect(user,password,cnx)
  if user!=uname:
    return "user_named_not_matched"
  if user=="":
    letsgo="True"
  if letsgo=="False":
    dictionary ={ 
      "output": "NO_user_password",
    }
    return json.dumps(dictionary, indent = 5)
  sql ="UPDATE `posts` SET `text` = %s WHERE `posts`.`postkey` = %s; "
  tuple1= (text,key)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  dictionary ={ 
    "output": "text_updated",
  }
  return json.dumps(dictionary, indent = 5)

#update a key by solving an old one and makeing a new one and returns a keyname 
def change_key(key,name,newkey,cnx ,return_var_type):
  sql = "SELECT `hash`,`ledgername`,`forward`,`key_message` FROM `c_key` WHERE `entery_name` LIKE %s AND `solution` LIKE 'key';"
  tuple1 = (name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  counter=0
  for row in cursor:
    counter=counter+1
    hashs=row[0]
    Lname=row[1]
    forward=row[1]
    key_message=row[2]
  if counter==0:
    dictionary ={ 
      "output": "NO_name_or_key_taken",
    }
    return json.dumps(dictionary, indent = 5)

  if hashlib.sha256(key.encode()).hexdigest()!=hashs:
    dictionary ={ 
      "output": "NO_match"+key+" "+hashlib.sha256(key.encode()).hexdigest()+" "+hashs
    }
    return json.dumps(dictionary, indent = 5)
  #change key case
  sql ="UPDATE `c_key` SET `solution` = %s WHERE `entery_name` = %s; "
  tuple1 = (key,name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()

  myrandom = get_random_string(128)
  post_id = hashlib.sha256(myrandom.encode()).hexdigest()
  sql="INSERT INTO `c_key` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (%s, %s, %s, 'key', 'none', CURRENT_TIMESTAMP, %s, %s);";
  tuple1 = (post_id,Lname,newkey,forward,key_message)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  dictionary ={ 
    "output": post_id,
  }
  return json.dumps(dictionary, indent = 5)

#returns key inforamtiopn
def check_key(name,cnx,return_var_type):
  sql = "SELECT `hash`,`ledgername`,`solution` FROM `c_key` WHERE `entery_name` LIKE %s;"
  tuple1 = (name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  counter=0
  for row in cursor:
    counter    =counter+1
    hashs      =row[0]
    ledgername =row[1]
    sol        =row[2]
  if counter==0:
    dictionary ={ 
      "output": "NA",
      "hash":"NA",
      "ledgure":"NA",
      "solution":"NA"
    }
    return json.dumps(dictionary, indent = 5)
  dictionary ={ 
    "output": name,
    "hash":hashs,
    "ledgure":ledgername,
    "solution":sol
  }
  return json.dumps(dictionary, indent = 5)

#removes a key and resonrs the infomation about it. can also froward infromation
def rm_key(name,key,message,cnx,return_var_type):
  sql = "SELECT `hash`,`ledgername`,`forward`,`key_message`,`email` FROM `c_key` WHERE `entery_name` LIKE %s AND `solution` LIKE 'key';"
  tuple1 = (name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  counter=0
  for row in cursor:
    counter=counter+1
    hashs=row[0]
    Lname=row[1]
    forward=row[1]
    key_message=row[2]
    email=row[3]
  #a =sdfadsf
  if counter==0:
    dictionary ={ 
      "key_message": "NA",
      "email":"NA",
      "forward":"NA",
      "key_message":"NA",
      "post_id":"NO_Key"
    }
    return json.dumps(dictionary, indent = 5)
  if hashlib.sha256(key.encode()).hexdigest()!=hashs:
    dictionary ={ 
      "key_message": "NA",
      "email":"NA",
      "forward":"NA",
      "key_message":"NA",
      "post_id":"NO_match"
    }
    return json.dumps(dictionary, indent = 5)
  #removing key and sending back_info_to_user
  sql ="UPDATE `c_key` SET `solution` = %s WHERE `entery_name` = %s; "
  tuple1 = (key,name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  myrandom = get_random_string(128)
  post_id = hashlib.sha256(myrandom.encode()).hexdigest()
  sql="INSERT INTO `posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES ('addmin', '', '', '', CURRENT_TIMESTAMP, '', '', '', %s, %s);";
  tuple1 = (Lname,post_id)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  dictionary ={ 
    "key_message": str(key_message),
    "email":str(hashs),
    "forward":str(forward),
    "key_message":str(key_message),
    "post_id":str(post_id),
    "ledgure":str(Lname),
    "mesage_to_send":str(message)
  }
  #where send logic is handeled

  return json.dumps(dictionary, indent = 5)

#adds a template with post see posturl.html for an example as this uses post makes a html template to be used by user
def add_template(username,password,template_name,template,replace,cnx,return_var_type):
  letsgo = usercheck_conect(username,password,cnx)
  if replace=="":
    replace = "!"
  if letsgo=="False":
    dictionary ={ 
      "output": "NO_user_password"
    }
    return json.dumps(dictionary, indent = 4)
  #repalceing template wiht strings

  template = template.replace('\"',  '(!A???'+replace+'???A!)' )
  template = template.replace('\'',  '(!B???'+replace+'???B!)' )
  template = template.replace('`',   '(!C???'+replace+'???C!)' )
  template = template.replace('\\',  '(!D???'+replace+'???D!)' )
  try:
    sql=  "INSERT INTO `template` (`user`, `usertemplate_name`, `template`, `time`) VALUES (%s, %s, %s, CURRENT_TIMESTAMP); "
    tuple1 = (username,username+"_"+template_name,template)
    cursor = cnx.cursor()
    cursor.execute(sql,tuple1)
    cnx.commit()
    dictionary ={ 
      "output": "added_tempalte "+username+"_"+template_name 
    }
    return json.dumps(dictionary, indent = 4)
  except:
    #case name taken
    dictionary ={ 
      "output": "dup_name"
    }
    return json.dumps(dictionary, indent = 4)

#Sends back a tempalte returning a page after replaceing variables makes a setion post with a given id not called by user
def make_setion(myid,cnx,make):
  sql="INSERT INTO `posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES ('', '', '', '', CURRENT_TIMESTAMP, '', '', %s, '', %s);";
  tuple1 = (make,myid)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()

#returns a template 
def return_template(usertemplate_name,var1,setion,setion2,rep,cnx):
  path=path_getter()+"/doit"
  url=path+"?action_type=makepage2&usertemplate_name="+usertemplate_name+"&var1="+var1+"&rep="+rep+"&setion="+setion+"&setion2="+setion2
  return "<script type=\"text/javascript\"> function blank(A,B){  val = JSON.parse(A); newval = val[\"id\"].replaceAll(\"\\\"\", \"&quot;\"); console.log(\"on here\"); console.log(newval); document.getElementById(\"main\").innerHTML = \"<iframe style=\\\"width: 100%;height:100%;\\\" sandbox=\\\"allow-scripts\\\" srcdoc=\\\"\"+newval+\"\\\"></iframe>\"; } function post_responce(path,func,varible){ fetch(path).then( ( response) => { return response.text();   }).then((html) => { func(  html.trim()  , varible ) }); } post_responce(\""+url+"\",blank,\"val\"); </script> <div id = \"main\"> <div>"

#returns a template 
def return_template2(usertemplate_name,var1,setion,setion2,rep,cnx):
  path=path_getter()+"/doit"
  sql = "SELECT `template` FROM `template` WHERE `usertemplate_name` LIKE %s"
  tuple1 = (usertemplate_name)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  cnx.commit()
  counter=0
  for row in cursor:
    counter=counter+1
    template=row[0]
  if (counter==0):
    #case no template
    return "NO_template"+" "+sql
  else:
    pass
  if (rep==""):
    rep="!"
  template = template.replace('(!A???'+rep+'???A!)',  '\"' )
  template = template.replace('(!B???'+rep+'???B!)',  '\'' )
  template = template.replace('(!C???'+rep+'???C!)',   '`' )
  template = template.replace('(!D???'+rep+'???D!)',  '\\' )
  template = template.replace('(!Q???'+rep+'???Q!)',  'script' )
  template = template.replace('(!0???'+rep+'???0!)',  var1     )
  template = template.replace('(!W???'+rep+'???W!)',  '&'      )
  template = template.replace('(!L???'+rep+'???L!)',  '+')
  template = template.replace('(!S???'+rep+'???S!)',  setion   )
  template = template.replace('(!Z???'+rep+'???Z!)',  setion2  )
  template = template.replace('(!P???'+rep+'???P!)',  path  )
  template = template.replace('(!T???'+rep+'???T!)',  usertemplate_name  )

  dictionary ={ 
    "id": str(template)
  }
  return json.dumps(dictionary, indent = 4)

#makes and redirects urls
def redirect_req(var,types,cnx):
  if types=="":
    sql="SELECT `url` FROM `redirect` WHERE `id` LIKE %s "
    tuple1 = (var)
    cursor = cnx.cursor()
    cursor.execute(sql,tuple1)
    cnx.commit()
    counter=0
    for row in cursor:
      counter=counter+1
      url=row[0]
    if counter==0:
      dictionary ={ 
        "id": "NOURL"
      } 
      return HttpResponse(json.dumps(dictionary, indent = 4))
    return redirect(url)
  else:
    myrandom = get_random_string(128)
    post_id = hashlib.sha256(myrandom.encode()).hexdigest()
    post_id = post_id[:15]
    sql="INSERT INTO `redirect` (`id`, `url`, `time`) VALUES (%s, %s, CURRENT_TIMESTAMP ); "
    tuple1 = (post_id,var)
    cursor = cnx.cursor()
    cursor.execute(sql,tuple1)
    cnx.commit()
    dictionary ={ 
      "id": post_id
    } 
  return HttpResponse(json.dumps(dictionary, indent = 4))

#finishes traid via traid id
def funtion_make_traid(username, password ,traid_money_type,traid_money_amount,request_money_type,request_amount ,cnx):
  try:
    float(request_amount)
    float(traid_money_amount)
  except:
    dictionary ={ 
      "response": "Invaild",
      "amnountleft":"NA"
    } 
    return json.dumps(dictionary, indent = 4)

  if username=="NULL":
    dictionary ={ 
      "response": "Wrong_Username",
      "amnountleft":"NA"
    } 
    return json.dumps(dictionary, indent = 4)
  is_user=usercheck_conect(username,password,cnx)
  if is_user=="False":
    dictionary ={ 
      "response": "Wrong_Username",
      "amnountleft":"NA"
    } 
    return json.dumps(dictionary, indent = 4)
  traidid=get_random_string(64)
  checkandadd_money_type(username,traid_money_type,cnx)
  Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
  tuple1 = (username+"_"+traid_money_type)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  for row in cursor:
    money=row[0]
  amnountleft=money-traid_money_amount
  if amnountleft>0:
    pass
  else:
    #case no funds in user acount
    dictionary ={ 
      "response": "No_Funds",
      "amnountleft":"NA"
    } 
    return json.dumps(dictionary, indent = 4)
  #event where there are user funds in acount
  U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
  tuple1 = (str(amnountleft),username+"_"+traid_money_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()
  Q1=("INSERT INTO `traidtable` (`traid_id`, `traid_mony_type`, `traid_request_type`, `traid_request_amount`, `traid_money_amount`, `user`, `buyer`) VALUES (%s, %s, %s, %s, %s, %s, 'NULL');")
  tuple1 = (traidid,traid_money_type,request_money_type,str(request_amount),str(traid_money_amount),username)
  cursor = cnx.cursor()
  cursor.execute(Q1,tuple1)
  cnx.commit()
  counter=0


  dictionary ={ 
    "response": traidid,
    "amnountleft":str(amnountleft)
  } 
  return json.dumps(dictionary, indent = 4)

#compleate traid with traid id
def compleat_traid_comand(user,password,traid_id,cnx):
  if user=="NULL":
    dictionary ={ 
      "response": "NO_USER",
    }
    return json.dumps(dictionary, indent = 4)
  is_user=usercheck_conect(user,password,cnx)
  if is_user=="False":
    dictionary ={ 
      "response": "NO_USER",
    }
    return json.dumps(dictionary, indent = 4)
  sql=("SELECT `traid_mony_type`,`traid_request_type`,`traid_request_amount`,`traid_money_amount`,`buyer`,`user` FROM `traidtable` WHERE `traid_id` LIKE %s AND `buyer` LIKE 'NULL';")
  cursor = cnx.cursor()
  tuple1 = (traid_id)
  cursor = cnx.cursor()
  cursor.execute(sql,tuple1)
  counter=0
  for row in cursor:
    counter=1
    traid_mony_type=row[0]
    traid_request_type=row[1]
    traid_request_amount=row[2]
    traid_money_amount=row[3]
    buyer=row[4]
    reciver=row[5]
  #substack form payied user
  if counter==0:
    dictionary ={ 
      "response": "No_Traid",
    }
    return json.dumps(dictionary, indent = 4)
  #verifies theres enough money user acount
  checkandadd_money_type(user,traid_request_type,cnx)
  Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
  cursor = cnx.cursor()
  tuple1 = (user+"_"+traid_request_type)
  cursor.execute(Q0,tuple1)
  for row in cursor:
    money=row[0]
  amnountleft=money-traid_request_amount
  if amnountleft>0:
    pass
  else:
    dictionary ={ 
      "response": "No_Funds",
    }
    return json.dumps(dictionary, indent = 4)
  checkandadd_money_type(user,traid_request_type,cnx)
  U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
  tuple1 = (str(amnountleft),user+"_"+traid_request_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()

  #put money gained form train to taker of traid
  checkandadd_money_type(reciver,traid_request_type,cnx)
  Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
  tuple1 = (reciver+"_"+traid_request_type)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  for row in cursor:
    money=row[0]
  amnountleft=money+traid_request_amount
  U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
  tuple1 = (str(amnountleft),reciver+"_"+traid_request_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)

  #add to user acount who made traid
  checkandadd_money_type(user,traid_mony_type,cnx)
  Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
  tuple1 = (user+"_"+traid_mony_type)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  for row in cursor:
    money=row[0]
  amnountleft=money+traid_money_amount

  #add money to user acount
  checkandadd_money_type(reciver,traid_mony_type,cnx)
  U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
  tuple1 = (str(amnountleft),user+"_"+traid_mony_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()
  #update buyer
  Q0=("UPDATE `traidtable` SET `buyer` = %s WHERE `traidtable`.`traid_id` = %s;")
  tuple1 = (user,traid_id)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  cnx.commit()
  #print(traid_mony_type,traid_request_type,traid_request_amount,traid_money_amount,buyer,reciver)
  dictionary ={ 
    "response": traid_id,
  }
  return json.dumps(dictionary, indent = 4)
  return traid_id;

#add barter curancy to acount
def get_key2(path,ledgure_name,keyname,password):
  #get barter key
  myurl = path+"?action_type=check_key&name="+keyname
  x = requests.get(myurl)
  getarray = json.loads(x.content.decode('utf-8'))
  if getarray["hash"]!="NA":
    print("passed_leddgure")
  else:
    return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  if getarray["ledgure"]==ledgure_name:
    print("passed_leddgure")
  else:
    return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  passwordCandidate = password
  val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
  if val==getarray["hash"]:
    print("passed_key")
  else:
    return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  random_string=""

  #generate and sores new crypto
  for _ in range(100):
      random_integer = random.randint(65, 80)
      random_string += (chr(random_integer))
  passwordCandidate = random_string
  newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()
  keyhash = hashlib.sha256(newkey.encode()).hexdigest()
  newname = ""
  #"http://localhost:8000/doit?name=8cb659e7c6a3741f06c05a470c5d1be19fc06e0e92428683cace4d466dab93fa&action_type=change_key&key=f23fe76e075c152c58b7446f963282c6f719ead3c87207d919f7a1a5b139959b&newkey=new_key"
  x = requests.get(path+"?name="+keyname+"&key="+password+"&newkey="+keyhash+"&action_type=change_key")
  # { "output": "1d02bd8d2550f41376ef49188516c870119dca49e9d8a5ff9649f6211eb2bfb7" }
  myval = json.loads( x.content.decode('utf-8').strip() )

  if len(myval["output"])<=40:
    return [False,"NO_key", "",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  dictionary ={ 
      "key": str(newkey),
      "name": str(newkey),
      "entery_name":str(ledgure_name),
      "path":str(path)
  }
  stingout = json.dumps(dictionary, indent = 4)
  return [True,stingout,path+ledgure_name]

#add crypto to user acount
def add_crypto(uname,password,path,key,name,lname,cnx):
  if (usercheck_conect(uname,password,cnx)==False):
    return "No_user"
  is_user=usercheck_conect(uname,password,cnx)
  if is_user=="False" or uname=="NULL":
    dictionary ={ 
      "response": "NO_user",
    }
    return json.dumps(dictionary, indent = 4) 
  val = [False,path+"check_key.php?name="+key,path+"check_key.php?name="+key,""]
  try:
    val = get_key2(path,lname,name,key)
  except:
    pass
  #val = get_key(path,lname,name,key)
  if (val[0]==True):
    random_string=""
    for _ in range(100):
        random_integer = random.randint(65, 80)
        random_string += (chr(random_integer))
    passwordCandidate = random_string
    ADD="INSERT INTO `crypto3` (`id_section`, `item_name`, `url`, `added`, `cached`, `used`) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'NOT');"
    tuple1 = (random_string,val[2],val[1])
    cursor = cnx.cursor()
    cursor.execute(ADD,tuple1)
    cnx.commit()
    Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE %s ")
    tuple1 = (uname+"_"+val[2])
    cursor = cnx.cursor()
    cursor.execute(Q0,tuple1)
    for row in cursor:
      number_of_users=row[0]
    if (number_of_users==0):
      query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (%s, %s, %s, '1');")
      cursor = cnx.cursor()
      tuple1 = (uname,uname+"_"+val[2],val[2] )
      cursor.execute(query2,tuple1)
      cnx.commit()
      dictionary ={ 
        "response": "1",
      }
      return json.dumps(dictionary, indent = 4)
    else:
      Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
      tuple1 = (uname+"_"+val[2] )
      cursor = cnx.cursor()
      cursor.execute(Q0,tuple1)
      for row in cursor:
        money=row[0]
      amnountleft=money+1
      U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
      tuple1 = (str(amnountleft),uname+"_"+val[2] )
      cursor = cnx.cursor()
      cursor.execute(U1,tuple1)
      cnx.commit()
      dictionary ={ 
        "response": str(amnountleft),
      }
      return json.dumps(dictionary, indent = 4) 
  else:
    dictionary ={ 
      "response": "NO_key",
    }
    return json.dumps(dictionary, indent = 4)

#adds money type to user acount if its not there and makes it zero 
def checkandadd_money_type(user,money,cnx):
  #adds a money collum if there is no money avaible
  Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE %s ")
  tuple1 = (user+"_"+money)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  for row in cursor:
    number_of_users=row[0]
  if (number_of_users==0):
    query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (%s, %s, %s, '0');")
    tuple1 = (user,user+"_"+money,money)
    cursor = cnx.cursor()
    cursor.execute(query2,tuple1)
    cnx.commit()
  return

#returns barter curnacy to user 
def get_key_back(uname,password,money_type,cnx):
  if (usercheck_conect(uname,password,cnx)==False):
    return "No_user"
  checkandadd_money_type(uname,money_type,cnx)
  Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE %s")
  tuple1 = (uname+"_"+money_type)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  for row in cursor:
    money=row[0]
  amnountleft = money-1
  if amnountleft>=0:
    pass
  else:
    dictionary ={ 
      "response": "no_funds for " + uname+"_"+money_type,
    }
    return json.dumps(dictionary, indent = 4)
  U1=("UPDATE `money` SET `amount_of_money` = %s WHERE `money`.`user_money` = %s;")
  tuple1 = (str(amnountleft),uname+"_"+money_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()
  U1=("SELECT `id_section`,`url` FROM `crypto3` WHERE `item_name` LIKE %s and  `used` LIKE 'NOT';")
  tuple1 = (money_type)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()
  for row in cursor:
    stingid=row[0]
    url=row[1]
  U1=("UPDATE `crypto3` SET `used` = 'used' WHERE `id_section` = %s;")
  tuple1 = (stingid)
  cursor = cnx.cursor()
  cursor.execute(U1,tuple1)
  cnx.commit()
  dictionary ={ 
    "response": str(url),
  }
  return json.dumps(dictionary, indent = 4)

#get info about traid
def get_traid(traid_id,cnx):
  Q0="SELECT `traid_id`,`traid_mony_type`,`traid_request_type`,`traid_mony_type`,`traid_request_amount`,`traid_money_amount`,`user`,`buyer` FROM `traidtable` WHERE `traid_id` LIKE %s; "
  counter=0
  tuple1 = (traid_id)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  cnx.commit()
  for row in cursor:
    counter=1
    traid_id=row[0]
    traid_mony_type=row[1]
    traid_request_type=row[2]
    traid_request_amount=row[3]
    traid_money_amount=row[4]
    traid_request_amount=row[5]
    user=row[6]
    buyer =row[7]
  if counter==1:
    dictionary ={ 
      "traid_id": traid_id,
      "traid_mony_type": traid_mony_type,
      "traid_request_type":traid_request_type,
      "traid_request_amount":traid_request_amount,
      "traid_money_amount":traid_money_amount,
      "traid_request_amount":traid_request_amount,
      "user":user,
      "buyer":buyer
    }
    return json.dumps(dictionary, indent = 4)
  dictionary ={ 
    "traid_id": "NO_traid_id",
    "traid_mony_type": "NA",
    "traid_request_type":"NA",
    "traid_request_amount":"NA",
    "traid_money_amount":"NA",
    "traid_request_amount":"NA",
    "user":"NA",
    "buyer":"NA"
  }
  return json.dumps(dictionary, indent = 4)

#prints infro about user
def user_acount(user,cnx):
  if user=="NULL":
    return "False_NO_NULL_user"
  Q0=("SELECT `user_money`,`amount_of_money` FROM `money` WHERE `user` LIKE %s")
  tuple1 = (user)
  cursor = cnx.cursor()
  cursor.execute(Q0,tuple1)
  cnx.commit()
  outsting=[]
  for row in cursor:
    outsting=outsting+[ [row[0],str(row[1])] ]
  cnx.commit()
  dictionary ={ 
    "out": outsting,
  }
  return json.dumps(dictionary, indent = 4)

#setup up api returens and  calls other functions
def sriper(word):
  word=word.replace("\"" ,"(???1???)")
  word=word.replace("'"  ,"(???2???)")
  word=word.replace("`"  ,"(???3???)")
  word=word.replace("\\" ,"(???4???)")
  return word

def unstrip(word):
  word=word.replace("(???1???)","\"")
  word=word.replace("(???2???)","'" )
  word=word.replace("(???3???)","`" )
  word=word.replace("(???4???)","\\")
  return word

def doit(req):
    #Geting input vars
    action_type=""
    try:
        action_type=sriper(req.GET["action_type"])
    except:
        action_type=""
    user=""
    try:
        user=sriper(req.GET["user"])
    except:
        user=""
    email=""
    try:
        email=sriper(req.GET["email"])
    except:
        email=""
    phone=""
    try:
        phone=sriper(req.GET["phone"])
    except:
        phone=""
    password=""
    try:
        password=sriper(req.GET["password"])
    except:
        pass
    crypto_name=""
    try:
        crypto_name=sriper(req.GET["crypto_name"])
    except:
        pass
    crypto_key=""
    try:
        crypto_key=sriper(req.GET["crypto_key"])
    except:
        pass
    crypto_path=""
    try:
        crypto_path=sriper(req.GET["crypto_path"])
    except:
        pass
    L_name=""
    try:
        L_name=sriper(req.GET["L_name"])
    except:
        pass
    request_type=""
    try:
        request_type=sriper(req.GET["request_type"])
    except:
        pass
    tital=""
    try:
        tital=sriper(req.GET["tital"])
    except:
        pass

    text=""
    try:
        text=sriper(req.GET["text"])
    except:
        pass

    body=""
    try:
        body=sriper(req.GET["body"])
    except:
        pass
    photo=""
    try:
        photo=sriper(req.GET["photo"])
    except:
        pass
    catagoy=""
    try:
        catagoy=sriper(req.GET["catagoy"])
    except:
        pass
    catagoy_2=""
    try:
        catagoy_2=sriper(req.GET["catagoy_2"])
    except:
        pass
    iframe=""
    try:
        iframe=sriper(req.GET["iframe"])
    except:
        pass
    key=""
    try:
        key=sriper(req.GET["key"])
    except:
        pass
    seach1=""
    try:
        seach1=sriper(req.GET["seach1"])
    except:
        pass
    seach2=""
    try:
        seach2=sriper(req.GET["seach2"])
    except:
        pass
    message=""
    try:
        message=sriper(req.GET["message"])
    except:
        pass
    hashword=""
    try:
        hashword=sriper(req.GET["hashword"])
    except:
        pass
    Ledgure=""
    try:
        Ledgure=sriper(req.GET["Ledgure"])
    except:
        pass
    ledgure=""
    try:
        ledgure=sriper(req.GET["ledgure"])
    except:
        pass
    name=""
    try:
        name=sriper(req.GET["name"])
    except:
        pass
    newkey=""
    try:
        newkey=sriper(req.GET["newkey"])
    except:
        pass
    seach_type=""
    try:
        seach_type=sriper(req.GET["seach_type"])
    except:
        pass
    use_key=""
    try:
        use_key=sriper(req.GET["use_key"])
    except:
        pass
    try:
        use_key=sriper(req.GET["usekkey"])

    except:
        pass
    key_message=""
    try:
        key_message=sriper(req.GET["keyfroward"])
    except:
        pass
    keyfroward=""
    try:
        keyfroward=sriper(req.GET["keyfroward"])
    except:
        pass
    return_var_type=""
    try:
        return_var_type=sriper(req.GET["return_var_type"])
    except:
      pass
    setion=""
    try:
        setion=sriper(req.GET["setion"])
    except:
        pass
    setion2=""
    try:
        setion2=sriper(req.GET["setion2"])
    except:
        pass
    var1=""
    try:
        var1=sriper(req.GET["var1"])
    except:
      pass
    usertemplate_name=""
    try:
        usertemplate_name=sriper(req.GET["usertemplate_name"])
    except:
        pass
    rep=""
    try:
        rep=sriper(req.GET["rep"])
    except:
        pass
    url=""
    try:
        url=sriper(req.GET["url"])
    except:
        pass
    L_name=""
    try:
        L_name=sriper(req.GET["L_name"])
    except:
        pass
    request_type=""
    try:
        request_type=sriper(req.GET["request_type"])
    except:
        pass
    send_type=""
    try:
        send_type=sriper(req.GET["send_type"])
    except:
        pass
    send_amount=""

    try:
        send_amount=float(req.GET["send_amount"])
    except:
        pass

    crypto_path=""
    try:
        crypto_path=sriper(req.GET["crypto_path"])
    except:
        pass
    traid_id=""
    try:
        traid_id=sriper(req.GET["traid_id"])
    except:
        pass
    request_amound=""
    try:
        request_amound=float(req.GET["request_amound"])
    except:
        pass
    crypto_name=""
    try:
        crypto_name=sriper(req.GET["crypto_name"])
    except:
        pass
    crypto_key=""
    try:
        crypto_key=sriper(req.GET["crypto_key"])
    except:
      pass
    if action_type=="adduser":
        out=add_user(user,password,email,try_to_connect(),return_var_type)
        return HttpResponse( out )
    #Getting values
    if action_type=="add_post":
      return  HttpResponse(add_post(user,password,tital,text,body,photo,catagoy,catagoy_2,iframe, try_to_connect(),return_var_type ) )
    if action_type=="get_post":
      return  HttpResponse( getpost(key,use_key,try_to_connect(),return_var_type ) )
    if action_type=="add_ledgure":
      return HttpResponse( add_ledgure(user,password,email,hashword,Ledgure,try_to_connect() ,return_var_type ) )
    if action_type=="add_key":
      return HttpResponse(  add_key(ledgure,password,email,message,key_message,keyfroward, try_to_connect() ,return_var_type ) )
    if action_type=="change_post":
      return HttpResponse( change_post(user,password,key,text,try_to_connect() ,return_var_type ) )
    if action_type =="change_key":
      return HttpResponse( change_key(key,name,newkey,try_to_connect(),return_var_type ) )
    if action_type =="check_key":
      return HttpResponse( check_key(name,try_to_connect(),return_var_type ) )
    if action_type =="rm_key":
      return HttpResponse( rm_key(name,key,L_name,try_to_connect(),return_var_type ) )
    if action_type=="fintraid":
        return HttpResponse( compleat_traid_comand(user,password,traid_id,try_to_connect()) )
    if action_type=="Uprint":
      return HttpResponse(  user_acount(user,try_to_connect()) )
    if action_type=="traid":
      return HttpResponse( get_traid(traid_id,try_to_connect()) )
    if action_type=="add_C":
        return HttpResponse(add_crypto(user,password,crypto_path,crypto_key,crypto_name,L_name,try_to_connect()) )
    if action_type=="get_C":
        return HttpResponse(get_key_back(user,password,crypto_path+L_name,try_to_connect()))
    if action_type=="maketraid":
        return HttpResponse( funtion_make_traid(user,password,send_type,send_amount,request_type,request_amound,try_to_connect())  )
    a=""
    try:
        a=sriper(req.GET["a"])
    except:
        pass
    if a =="re":
      return redirect_req(url,rep,try_to_connect())
    #templates
    types=""
    user=""
    password=""
    template=""
    types=""
    replace=""
    try:
        user=sriper(req.POST["user"])
        password=sriper(req.POST["password"])
        temmplate_name=sriper(req.POST["temmplate_name"])
        template=req.POST["template"]#striped elsewere
        types=sriper(req.POST["type"])
        replace=sriper(req.POST["replace"])
    except:
        pass

    if types!="":
        return HttpResponse(add_template(user,password,temmplate_name,template,replace,try_to_connect(),return_var_type ))

    if action_type=="makepage":
        if setion==""  or setion2=="":
            if setion=="":
                    randome2 = get_random_string(128)
                    setion = hashlib.sha256(randome2.encode()).hexdigest()
                    make_setion(setion, try_to_connect(),usertemplate_name )
            if setion2=="":
                    randome2 = get_random_string(128)
                    setion2 = hashlib.sha256(randome2.encode()).hexdigest()
                    make_setion(setion2, try_to_connect(),usertemplate_name )

            response = redirect(path_getter()+'/doit?action_type=makepage&usertemplate_name='+usertemplate_name+'&var1='+var1+'&rep='+rep+'&setion='+setion+'&setion2='+setion2)
            return response
        else:
            return HttpResponse(return_template(usertemplate_name,var1,setion,setion2,rep,try_to_connect() ) )

    if action_type=="makepage2":
        if setion==""  or setion2=="":
            if setion=="":
                    randome2 = get_random_string(128)
                    setion = hashlib.sha256(randome2.encode()).hexdigest()
                    try:
                      make_setion(setion, try_to_connect(),usertemplate_name )
                    except:
                      pass
            if setion2=="":
                    randome2 = get_random_string(128)
                    setion2 = hashlib.sha256(randome2.encode()).hexdigest()
                    try:
                        make_setion(setion2, try_to_connect(),usertemplate_name )
                    except:
                      pass

            response = redirect(path_getter()+'/doit?action_type=makepage&usertemplate_name='+usertemplate_name+'&var1='+var1+'&rep='+rep+'&setion='+setion+'&setion2='+setion2)
            return response
        else:
            return HttpResponse(return_template2(usertemplate_name,var1,setion,setion2,rep,try_to_connect() ) )
    return HttpResponse( "api_fail" )

def get_key(path,ledgure_name,keyname,password):
  #get barter key
  x = requests.get(path+"check_key.php?name="+keyname)

  getarray = str(x.content)

  out = getarray.split(" ")
  if len(out)==9:
  #cehcks barter key
    print("passed_leddgure")
  else:
    return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]

  if ledgure_name==out[1]:
    print("passed_leddgure")
  else:
    return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  #
  passwordCandidate = password
  val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
  if val==out[3]:
    print("passed_key")
  else:
    return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  random_string=""
  #generate and sores new crypto
  for _ in range(100):
      random_integer = random.randint(65, 80)
      random_string += (chr(random_integer))
  passwordCandidate = random_string
  newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()
  keyhash = hashlib.sha256(newkey.encode()).hexdigest()
  newname = ""
  x = requests.get(path+"change_key.php?name="+keyname+"&key="+password+"&Nkey="+keyhash)
  myval = x.content.decode('utf-8').strip()

  if myval=="false":
    return [False,"NO_key", "",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
  stingout = path+"output2.php?key="+newkey+"&name="+myval+"&entery_name="+ledgure_name 
  #print(stingout)
  return [True,stingout,path+ledgure_name]





