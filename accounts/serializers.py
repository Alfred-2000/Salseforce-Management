from rest_framework.serializers import ModelSerializer
from accounts.models import Users, Notes

class UserSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class NotesSerializer(ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'

        