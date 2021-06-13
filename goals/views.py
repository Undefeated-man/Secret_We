from django.shortcuts import render, redirect
from django.http import HttpResponse

from login.models import LoginUser
from goals.models import Goals

# Create your views here.
def goals(request, uid=None):
    print("start")
    context = {}
    # to ensure the user is login
    uid = request.get_signed_cookie(key="isLogin", salt="20200809")
    try:
        status = request.get_signed_cookie(key="isLogin", salt="20200809")
        if (status != uid) and (uid != None):
            return redirect('/login/')
    except:
        return redirect('/login/')

    if request.method == "GET":
        username = LoginUser.objects.get(email=uid).name
        context["username"] = username
        return render(request, "home.html", context)
    else:
        print("POST")
        gid = request.POST.get("id", "")
        life = request.POST.get("life", "")
        study = request.POST.get("study", "")
        interest = request.POST.get("interest", "")
        edit = True

        if gid != "":
            t = Goals.objects.get(gid=gid)
        else:
            t = Goals.objects.create()
        if life != "":
            study = t.study
            interest = t.interest
        elif study != "":
            life = t.life
            interest = t.interest
        elif interest != "":
            life = t.life
            study = t.study
        else:
            edit = False

        # to ensure the edit is legal
        if edit:
            goal = Goals(life=life, study=study, interest=interest)
            goal.save()
