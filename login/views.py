from django.shortcuts import render, redirect
import os
import logging
import time
import pandas as pd

from time import localtime
from login.models import LoginUser, Track
from tools.views import fansy_bar

# Create your views here.
# to log the track
if not os.path.exists("./log"):
    os.mkdir("./log")

t = localtime()
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                        datefmt='%a, %d %b %Y %H:%M:%S', filename="log/%d_%d_%d.log"%(t[0],t[1],t[2]), filemode='a')    # initialize the logging format


def track_result(request):
    # to ensure the user is login
    try:
        uid = request.get_signed_cookie(key="isLogin", salt="20200809")
    except:
        return redirect('/login/')
    try:
        status = request.get_signed_cookie(key="isLogin", salt="20200809")
        if (status != uid) and (uid != None):
            return redirect('/login/')
    except:
        return redirect('/login/')

    t = Track.objects.all()
    index = []
    t_dic = {
            "Activity": [],
            "User": []
        }
    for i in t:
        t_dic["Activity"].append(i.activity)
        if i.uid == "1135235700@qq.com":
            t_dic["User"].append("Vincent")
        elif i.uid == "1161390256@qq.com":
            t_dic["User"].append("Artemis")
        elif i.uid == "visitor@qq.com":
            t_dic["User"].append("Visitor")
        else:
            t_dic["User"].append("Strangers")
        index.append(i.time)

    df = pd.DataFrame(t_dic, index=index)
    stat = df.groupby(["User"])
    activities = df["Activity"].unique()
    columns = ["Vincent", "Artimes", "Visitor", "Strangers"]
    t_dic = {"Vincent": [], "Artimes":[], "Visitor":[], "Strangers":[]}

    for name in columns:
        act_tmp = []
        if name in stat.groups.keys():
            df_tmp = stat.get_group(name)
            for act in activities:
                try:
                    act_tmp.append(df_tmp[df_tmp["Activity"]==act]["User"].count())
                except Exception as e:
                    print(e)
                    act_tmp.append(0)
        else:
            for act in activities:
                act_tmp.append(0)
        t_dic[name] = act_tmp

    df = pd.DataFrame(t_dic, index=list(activities))
    fansy_bar(df, title="Track", x_axis_name="Activity type")
    return redirect("/tools/visual/result")


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
                    track(uid, "login")
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
    

def track(uid, activity):
    try:
        t = Track.objects.create(uid=uid)
        t.time = time.strftime("%Y-%m-%d_%H:%M:%S:", time.localtime())
        t.activity = activity
        t.save()
    except Exception as e:
        print(e)
        logging.error(e)
    