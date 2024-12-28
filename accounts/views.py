from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('polls:cargar_csv')  
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirige a la página de login después de cerrar sesión




def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username=username, password=password1)
                login(request, user)
                return redirect('login')
            except:
                messages.error(request, 'Error al crear el usuario. El nombre de usuario ya existe.')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')
    return render(request, 'register.html')
