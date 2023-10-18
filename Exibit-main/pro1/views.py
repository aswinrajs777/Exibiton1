
from django.shortcuts import render
import pyrebase
import requests
from django.contrib import auth
import os
import moviepy.video.io.ffmpeg_tools
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from django.conf.urls.static import static


from django.shortcuts import render
from django.http import JsonResponse, HttpResponse


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro1.settings')

application = get_wsgi_application()

import os

config = {

'apiKey': "AIzaSyDfStYg1oybMuNWma1-4KGJynjrPwIfyhU",
  'authDomain': "exhibiton-ce35a.firebaseapp.com",
  'databaseURL': "https://exhibiton-ce35a-default-rtdb.firebaseio.com",
  'projectId': "exhibiton-ce35a",
  'storageBucket': "exhibiton-ce35a.appspot.com",
  'messagingSenderId': "241695038706",
  'appId': "1:241695038706:web:91fe325c99c663f7f4c46b",
  'measurementId': "G-Z9LMLY6ZK8"
  }


firebase = pyrebase.initialize_app(config)
database=firebase.database()
authe = firebase.auth()

def landing(request):

    return render(request, "signIn.html")

def singIn(request):

    return render(request, "signIn.html")


def postsign(request):
    email=request.POST.get('email')
    passw = request.POST.get("pass")
    try:
        user = authe.sign_in_with_email_and_password(email,passw)
    except:
        message = "invalid cerediantials"
        return render(request,"signIn.html",{"msg":message})
    print(user)
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request, "upload.html",{"name":name})

def logout(request):
    auth.logout(request)
    return render(request,'signIn.html')


def postsignup(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = authe.create_user_with_email_and_password(email, passw)
        uid = user['localId']
        data = {"name": name, "status": "1"}
        database.child("users").child(uid).child("details").set(data)
        authe.send_email_verification(user['idToken'])

    except:
        message = "Weak Password, Use Some Special Characters"
        return render(request, "signIn.html", {"messg": message})


    return render(request, "signIn.html",{"messg": "Check Your Mail!"})


def create(request):
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    name = database.child('users').child(a).child('details').child('name').get().val()
    return render(request,'upload.html',{"name":name})

def post_create(request):


    millis = "videourls"
    print("mili"+str(millis))
    url = request.POST.get('url')
    urlcsv = request.POST.get('csvurl')
    idtoken= request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    print("info"+str(a))
    data = {
        'url':url

    }
    database.child('users').child(a).child('reports').child(millis).set(data)


    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    img_url = database.child('users').child(a).child('reports').child('videourls').child('url').get().val()
    # print(img_url)
    



    return render(request,'Csvupload.html', {'i':img_url})
def load_file(filepath):
    response = requests.get(filepath)
    if response.status_code == 200:
        filepath1=os.path.join('static', 'files/sheets.csv')
        with open(filepath1, "wb") as file:
            file.write(response.content)
            print("Excel File has been Fetched and written Successfully!")
        return True
    else:
        return False

def post_createcsv(request):
    millis = "csvurls"
    print("mili" + str(millis))
    url = request.POST.get('url')
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    print("info" + str(a))
    data = {
        'csvurl': url

    }
    database.child('users').child(a).child('reports').child(millis).set(data)

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    video_url = database.child('users').child(a).child('reports').child('videourls').child('url').get().val()
    csv_url = database.child('users').child(a).child('reports').child('csvurls').child('csvurl').get().val()
    print("csvurl")
    print(csv_url)
    load_file(csv_url)


    return render(request, 'videopage.html', {'i': video_url,'e':csv_url,})

def crop(request):

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    video_url = database.child('users').child(a).child('reports').child('videourls').child('url').get().val()

    return render(request,'crop.html', {'i': video_url,})
def crop_video(request):
    if request.method == 'POST':
        try:
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')

            # Convert start and end times from HH:MM:SS to seconds
            start_time = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time_str.split(':')))
            end_time = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time_str.split(':')))

            if start_time >= end_time:
                return HttpResponse("Invalid time range", status=400)

            input_video_path = "Trial with 5MP camera (1).mp4"  # Replace with your input video path
            output_video_path = "output_cropped_video.mp4"

            ffmpeg_extract_subclip(input_video_path, start_time, end_time, targetname=output_video_path)

            with open(output_video_path, 'rb') as video_file:
                response = HttpResponse(video_file.read(), content_type='video/mp4')
                response['Content-Disposition'] = 'attachment; filename="cropped_video.mp4"'
                return response

        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse("Invalid request method", status=405)