from django.shortcuts import render, redirect
import os
import logging
from time import localtime
from login.models import LoginUser

# Create your views here.
# to log the track
if not os.path.exists("./log"):
    os.mkdir("./log")

t = localtime()
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                        datefmt='%a, %d %b %Y %H:%M:%S', filename="log/%d_%d_%d.log"%(t[0],t[1],t[2]), filemode='a')    # initialize the logging format


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        uid = request.POST.get('uid', '')
        password = request.POST.get('password', '')

        logging.debug("\n\n\t** %s\n\t** %s\n\n"%(uid, password))

        try:
            d = LoginUser.objects.get(email=uid)

            if d:
                if d.password == password:
                    req = redirect("/home/")
                    req.set_signed_cookie(key="isLogin", value=uid, max_age=60*30, salt="20200809")
                    return req
            else:
                return redirect("/login/")

        except Exception as e:
            print(e)
            logging.error("\n%s\n"%e)
        return render(request, "login.html")


def register(request):
    if request.method == "GET":
        return render(request, "register.html")
    else:
        uid = request.POST.get('uid', '')
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')
        email_tail = ["qq.com", "163.com", "126.com", "sina.com",
                      "sina.cn", "139.com", "outlook.com", "gmail.com"]

        if not uid.split("@")[-1] in email_tail:
            return render(request, "re_register.html")

        try:
            # We use register page to edit user's info
            user = LoginUser.objects.get(email=uid)
            user.name = name
            user.password = password
        except:
            if len(LoginUser.objects.all()) >= 3:
                return render(request, "404.html")
        # print(uid, name, password)

        user = LoginUser(email=uid, name=name, password=password)
        user.save()

        req = redirect("/home/")
        # 设置cookie
        """
        key: cookie的名字
        value: cookie对应的值
        max_age: cookie过期的时间
        """
        req.set_signed_cookie(key="isLogin", value=uid, max_age=60*30, salt="20200809")
        return req


def logout(request):
    rep = redirect('/login/')
    rep.delete_cookie("isLogin")
    return rep # 点击注销后执行,删除cookie,不再保存用户状态，并弹到登录页面

def home(request):
    return render(request, "home.html")