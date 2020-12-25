from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.base import View
from validate_email import validate_email
from User.utils import generate_token
from datetime import datetime
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class SignUp(View):
    def get(self, request):
        return render(request, 'blog/landing.html')

    def post(self, request):
        context = {

            'data': request.POST,
            'has_error': False

        }
        email = request.POST.get('email')
        username = request.POST.get('name')
        password = request.POST.get('pass')
        password2 = request.POST.get('re_pass')

        if password != password2:
            messages.add_message(request, messages.ERROR, ' password don\'t match')
            context['has_error'] = True

        if len(password) < 8:
            messages.add_message(request, messages.ERROR, 'invalid password.Password should be minimum of 8 characters')
            context['has_error'] = True

        if len(username) == 0:
            messages.add_message(request, messages.ERROR, 'please provide a valid username')

            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR, 'please provide a valid email..')
            context['has_error'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'email already used by another user')
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'username already taken')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'blog/landing.html', context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.profilepic = ""
        user.is_active = False

        user.save()
        from django.core.mail import EmailMultiAlternatives

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk)),
        token = generate_token.make_token(user)
        # 
        # subject, from_email, to = 'Subcription to Newsletter', settings.EMAIL_HOST_USER, email
        # text_content = 'This is an important message.'
        # html_content = '<div style="line-height: 70px;float:left;margin:1.5rem;width: 100%;max-height: 70px;display:inline-block;">' \
        #                '<a href="http://bitshub.uc.r.appspot.com/"><img src="https://ucarecdn.com/8801c797-68e1-4a2f-8129-2af7f335a7ec/logo.png" alt=""></a></div>' \
        #                '<div style="padding: 30px 0;"><div style="font-size:15px; width: 900px;background: #fff;margin: 0 auto;border-radius: 20px;-moz-border-radius: 20px;-webkit-border-radius: 20px;-o-border-radius: 20px;-ms-border-radius: 20px;"><p style="font-family:sans-serif;">This email has successfully been added to Newsletter, You will recieve notification on new ' \
        #                'posts about the latest tech announcements and my reviews.</p></div></div>' \
        #                '<p style="font-size:15px; width: 900px;background: #fff;margin: 0 auto;border-radius: 20px;-moz-border-radius: 20px;-webkit-border-radius: 20px;-o-border-radius: 20px;-ms-border-radius: 20px;">if you did not sign up to this newsletter or would like to remove your email from the Newsletter, you can follow the link... ' \
        #                '</br>' \
        #                '<a href=" ' + current_site + '/activate/' + uid + '/ ' + token + ' ">Remove Newsletter Email</a></p>'
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()
        email_subject = 'Active your account'
        message = render_to_string('auth/activate_author.html',
                                   {
                                       'user': user,
                                       'domain': current_site.domain,
                                       'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                       'token': generate_token.make_token(user)

                                   }
                                   )
        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        EmailThread(email_message).start()
        messages.add_message(request, messages.SUCCESS,
                             """A Verification link has been sent to your email to confirm your account, you will 
                             receive the mail soon. Please click the link to continue ... 
                             """)
        return render(request, 'auth/activate.html')


class ActiveAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.INFO, 'email verified and account successfully created')
            return redirect('login')
        if not user or not User:
            return render(request, 'blog/error.html', )
        return render(request, 'blog/error.html', )


class LoginView(View):
    def get(self, request):
        return render(request, 'blog/login.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'has_error': False
        }
        username = request.POST.get('your_name')
        password = request.POST.get('your_pass')

        if username == '':
            messages.add_message(request, messages.ERROR, 'Username is required ')
            context['has_error'] = True

        if password == '':
            messages.add_message(request, messages.ERROR, 'password is required ')
            context['has_error'] = True
        user = authenticate(request, username=username, password=password)
        if not user and not context['has_error']:
            messages.add_message(request, messages.ERROR, ' Invalid login details')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'blog/login.html', status=401, context=context)
        login(request, user)
        return redirect('home')


class ResetPasswordView(View):
    def get(self, request):
        return render(request, 'blog/reset.html')

    def post(self, request):
        context = {

            'data': request.POST,
            'has_error': False

        }
        email = request.POST.get('reset-email')
        username = request.POST.get('reset-username')

        if not validate_email(email):
            messages.error(request, "Please enter a valid email")
            context['has_error'] = True
        if len(username) == 0:
            messages.add_message(request, messages.ERROR, 'please provide a valid username')

            context['has_error'] = True
        notuser = User.objects.filter(username=username, email=email)
        if not notuser.exists():
            messages.add_message(request, messages.ERROR, 'please provide a valid username')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'blog/reset.html', context)

        user = User.objects.get(email=email)

        current_site = get_current_site(request)
        email_subject = '  Reset  Password'
        message = render_to_string('auth/reset-password.html',
                                   {
                                       'domain': current_site.domain,
                                       'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                       'token': PasswordResetTokenGenerator().make_token(user)

                                   }
                                   )
        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        EmailThread(email_message).start()

        messages.success(request, 'Your reset password instructions has been sent to your email')
        return redirect('login')


class SetPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        return render(request, 'auth/reset-email.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            context['has_error'] = True
            messages.add_message(request, messages.ERROR, 'Passwords don\'t match!!')

        if len(password) < 8:
            context['has_error'] = True
            messages.add_message(request, messages.ERROR, 'Password should be a minimum of eight character')

        if context['has_error']:
            return render(request, 'auth/reset-email.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password successfully changed')

        except DjangoUnicodeDecodeError as identifier:
            messages.add_message(request, messages.ERROR, 'Something went wrong')
            return render(request, 'auth/reset-email.html', context)

        return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'logout successfully')
        return redirect('login')
