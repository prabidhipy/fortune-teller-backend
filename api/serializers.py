# serializers.py

from rest_framework import serializers
# Make sure to import all your new models
from .models import (
    User, UserRole, Skill, Post, Comment, Conversation, Message,
    FortuneTellerProfile, ClientProfile
)

# --- No changes needed here ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


# --- MAJOR CHANGE: Update the RegisterSerializer ---
class RegisterSerializer(serializers.ModelSerializer):
    # We still get the role ID during registration
    user_role_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'user_role_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_role_id = validated_data.pop('user_role_id')
        try:
            # We assume roles 'Fortune Teller' and 'Client' exist in the DB with these names
            user_role = UserRole.objects.get(id=user_role_id)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError("Invalid user role ID provided.")

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            user_role=user_role
        )

        # *** THE NEW LOGIC ***
        # After creating the user, create the correct profile for them based on their role.
        if user_role.name.lower() == 'fortune teller':
            FortuneTellerProfile.objects.create(user=user)
        elif user_role.name.lower() == 'client':
            ClientProfile.objects.create(user=user)
        # You can add an 'else' here for other roles like 'Admin' if needed

        return user

class FortuneTellerProfileSerializer(serializers.ModelSerializer):
    # We can pull user info directly from the related user object
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    # We want to see skill names, not just IDs
    #can be deleted
    skills = SkillSerializer(many=True, read_only=True)
    # But for updating, we accept a list of IDs
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), write_only=True, source='skills'
    )

    class Meta:
        model = FortuneTellerProfile
        fields = [
            'user', 'first_name', 'last_name', 'email', 'bio', 'profile_image',
            'phone_number', 'years_of_experience', 'availability',
            'cultural_specialty', 'skills', 'skill_ids'
        ]
        # user field is read-only as it's set on creation
        read_only_fields = ['user']

class ClientProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'user', 'first_name', 'last_name', 'email', 'bio', 'profile_image',
            'date_of_birth', 'gender'
        ]
        read_only_fields = ['user']

class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# --- Post Serializer: Unchanged is fine, but you could add status ---
class PostSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_url', 'created_at', 'status']
        # You might not want users to set the status, so make it read-only
        read_only_fields = ['status']


# --- AssignSkillSerializer: Still useful for Fortune Tellers ---
class AssignSkillSerializer(serializers.Serializer):
    # This serializer can now be used specifically on a FortuneTellerProfile view
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    def update(self, instance, validated_data):
        skill_ids = validated_data.get('skill_ids')
        skills = Skill.objects.filter(id__in=skill_ids)
        instance.skills.set(skills)
        instance.save()
        return instance

# --- NEW SERIALIZERS for new models ---
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'image_url', 'created_at']
        read_only_fields = ['author'] # Author is set from request.user in the view

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'image_url', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    # Nested serializers to show participant details and messages
    participant1 = UserSerializer(read_only=True)
    participant2 = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participant1', 'participant2', 'messages', 'created_at']