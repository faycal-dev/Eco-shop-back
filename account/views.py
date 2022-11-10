from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from decouple import config


from .serializers import UserSerializer, EmailVerificationSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from .utils import Util


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = ['http', 'https']


# here we will use the model directly without serializer
class RegisterView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        try:
            data = request.data
            full_name = data['full_name']
            email = data['email']
            username = data['username']
            password = data['password']
            re_password = data['re_password']

            if password == re_password:
                if len(password) >= 8:
                    if not User.objects.filter(email=email).exists():
                        user = User.objects.create_user(
                            email=email,
                            user_name=username,
                            full_name=full_name,
                            password=password,
                        )

                        if User.objects.filter(email=email).exists():
                            current_user = User.objects.get(email=email)
                            token = RefreshToken.for_user(
                                current_user).access_token
                            current_site = get_current_site(request).domain
                            # relativeLink = reverse('email-verify')
                            absurl = 'http://'+current_site + \
                                "/account/email-verify"+"?token="+str(token)
                            email_body = 'Hi '+user.user_name + \
                                ' Use the link below to verify your email \n' + absurl
                            data = {'email_body': email_body, 'to_email': user.email,
                                    'email_subject': 'Verify your email'}

                            Util.send_email(data)
                            return Response(
                                {'success': 'Account created successfully'},
                                status=status.HTTP_201_CREATED
                            )
                        else:
                            return Response(
                                {'error': 'Something went wrong when trying to create account'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
                    else:
                        return Response(
                            {'error': 'Email already exists'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {'error': 'Password must be at least 8 characters in length'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'error': 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to register account'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'success': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if (serializer.is_valid() == False):
            return Response({'error': 'Please check if the email is correct'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email', '')
        try:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(
                    request=request).domain
                relativeLink = "/account/password-reset/" + uidb64 + "/" + token
                # relativeLink = reverse(
                #     'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
                redirect_url = request.data.get('redirect_url', '')
                absurl = 'http://'+current_site + relativeLink
                email_body = 'Hello, \n Use link below to reset your password  \n' + \
                    absurl+"?redirect_url="+redirect_url
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Reset your passsword'}
                Util.send_email(data)
                return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(config('FRONTEND_URL')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(config('FRONTEND_URL')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny, )

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': "Password reset successfully"}, status=status.HTTP_200_OK)


class LoadUserView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        try:
            user = request.user
            user = UserSerializer(user)

            return Response(
                {'user': user.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to load user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangeUserCredentials(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request):
        try:
            id = request.user.id
            user = get_object_or_404(User, id=id)
            data = request.data
            verification_email_sent = False
            if (data["email"] != user.email):
                user.email = data["email"]
                user.is_verified = False
                user.save()
                current_user = user
                token = RefreshToken.for_user(
                    current_user).access_token
                current_site = get_current_site(request).domain
                # relativeLink = reverse('email-verify')
                absurl = 'http://'+current_site + \
                    "/account/email-verify"+"?token="+str(token)
                email_body = 'Hi '+user.user_name + \
                    ' Use the link below to verify your email \n' + absurl
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Verify your email'}
                Util.send_email(data)
                verification_email_sent = True

            if (data["full_name"] != user.full_name):
                user.full_name = data["full_name"]
                user.save()

            return Response({"message": "User modified successfully", "user": UserSerializer(user).data, "verification_email": verification_email_sent}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to modify user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangeUserImage(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request):
        id = request.user.id
        user = get_object_or_404(User, id=id)
        try:
            image = request.data["image"]
            user.image = image
            user.save()
            return Response({"message": "User image updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to modify user password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class ChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request):
        id = request.user.id
        user = get_object_or_404(User, id=id)
        try:
            old_password = request.data["old_password"]
            new_password = request.data["new_password"]
            if not user.check_password(old_password):
                return Response({"error": "Please verify if your password is correct"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user.set_password(new_password)
                user.save()
                return Response({"message": "password updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to modify user password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlacklistTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'success': 'Token blacklisted successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
