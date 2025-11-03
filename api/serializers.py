from rest_framework import serializers
from .models import User,  UserRole, UserProfile, Skill, Post

#converts user model data into json format
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #fields that will be in response
        fields = ['id', 'email', 'first_name', 'last_name', 'username', 'bio', 'profile_image']

class RegisterSerializer(serializers.ModelSerializer):
    user_role_id = serializers.IntegerField(write_only = True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'user_role_id']
        extra_kwargs = {
            'password': {'write_only': True} #making sure pw isnt returned in api response
        }

    def create(self, validated_data):
        user_role_id = validated_data.pop('user_role_id')

        try:
            user_role = UserRole.objects.get(id = user_role_id)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError("Invalid user role ID provided.")
        
        #using django's create user method to handle password hashing
        user = User.objects.create_user(
            email = validated_data['email'],
            username = validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            password = validated_data['password'],
            user_role = user_role
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    # To display the user's name and email alongside their profile details
    email = serializers.EmailField(source='user.email')

    skills = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Skill.objects.all()
        )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name','email', 'phone_number', 
            'years_of_experience', 'date_of_birth', 
            'gender', 'availability', 'skills'
        ]
        
    def update(self, instance, validated_data):
        # Extract nested user data
        user_data = validated_data.pop('user', {})

        # Update user fields individually
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        skills = validated_data.pop('skills', None)
        if skills is not None:
            instance.skills.set(skills)

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta: 
        model = Post
        fields = ['id', 'author', 'content', 'image_url', 'created_at']

    def get_author(self, obj):
        first = obj.author.first_name or ''
        last = obj.author.last_name or ''
        return f"{first} {last}".strip()

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


#allowing users to add skills to their profile
class AssignSkillSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField()