# Importing the python modules
from flask import *
import ibm_db
import requests
import os
import re
# import numpy as np
# import base64
# from flask import session

app=Flask(__name__)

# API keys 
RAPIDAPI_KEY='e629580d34msheba42c5fcea11aap149f50jsn94f770685ef0'  #mine 1 rj.group
RAPIDAPI_KEY1='714250c24fmsh829f65c05932f01p1ad65cjsn43a39e64b3bb' #mahidhar anna
RAPIDAPI_KEY2='d73283ca42msh25142662f0dd1eap11bde4jsnbe1a5c63f516' #siddhart
RAPIDAPI_KEY3='31dfff2899msh3849415864bc766p188f0djsn3347d5121717' #mine 2 1998

#db connection 
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=fnc49721;PWD=oI8YaxBwwrliegJ9",'','')
print(conn)
print("connection successful...")

app.secret_key='gajanan'
global user

#routing to home page
@app.route('/', methods=['POST','GET'])
def homepage():
    return render_template('index.html')

#routing to home page after login of user 
@app.route('/home', methods=['POST','GET'])
def after_login():
    return render_template('home.html')

#user login code
@app.route('/login', methods=['POST','GET'])
def login_page():
    msg = ''
    if request.method == "POST":
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        sql = "SELECT * FROM USER1 WHERE EMAIL=? AND PASSWORD=?"  
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, EMAIL)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['USERD'] = account['USERD']
            session['NAME'] = account['NAME']
            msg = "logged in successfully !"
            return redirect(url_for('after_login'))
        else:
            msg = "Incorrect Email/password"
            return render_template('login.html', msg=msg)
    return render_template('login.html', msg=msg)

#user registartion code    
@app.route('/register', methods=['POST','GET'])
def register_page():
    msg = ''
    if request.method == 'POST':
        NAME = request.form["name"]
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        sql = "SELECT* FROM USER1 WHERE EMAIL= ? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, EMAIL)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = "Your deatils are already exists in the database Please login"
            return render_template('login.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = "Invalid Email Address!"
        else:
            sql = "SELECT count(*) FROM USER1"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO USER1 VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, NAME)
            ibm_db.bind_param(prep_stmt, 2, EMAIL)
            ibm_db.bind_param(prep_stmt, 3, PASSWORD)
            ibm_db.bind_param(prep_stmt, 4, length['1']+1)
            ibm_db.execute(prep_stmt)
            msg = "Successfully registed!"
            return render_template('login.html', msg=msg)
    return render_template('register.html', msg=msg)

#remove background routing start
@app.route('/removebg', methods=['POST','GET'])
def removeback():
    global USERD
    url = "https://product-background-removal.p.rapidapi.com/cutout/commodity/commodity"

    # sql = "SELECT * FROM USER1 WHERE USERD=" +str(session['USERD'])
    sql = "SELECT * FROM USER1 WHERE USERD=" +str(session.get('USERD', -1))
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    # account = True
    if account:
            user='Loggedin'
            print('loggegin')
            if request.method == "POST":
                # user='Loggedin'
                print(user)
                file = request.files["filename"]
                print(file)
                image_option = request.form["return_form"]
                payload = {
                        'image': ('image',file),
                        'return_form':image_option
                    }
                headers = {
                    'X-RapidAPI-Key': RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "product-background-removal.p.rapidapi.com"
                }
                response = requests.post(url, headers=headers,files=payload)
                output=response.json()
                print(output)
                # print(type(output))    # should be a dictionary
                # print(dir(output))     # should show the keys of the dictionary
                image_output = output['data']['image_url']
                print(image_output)
                IMAGE_BG=image_output
                insert_sql = "INSERT INTO IMAGE_URL VALUES (?,?,NULL,NULL,NULL,NULL,NULL,NULL)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, account['USERD'])
                ibm_db.bind_param(prep_stmt, 2, IMAGE_BG)
                ibm_db.execute(prep_stmt)
                print('image_url sent to db2')
                # image_b64 = base64.b64encode(file.read()).decode('utf-8')
                # file.save(file.filename)
                return render_template('removebg.html',image_o=image_output,user=user)
            return render_template('removebg.html',user=user)    
    else:
            # user='none'
            if request.method == "POST":
                file = request.files["filename"]
                print(file)
                image_option = request.form.get("return_form")
                payload = {
                        'image': ('image',file),
                        'return_form': ('mask','whiteBK',image_option)
                    }
                headers = {
                    'X-RapidAPI-Key': RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "product-background-removal.p.rapidapi.com"
                }
                response = requests.post(url, headers=headers,files=payload)
                output=response.json()
                print(output)
                image_output = output['data']['image_url']
                print(image_output)
                # image_b64 = base64.b64encode(file.read()).decode('utf-8')
                # file.save(file.filename)
                return render_template('removebg.html',image_o=image_output)
    return render_template('removebg.html')
#remove background routing end 

#remove Vehicle background routing start
@app.route('/vehicleremove', methods=['POST','GET'])
def vehicle_bg():
    url = "https://vehicle-background-removal.p.rapidapi.com/cutout/universal/vehicle"
    sql = "SELECT * FROM USER1 WHERE USERD=" +str(session.get('USERD', -1))
    # sql = "SELECT * FROM USER1 WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    # account = True
    if account:
        user='Loggedin'
        print('loggegin')
        if request.method == "POST":
            user='Loggedin'
            file = request.files["filename"]
            print(file)
            # file1=file
            payload = {
                    'image': ('image',file)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY,
                "X-RapidAPI-Host": "vehicle-background-removal.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_input = output['data']['elements'][0]['origin_image_url']
            image_output = output['data']['elements'][0]['image_url']
            print(image_output)
            print(image_input)
            VEHICLE_BG=image_output

            insert_sql = "INSERT INTO IMAGE_URL VALUES (?,NULL,?,NULL,NULL,NULL,NULL,NULL)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, account['USERD'])
            ibm_db.bind_param(prep_stmt, 2, VEHICLE_BG)
            ibm_db.execute(prep_stmt)
            print('image_url sent to db2')
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file1.save(file1.filename)
            return render_template('vehicleremove.html',image_o=image_output,image_i=image_input,user=user)
        return render_template('vehicleremove.html',user=user)
    else:
        if request.method == "POST":
            user='Loggedin'
            file = request.files["filename"]
            print(file)
            # file1=file
            payload = {
                    'image': ('image',file)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY,
                "X-RapidAPI-Host": "vehicle-background-removal.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_input = output['data']['elements'][0]['origin_image_url']
            image_output = output['data']['elements'][0]['image_url']
            print(image_output)
            print(image_input)
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file1.save(file1.filename)
            return render_template('vehicleremove.html',image_o=image_output,image_i=image_input,user=user)
        
    return render_template('vehicleremove.html')
#remove Vehicle background routing end

#increase the beauty of images routing start
@app.route('/beauty_img', methods=['POST','GET'])
def beauty_image():
    url = "https://ai-skin-beauty.p.rapidapi.com/face/editing/retouch-skin"
    sql = "SELECT * FROM USER1 WHERE USERD=" +str(session.get('USERD', -1))
    # sql = "SELECT * FROM USER1 WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
    # if account['USERD']== session['USERD']:
        user='Loggedin'
        print('loggegin')
        if request.method == "POST":
            file = request.files["filename"]
            Retouch_degree=request.form['number']
            Whitening_degree=request.form['number1']
            print(file)
            # option = request.form.get("return_form")
            payload = {
                    'image': ('image',file),
                    'Retouch_degree': ('',Retouch_degree),
                    'Whitening_degree': ('',Whitening_degree)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY,
                "X-RapidAPI-Host": "ai-skin-beauty.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_output = output['data']['image_url']
            print(image_output)
            SKIN_BEAUTY	=image_output
            insert_sql = "INSERT INTO IMAGE_URL VALUES (?,NULL,NULL,NULL,?,NULL,NULL,NULL)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, account['USERD'])
            ibm_db.bind_param(prep_stmt, 2, SKIN_BEAUTY	)
            ibm_db.execute(prep_stmt)
            print('image_url sent to db2')
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file.save(file.filename) 
            return render_template('beauty_img.html',image_o=image_output,user=user) 
        return render_template('beauty_img.html',user=user)
    else:
         if request.method == "POST":
            file = request.files["filename"]
            Retouch_degree=request.form['number']
            Whitening_degree=request.form['number1']
            print(file)
            # option = request.form.get("return_form")
            payload = {
                    'image': ('image',file),
                    'Retouch_degree': ('',Retouch_degree),
                    'Whitening_degree': ('',Whitening_degree)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY,
                "X-RapidAPI-Host": "ai-skin-beauty.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_output = output['data']['image_url']
            print(image_output)
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file.save(file.filename)  
            return render_template('beauty_img.html',image_o=image_output)
    return render_template('beauty_img.html')

#increase the beauty of images routing end

#make your face cartoon routing start
@app.route('/cartoon_img', methods=['POST','GET'])
def cartoon_image():
    
    url = "https://cartoon-yourself.p.rapidapi.com/facebody/api/portrait-animation/portrait-animation"

    sql = "SELECT * FROM USER1 WHERE USERD=" +str(session.get('USERD', -1))
    # sql = "SELECT * FROM USER1 WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        user='Loggedin'
        print('loggegin')
        if request.method == "POST":
            # user='Loggedin'
            file = request.files["filename"]
            print(file)
            option = request.form["return_form"]
            print(option)
            payload = {
                    'image': (file),
                    'type': (option)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY3,
                "X-RapidAPI-Host": "cartoon-yourself.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            print(response)
            output=response.json()
            print(output)
            # try:
            #     output = response.json()
            # except json.decoder.JSONDecodeError as e:
            #     print(f"Failed to decode response: {e}")
            #     output = {}
            print(type(output))    # should be a dictionary
            print(dir(output))     # should show the keys of the dictionary
            image_output = output['data']['image_url']
            print(image_output)
            CARTOON_IMG=image_output
            insert_sql = "INSERT INTO IMAGE_URL VALUES (?,NULL,NULL,?,NULL,NULL,NULL,NULL)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, account['USERD'])
            ibm_db.bind_param(prep_stmt, 2, CARTOON_IMG)
            ibm_db.execute(prep_stmt)
            print('image_url sent to db2')
            return render_template('cartoon_img.html',image_o=image_output, user=user)
        return render_template('cartoon_img.html',user=user)
    else:
        if request.method == "POST":
            user='Loggedin'
            file = request.files["filename"]
            print(file)
            option = request.form["return_form"]
            payload = {
                    'image': ('image',file),
                    'return_form': ('anime',option)
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY3,
                "X-RapidAPI-Host": "cartoon-yourself.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_output = output['data']['image_url']
            print(image_output)
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file.save(file.filename)  
            return render_template('cartoon_img.html',image_o=image_output, user=user)
    return render_template('cartoon_img.html')

#make your face cartoon routing end


# Future development code starts
'''
@app.route('/motion_img', methods=['POST','GET'])
def motion_img():

    url = "https://image-micro-motion.p.rapidapi.com/image/enhance/image_micro_motion"
    sql = "SELECT * FROM USER1 WHERE USERD=" +str(session.get('USERD', -1))
    # sql = "SELECT * FROM USER1 WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        user='Loggedin'
        print('loggegin')
        if request.method == "POST":
            file = request.files["filename"]
            print(file)
            image_option = request.form["return_form"]
            print(image_option)
            payload = {
                    'image': ('image',file),
                    'operation': image_option
                }
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY2,
                "X-RapidAPI-Host": "image-micro-motion.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_output = output['data']['url']
            print(image_output)
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file.save(file.filename)
            IMG_MOTION=image_output
            insert_sql = "INSERT INTO IMAGE_URL VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, account['USERD'])
            ibm_db.bind_param(prep_stmt, 2, IMG_MOTION	)
            ibm_db.execute(prep_stmt)
            print('image_url sent to db2')  
            return render_template('motion_img.html',image_o=image_output,user=user)
        return render_template('motion_img.html',user=user)
    else:
          if request.method == "POST":
            file = request.files["filename"]
            print(file)
            image_option = request.form["return_form"]
            print(type(image_option))
            payload = {
                    'image': ('image',file),
                    'operation': image_option
                }
            print(payload)
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY2,
                "X-RapidAPI-Host": "image-micro-motion.p.rapidapi.com"
            }
            response = requests.post(url, headers=headers,files=payload)
            output=response.json()
            print(output)
            image_output = output['data']['url']
            print(image_output)
            # image_b64 = base64.b64encode(file.read()).decode('utf-8')
            # file.save(file.filename)  
            return render_template('motion_img.html',image_o=image_output,user=user)
    return render_template('motion_img.html')

@app.route('/3dcartoon_img', methods=['POST','GET'])
def dcartoon_image():

    url = "https://3d-cartoon-face.p.rapidapi.com/run"

    if request.method == "POST":
        img_url = request.form.get("text")
        print(img_url)
        # image_option = request.form.get("return_form")
        payload = {
            "image": img_url,
            "render_mode": "3d",
            "output_mode": "url"
        }
        headers = {
            'X-RapidAPI-Key': RAPIDAPI_KEY1,
            "X-RapidAPI-Host": "3d-cartoon-face.p.rapidapi.com"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)

        image_output = requests.get('output_url')
        print(image_output)
        # output_url
        # response = requests.post(url, headers=headers,files=payload)
        # print(response.text)
        print('--------------')
        # output=response.json()
        # print(output)
        # image_output = response.text['output_url']
        # print(image_output)
        return render_template('3dcartoon_img.html', imag_o=image_output)
    return render_template('3dcartoon_img.html')'''
# Future development code end


# this lines of code for displaying the images retrived from db2  start
@app.route('/beauty_images')
def beauty_img_ai():
    user='login'
    # user='loggedin'
    sql = "SELECT * FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
    print('rows: ', row)
    return render_template("My_images.html", rows=row, user1=user)

@app.route('/remove_bg_images')
def remove_bg_images():
    user1='login'
    # user='loggedin'
    sql = "SELECT * FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row = []
    while True:
        images_url = ibm_db.fetch_assoc(stmt)
        if not images_url:
            break
        else:
            row.append(images_url)
    print('rows: ', row)
    return render_template("My_images.html", row1=row, user1=user1)

@app.route('/vehicle_images')
def vehicle_img_ai():
    user1='login'
    # user='loggedin'
    sql = "SELECT * FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
    print('rows: ', row)
    return render_template("My_images.html", row2=row, user1=user1)

@app.route('/cartoon_images')
def cartoon_img_ai():
    user1='login'
    # user='loggedin'
    sql = "SELECT * FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
    print('rows: ', row)
    return render_template("My_images.html", row3=row, user1=user1)

# this lines of code for displaying the images in html page retrived from db2  end

# for logout the user start
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('USERD', None)
    return render_template('index.html')

# for logout the user end

# main function start
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')

# main function end