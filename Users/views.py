from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from.forms import*
from .models import*
from Users.models import*
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from validate_email import validate_email
from django.contrib.sites.shortcuts import get_current_site
import django
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError,force_text
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
import threading
from django.views import View
from .utils import generate_token
from.decorators import auth_user_should_not_access
from .email_backend import EmailBackend
from django.db.models import Sum
# Create your views here.

# To MAKE EASIER FOR EMAILING A USER
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()
        #self.email.send(fail_silently=False)

#THE EMAIL BODY TO SEND THE ACTIVATION TO LOGIN
def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('users/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        EmailThread(email).start()


#THE ACTIVATE TOKEN FOR THE EMAIL.
def activate_user(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('account_login'))

    return render(request, 'users/activate-failed.html', {"user": user})


# REGISTER USERS
def account_register(request):
    customuserForm = UserForm(request.POST or None)
    context = {
        'form1': customuserForm,
    }
    if request.method == 'POST':
        if customuserForm.is_valid():
            user = customuserForm.save(commit=False)
            user.save()
            messages.success(request, "Account created. You can login now!")
            send_activation_email(user,request)
            messages.success(request,'We sent you an email to verify your account')
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "users/register.html", context)


#LOGIN USERS
@auth_user_should_not_access
def account_login(request):
    if request.method == 'POST':
        context = {}
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))

        if user and not user.is_email_verified:
            messages.add_message(request,messages.WARNING ,'Email is not verified, please check your email inbox')
            return render(request, 'users/login.html', context, status=401)

        if not user:
            messages.add_message(request, messages.WARNING,
                                 'Invalid credentials, try again')
            return render(request, 'users/login.html', context, status=401)

        login(request, user)

        messages.add_message(request, messages.SUCCESS,
                             f'Welcome  {user.email} ')

        return redirect(reverse('add_group'))

    return render(request, 'users/login.html')



#LOGOUT VIEWS
def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Successfully logout !")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))




#RESET PASSWORD 
class RequestPasswordReset(View):
    def get(self,request):
        return render(request,'users/password_reset.html')


    def post(self,request):
        email=request.POST['email']

        context ={
        'values':request.POST
        }

        if not validate_email(email):
            messages.error(request,'please supply validate email')
            return render(request,'users/password_reset.html',context)

        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = { 
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

            link = reverse('reset-user-password',kwargs={
                'uidb64':email_contents['uid'],'token':email_contents['token']
                })

            email_subject = 'Password reset instruction'

            reset_url='http://'+current_site.domain+link

            email= EmailMessage(
                email_subject,
                'Hi there,Please use the link below to reset your password \n' + reset_url,
                'noreply@semycolon.com',
                [email],
            )
            EmailThread(email).start()
        messages.success(request,'We have sent you an email to reset your password')
        return render(request,'users/password_reset.html')



#COMPLETE RESET PASSWORD
class CompletePasswordReset(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id=force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,'password link is invalid,please request a new one') 
                return render(request,'users/password_reset.html')       
        except Exception as identifer:
            pass
        return render(request,'users/new-password.html',context)


    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.warning(request,'password do not match')
            return render(request,'users/new-password.html',context)
        if len(password) < 6:
            messages.warning(request,'password too short')
            return render(request,'users/new-password.html',context)
        try:
            user_id=force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfully,you can login now with new Password')
            return redirect('account_login') 
        except Exception as identifer:
            messages.info(request,'Something went wrong ,try again')
            return render(request,'users/new-password.html',context)


