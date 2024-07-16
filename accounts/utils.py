
import pytz, hashlib, logging, jwt
from datetime import datetime
from rest_framework.authentication import SessionAuthentication
from accounts.models import Users
from salseforce_management.constants import(
    ENCODE,
    DECODE,
    JWT_SECRECT_KEY,
)
from salseforce_management.settings import OPEN_API
from django.urls import resolve

def get_current_timestamp_of_timezone(time_zone):
    """get current timestamp of given timezone"""
    timezone = pytz.timezone(time_zone)
    return round(datetime.now(timezone).timestamp())

def hash_given_password(password):
    password_hash_key = password
    output = hashlib.md5(password_hash_key.encode()).hexdigest()
    return output

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

def encode_decode_jwt_token(data_to_convert, convertion_type):
    if convertion_type == ENCODE:
        try:
            response = jwt.encode(payload = data_to_convert, key = JWT_SECRECT_KEY, algorithm = "HS256")
        except Exception as e:
            logging.error(e)
            response = ""
    if convertion_type == DECODE:
        try:
            response = jwt.decode(jwt = data_to_convert, key = JWT_SECRECT_KEY, algorithms = ["HS256"])
        except Exception as e:
            logging.error(e)
            response = {}
    return response

def validate_jwt_token(token):
    try:
        user_details = encode_decode_jwt_token(token, convertion_type=DECODE)
        if user_details:
            user_query = Users.objects.filter(user_id = user_details['id'])
            token_status = True if user_query else False
            return token_status
        return False
    except Exception as error:
        logging.error("Exception occured while validating jwt token {}".format(error))
        return False

def is_api_open(request):
    try:
        if OPEN_API.get(resolve(request.path).url_name):
            return True
    except:
        return False
        
def check_feature_permission(token):
    token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
    return token_data['is_admin']
