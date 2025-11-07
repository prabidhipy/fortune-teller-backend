from django.urls import path
from .views import (
    UserListView,
    RegisterView,
    MyProfileView, 
    PostListCreateView,
    CommentListCreateView, 
    ConversationListCreateView, 
    SkillListCreateView,
    PostDetailView, # <-- IMPORT
    FortuneTellerListView, # <-- IMPORT
    FortuneTellerSearchView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    # User and Auth URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile URL (uses the new intelligent view)
    path('profile/', MyProfileView.as_view(), name='my-profile'),

    # Post and Comment URLs
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:post_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'), # <-- ADD THIS


    # Conversation URL
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),

    # Skill URL
    path('skills/', SkillListCreateView.as_view(), name='skill-list-create'),
    
    # Admin-only URL (Good Practice)
    path('users/', UserListView.as_view(), name='user-list'),

    # Teller Suggestion and Search URLs
    path('tellers/suggestions/', FortuneTellerListView.as_view(), name='teller-suggestions'), # <-- ADD
    path('tellers/search/', FortuneTellerSearchView.as_view(), name='teller-search'),
]