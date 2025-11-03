from django.urls import path
from .views import UserListView, RegisterView, UserProfileView, PostListCreateView, SkillListCreateView, AssignSkillView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, #checks the email anad password and authenticates from the db automatically
    TokenRefreshView
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('skills/', SkillListCreateView.as_view(), name='skill-list-create'),
    path('profile/skills/', AssignSkillView.as_view(), name = 'assign-skill'),
]