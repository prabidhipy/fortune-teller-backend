# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- No Changes Here ---
class UserRole(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# --- User Model: Minor Change ---
class User(AbstractUser):
    # We remove bio and profile_image from here, as they belong in profiles.
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=False)
    user_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, blank=True, null=True)

    # We can keep USERNAME_FIELD and REQUIRED_FIELDS as is.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.username

class FortuneTellerProfile(models.Model):
    """Holds data specific ONLY to fortune tellers."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    availability = models.TextField(blank=True)
    cultural_specialty = models.CharField(max_length=255, blank=True) # Added this based on your report
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Fortune Teller Profile"

class ClientProfile(models.Model):
    """Holds data specific ONLY to clients."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Client Profile"


# --- Post Model: Add STATUS field ---
class Post(models.Model):
    class PostStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        PUBLISHED = 'PUBLISHED', 'Published'
        REJECTED = 'REJECTED', 'Rejected'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image_url = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=PostStatus.choices,
        default=PostStatus.PENDING
    )

    def __str__(self):
        return f"Post by {self.author.first_name} at {self.created_at.strftime('%Y-%m-%d')}"


# --- NEW MODELS to add at the end of the file ---
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image_url = models.ImageField(upload_to='comment_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"

class Conversation(models.Model):
    # Using participant names that are clear
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations1')
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.participant1.username} and {self.participant2.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image_url = models.ImageField(upload_to='message_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"