from django.contrib import admin
from .models import User, UserRole, Skill, UserProfile, Post

admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(Skill)
admin.site.register(UserProfile)
admin.site.register(Post)