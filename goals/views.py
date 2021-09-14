from django.shortcuts import render, redirect
from django.http import HttpResponse

from login.models import LoginUser
from goals.models import Goals, Together

# Create your views here.
def goals(request, uid=None):
    content = {}
    content["other_data"] = []
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
    
    if "visitor" in uid:
        return render(request, "Visualization.html")
    
    goal = Goals.objects.filter(uid=uid)
    if request.method == "GET":
        username = LoginUser.objects.get(email=uid).name
        content["username"] = username

        # fill the goals block's data
        content["data"] = []
        len_goal = len(goal)
        if len_goal > 0:
            for i in range(len_goal):
                content["data"].append([clean_str(goal[i].gid),
                                       i+1,
                                       clean_str(goal[i].life),
                                       clean_str(goal[i].study),
                                       clean_str(goal[i].interest)])
        if len_goal < 5:
            for i in range(5-len_goal):
                content["data"].append([None,
                                        i + len_goal + 1,
                                        None,
                                        None,
                                        None])

        t_other = Goals.objects.filter().exclude(uid=uid).all()
        len_goal = len(t_other)
        if len_goal > 0:
            for i in range(len_goal):
                content["other_data"].append([clean_str(t_other[i].gid),
                                              i + 1,
                                              clean_str(t_other[i].life),
                                              clean_str(t_other[i].study),
                                              clean_str(t_other[i].interest)])
        if len_goal < 5:
            for i in range(5 - len_goal):
                content["other_data"].append([None,
                                              i + len_goal + 1,
                                              None,
                                              None,
                                              None])

        # fill the together block's data
        content["together"] = []
        t = Together.objects.all()
        for i in range(len(t)):
            content["together"].append([clean_str(t[i].tid),
                                          clean_str(t[i].type),
                                          clean_str(t[i].name),
                                          clean_str(t[i].describe),
                                          t[i].done])

        return render(request, "home.html", content)
    else:
        gid = request.POST.get("id", "")
        life = clean_str(request.POST.get("life", ""))
        study = clean_str(request.POST.get("study", ""))
        interest = clean_str(request.POST.get("interest", ""))
        edit = True
        new = False
        if gid != "" and gid != "None":
            t = Goals.objects.get(gid=gid)
        else:
            t = Goals.objects.create(uid=uid)
            new = True
        if life != "":
            t.life = life
        elif study != "":
            t.study = study
        elif interest != "":
            t.interest = interest
        else:
            edit = False

        # to ensure the edit is legal
        if edit:
            t.save()

        return redirect("/home/")


def together(request):
    content = {}
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

    if "visitor" in uid:
        return render(request, "Visualization.html")
    
    tid = request.POST.get("id", "")
    name = request.POST.get("name", "")
    if tid != "":
        t = Together.objects.get(tid=tid)
        t.done = 1
    else:
        des = request.POST.get("describe", "")
        type_of_t = request.POST.get("type", "")
        print(name, des)
        t = Together.objects.create(name=name, describe=des, type=type_of_t)
    if tid != "" or name != "":
        t.save()
    return redirect("/home/")


def clean_str(text):
    nota = "\t\n\s"
    for i in nota:
        text = str(text).replace(i, "")
    return text