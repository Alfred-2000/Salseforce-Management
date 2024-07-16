from django.urls import path
from accounts.views import(
    RegisterUser,
    ListDeleteUsers,
    RetrieveUpdateDeleteUser,
    ListCreateDeleteNotes,
    RetrieveUpdateDeleteNotes,
    RetrieveUserNotes,
)
urlpatterns = [
    path('sign-up/', RegisterUser.as_view(), name='sign-up'),   #Register account
    path('list/', ListDeleteUsers.as_view()),   #List, Delete users
    path('<uuid:user_id>/', RetrieveUpdateDeleteUser.as_view()),    #Retrieve, Update, Delete users
    path('notes/', ListCreateDeleteNotes.as_view()),    #List, Delete notes
    path('notes/<uuid:notes_id>/', RetrieveUpdateDeleteNotes.as_view()),    #Retrieve, Update, Delete notes
    path('user-notes/<uuid:user_id>/', RetrieveUserNotes.as_view()),    #List user notes
]