from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.utils.http import urlsafe_base64_decode

from accounts.forms import UserForm
from accounts.models import User
from accounts.utils import detect_user, send_verification_email
from vendor.forms import VendorForm
from django.core.exceptions import PermissionDenied


# Create your views here.
def get_user_details_from_request(request):
    pass


# Restrict user from accessing wrong dashboard
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied()


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied()


def register_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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

            # Send  verification email
            send_verification_email(request, user, 'Please activate your account',
                                    'accounts/emails/account_verification.html')
            messages.success(request, 'Your account has been created successfully')
            return redirect('register-user')
            pass
        else:
            pass
    else:
        form = UserForm()
    return render(request, 'accounts/register.html', {'form': form})


def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = User.objects.create_user(first_name, last_name, username, email, password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.save()

            # Send  verification email
            send_verification_email(request, user)

            messages.success(request, 'Your account has been created successfully, please wait for approval')
            return redirect('register-vendor')
    else:
        form = UserForm()
        v_form = VendorForm()
        context = {
            'form': form,
            'v_form': v_form
        }
        return render(request, 'accounts/register-vendor.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Your credentials do not match our records')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('home')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def vendor_dashboard(request):
    return render(request, 'accounts/vendor-dashboard.html')


@login_required(login_url='login')
def profile(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: User | None = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, your account is activated!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect(request, 'dashboard')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            # send reset password email
            send_verification_email(request, user, 'Reset your password',
                                    'accounts/emails/reset_password.html')

        messages.success(request, "You'll receive an email if your account exists")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, "accounts/forgot-password.html")


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        if password_confirmation == password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password Reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do no match')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, "accounts/reset-password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: User | None = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired')
        return redirect('forgot_password')
