from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.forms import UserForm
from accounts.models import User


# Create your views here.
def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = User.objects.create_user(first_name, last_name, username, email, password)
            user.role = User.CUSTOMER
            user.save()

            messages.success(request, 'Your account has been created successfully')
            return redirect('register-user')
            pass
        else:
            pass
    else:
        form = UserForm()
    return render(request, 'accounts/register.html', {'form': form})
