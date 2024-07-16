import logging, pytz, uuid
from datetime import datetime
from rest_framework.views import APIView
from accounts.models import Users, Notes, UserToken
from accounts.serializers import UserSerializer, NotesSerializer
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from accounts.utils import (
    hash_given_password,
    CsrfExemptSessionAuthentication,
    encode_decode_jwt_token,
    get_current_timestamp_of_timezone,
    check_feature_permission,
)
from django.db.models import Q
from salseforce_management.constants import(
    ENCODE,
    DECODE,
    USER_DOSENT_EXISTS,
    USER_LOGGED_IN_SUCCESSFULLY,
    USER_LOGGED_OUT_SUCCESSFULLY,
    INVALID_CREDENTIALS,
    USER_REGISTERED_SUCCESSFULLY,
    UNAUTHORISED_ACCESS,
    USER_DELETED_SUCCESSFULLY,
    ACCOUNT_RETRIEVED_SUCCESSFULLY,
    USER_UPDATED_SUCCESSFULLY,
    NOTES_ADDED_SUCCESSFULLY,
    NOTES_DELETED_SUCCESSFULLY,
    NOTES_RETRIEVED_SUCCESSFULLY,
    NOTES_UPDATED_SUCCESSFULLY,
)
from salseforce_management.settings import TIME_ZONE

class LoginView(APIView):
    def post(self, request):
        try:
            userExist = Users.objects.filter(Q(username=request.data['username'])|Q(email=request.data['username']))
            if userExist.exists():
                user_object = userExist.get()
            else:
                return Response({"status": HTTP_404_NOT_FOUND, "message": USER_DOSENT_EXISTS, "data": []})
            user_details = UserSerializer(user_object).data
            request_password = hash_given_password(request.data["password"])
            if request_password == user_details.get('password'):
                admin_token_details = {
                    'id' : user_details.get('user_id'),
                    'username': request.data['username'],
                    'email': user_details.get('email'),
                    'is_admin': user_details.get('is_admin'),
                    'token_id': str(uuid.uuid4())
                }
                current_time = get_current_timestamp_of_timezone(TIME_ZONE)
                created_at= datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
                UserToken.objects.create(
                    token_id=admin_token_details['token_id'],
                    user_id=user_object,
                    created_at=created_at
                )
                access_token = encode_decode_jwt_token(admin_token_details, convertion_type=ENCODE)
                response = {"status": HTTP_200_OK, "message": USER_LOGGED_IN_SUCCESSFULLY, "data": []}
                logging.info(response)
                return Response(response, headers = {"Authorization": access_token})
            else:
                response = {"status": HTTP_401_UNAUTHORIZED, "error": INVALID_CREDENTIALS, "data": None}
                logging.info(response)
                return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class LogoutView(APIView):

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
            UserToken.objects.filter(token_id=token_data['token_id']).delete()
            response = {"status": HTTP_200_OK, "message": USER_LOGGED_OUT_SUCCESSFULLY, "data": []}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class RegisterUser(CreateAPIView):
    def post(self, request):
        try:
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data.update({'password': hash_given_password(request.data['password']),
                                 'created_at': datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S"),
                                 'user_id': uuid.uuid4()})
            serializer = UserSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_201_CREATED, "message": USER_REGISTERED_SUCCESSFULLY, "data": serializer.data}
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                logging.info(response)
                return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class ListDeleteUsers(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not check_feature_permission(token):
            response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
            logging.info(response)
            return Response(response)        
        query_dict = {}
        queryset  = Users.objects.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result
    
    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            if not check_feature_permission(token):
                response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
                logging.info(response)
                return Response(response)

            deleted_users = []
            users_list = Users.objects.filter(user_id__in = request.data['user_ids'])
            for user_object in users_list:
                user_data = UserSerializer(user_object).data
                deleted_users.append(user_data)
                user_object.delete()
            response = {"status": HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY, "data": deleted_users}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class RetrieveUpdateDeleteUser(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, **kwargs):
        try:
            user_id = str(kwargs['user_id'])
            user_query = Users.objects.filter(user_id= user_id)
            user_object = user_query.get()
            user_data = UserSerializer(user_object).data
            response = {"status": HTTP_200_OK, "message": ACCOUNT_RETRIEVED_SUCCESSFULLY, "data": user_data}
            logging.info(response)
            return Response(response)        
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def patch(self, request, **kwargs):
        try:
            user_id = str(kwargs['user_id'])
            user_query = Users.objects.filter(user_id = user_id)
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['updated_at'] = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
            user_object = user_query.get()
            serializer = UserSerializer(user_object, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_200_OK, "message": USER_UPDATED_SUCCESSFULLY, "data": serializer.data}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def delete(self, request, **kwargs):
        try:
            user_id = str(kwargs['user_id'])
            user_query = Users.objects.filter(user_id=user_id)
            user_object = user_query.get()
            user_object.delete()
            response = {"status": HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class ListCreateDeleteNotes(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not check_feature_permission(token):
            response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
            logging.info(response)
            return Response(response)
        query_dict = {}
        queryset  = Notes.objects.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotesSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result
    
    def post(self, request):
        try:
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
            request.data.update({
                'user_id': token_data['id'], 'notes_id': uuid.uuid4(),
                'created_at': datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S"),
            })
            serializer = NotesSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_201_CREATED, "message": NOTES_ADDED_SUCCESSFULLY, "data": serializer.data}
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                logging.info(response)
                return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
    
    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            if not check_feature_permission(token):
                response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
                logging.info(response)
                return Response(response)

            deleted_users = []
            notes_list = Notes.objects.filter(user_id__in = request.data['user_ids'])
            for obj in notes_list:
                user_data = NotesSerializer(obj).data
                deleted_users.append(user_data)
                obj.delete()
            response = {"status": HTTP_200_OK, "message": NOTES_DELETED_SUCCESSFULLY, "data": deleted_users}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class RetrieveUpdateDeleteNotes(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, **kwargs):
        try:
            notes_id = str(kwargs['notes_id'])
            user_query = Notes.objects.filter(notes_id= notes_id)
            user_object = user_query.get()
            user_data = NotesSerializer(user_object).data
            response = {"status": HTTP_200_OK, "message": NOTES_RETRIEVED_SUCCESSFULLY, "data": user_data}
            logging.info(response)
            return Response(response)        
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def patch(self, request, **kwargs):
        try:
            notes_id = str(kwargs['notes_id'])
            user_query = Notes.objects.filter(notes_id = notes_id)
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['updated_at'] = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
            user_object = user_query.get()
            serializer = NotesSerializer(user_object, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_200_OK, "message": NOTES_UPDATED_SUCCESSFULLY, "data": serializer.data}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def delete(self, request, **kwargs):
        try:
            notes_id = str(kwargs['notes_id'])
            user_query = Notes.objects.filter(notes_id=notes_id)
            user_object = user_query.get()
            user_object.delete()
            response = {"status": HTTP_200_OK, "message": NOTES_DELETED_SUCCESSFULLY, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class RetrieveUserNotes(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, **kwargs):
        user_id = str(kwargs['user_id'])
        token = request.META.get('HTTP_AUTHORIZATION', None)
        token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
        if token_data['id']!=user_id:
            response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
            logging.info(response)
            return Response(response)
        query_dict = {'user_id': user_id}
        queryset  = Notes.objects.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotesSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result