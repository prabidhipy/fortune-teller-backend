from rest_framework import generics, permissions, status
from .models import User, UserProfile, Post, Skill # Add UserProfile
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer, PostSerializer, SkillSerializer, AssignSkillSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response

#returns a list of all users
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#createapiview is designed for post requests
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile

#allows get and post
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly] #only letting authenticated users create a post otherwise just read

    def perform_create(self, serializer):
        serializer.save(author= self.request.user)

class SkillListCreateView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly] #anyone will get but post only by amdin

    def get_permission(self):
        if self.request.method == 'POST':
            return [IsAdminUser()] #only allowing admins to create post
        return super().get_permissions()
    
class AssignSkillView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignSkillSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            skill_id = serializer.validated_data['skill_id']
        
            try:
                skill = Skill.objects.get(id=skill_id)
                user_profile = request.user.userprofile

                #add the skill to the user's profile's skills relationship
                user_profile.skills.add(skill)

                return Response({'status': 'Skill added.'}, status=status.HTTP_200_OK)
            except Skill.DoesNotExist:
                return Response({'error': 'Skill not found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)