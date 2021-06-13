from django.shortcuts import redirect

# Create your views here.
def redirect_login(request):
    return redirect("/login/")