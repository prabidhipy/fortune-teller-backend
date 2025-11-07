# views.py

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrReadOnly
from .models import FortuneTellerProfile
from django.db.models import Q 

# --- Import all new models and serializers ---
from .models import (
    User, UserRole, Skill, Post, Comment, Conversation, Message,
    FortuneTellerProfile, ClientProfile
)
from .serializers import (
    UserSerializer, RegisterSerializer, SkillSerializer,
    FortuneTellerProfileSerializer, ClientProfileSerializer,
    PostSerializer, CommentSerializer, ConversationSerializer
)


# ===================================================================
# USER AND PROFILE VIEWS
# ===================================================================

# --- No changes needed ---
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Good practice to restrict this to admins

# --- No changes needed, logic is in serializer ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# --- REPLACED: UserProfileView is now MyProfileView ---
class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    An intelligent view that retrieves or updates the profile
    for the currently authenticated user, automatically handling
    whether they are a Fortune Teller or a Client.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Determine which profile to fetch based on the user's role
        try:
            if self.request.user.user_role.name.lower() == 'fortune teller':
                return self.request.user.fortunetellerprofile
            elif self.request.user.user_role.name.lower() == 'client':
                return self.request.user.clientprofile
        except (UserRole.DoesNotExist, FortuneTellerProfile.DoesNotExist, ClientProfile.DoesNotExist):
            return None # Handle case where profile or role doesn't exist
        return None

    def get_serializer_class(self):
        # Determine which serializer to use based on the user's role
        try:
            if self.request.user.user_role.name.lower() == 'fortune teller':
                return FortuneTellerProfileSerializer
            elif self.request.user.user_role.name.lower() == 'client':
                return ClientProfileSerializer
        except UserRole.DoesNotExist:
            pass
        # Fallback or error serializer if needed
        return UserSerializer # Should not happen in normal flow

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({"error": "Profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({"error": "Profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# --- PostListCreateView with moderation logic ---
class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Admins see all posts.
        Authenticated users see all PUBLISHED posts AND their own PENDING posts.
        Unauthenticated users see only PUBLISHED posts.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Post.objects.all().order_by('-created_at')
            
            # THE FIX: Show published posts OR the user's own pending posts
            return Post.objects.filter(
                Q(status=Post.PostStatus.PUBLISHED) | 
                Q(author=user, status=Post.PostStatus.PENDING)
            ).distinct().order_by('-created_at')
        
        # For non-logged-in users
        return Post.objects.filter(status=Post.PostStatus.PUBLISHED).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# --- View for listing and creating comments on a specific post ---
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Filter comments to only those for the post specified in the URL
        post_id = self.kwargs['post_pk']
        return Comment.objects.filter(post_id=post_id).order_by('created_at')

    def perform_create(self, serializer):
        # Automatically associate the comment with the post from the URL and the author from the request
        post_id = self.kwargs['post_pk']
        serializer.save(author=self.request.user, post_id=post_id)

class SkillListCreateView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()] # Only allowing admins to create skills
        return [IsAuthenticatedOrReadOnly()]


# --- AssignSkillView for Fortune Tellers ---
#can be deleted
class AssignSkillView(APIView):
    """
    A dedicated view for a Fortune Teller to update their skills.
    Accepts a POST request with a list of skill IDs.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'fortunetellerprofile'):
            return Response(
                {'error': 'Only users with a Fortune Teller profile can assign skills.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        skill_ids = request.data.get('skill_ids', [])
        if not isinstance(skill_ids, list):
            return Response({'error': 'skill_ids must be a list of integers.'}, status=status.HTTP_400_BAD_REQUEST)

        profile = request.user.fortunetellerprofile
        # Create a serializer instance to validate and update
        serializer = FortuneTellerProfileSerializer(instance=profile, data={'skill_ids': skill_ids}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'status': 'Skills updated successfully.', 'skills': serializer.data['skills']}, status=status.HTTP_200_OK)


# ---  View to list a user's conversations or start a new one ---
class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all conversations where the current user is a participant
        user = self.request.user
        return Conversation.objects.filter(Q(participant1=user) | Q(participant2=user)).distinct()

    def perform_create(self, serializer):
        # Expects 'participant2_id' in the request data
        participant2_id = self.request.data.get('participant2_id')
        participant2 = User.objects.get(id=participant2_id)
        # Prevent creating duplicate conversations
        existing_conversation = Conversation.objects.filter(
            (Q(participant1=self.request.user) & Q(participant2=participant2)) |
            (Q(participant1=participant2) & Q(participant2=self.request.user))
        ).first()

        if existing_conversation:
            # If conversation exists, don't create a new one. You might want to return the existing one.
            # This requires custom logic outside the standard create flow.
            # For now, we'll let it raise an integrity error or you can handle it gracefully.
            pass
        else:
            serializer.save(participant1=self.request.user, participant2=participant2)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    # api/views.py

# ... at the end of the file, add these two new views ...

class FortuneTellerListView(generics.ListAPIView):
    """
    Provides a list of all users with the 'Fortune Teller' role.
    Used for the "Suggestions" sidebar.
    """
    queryset = FortuneTellerProfile.objects.all()
    serializer_class = FortuneTellerProfileSerializer
    permission_classes = [IsAuthenticated]


class FortuneTellerSearchView(generics.ListAPIView):
    """
    Provides search functionality for Fortune Tellers.
    Searches by name and skill.
    e.g., /api/tellers/search/?q=John or /api/tellers/search/?q=Tarot
    """
    serializer_class = FortuneTellerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query is not None:
            # Search in user's first name, last name, and their skills' names
            return FortuneTellerProfile.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(skills__name__icontains=query)
            ).distinct()
        return FortuneTellerProfile.objects.none() # Return nothing if no query