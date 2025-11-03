
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#user role table definition
class UserRole(models.Model):
    name = models.CharField(max_length =100, unique=True)

    def __str__(self):
        return self.name
    
#user table definition (extends django's built-in user table)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length = 50, blank=False)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    user_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.username

#defining skill table
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

#defining profile table
class UserProfile(models.Model):
    #one to one link with user model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    phone_number = models.CharField(max_length=20, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    availability = models.TextField(blank=True)

    #many to many with skill table
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"

#post table deifnition
class Post(models.Model):
    #user who created the post
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image_url = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.author.first_name} at {self.created_at.strftime('%Y-%m-%d')}"