from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

def show_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('show_home')
    else:
        form = AuthenticationForm()
    
    return render(request, "login/login.html", {'form' : form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')