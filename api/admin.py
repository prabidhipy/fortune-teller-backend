# api/admin.py

from django.contrib import admin
from .models import (
    User, UserRole, Skill, Post, Comment, FortuneTellerProfile,
    ClientProfile, Conversation, Message
)

# Customizing the Post admin view to show the status
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'status', 'created_at', 'modified_at')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('author__username', 'content')

# Register your models
admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(Skill)
admin.site.register(FortuneTellerProfile)
admin.site.register(ClientProfile)
admin.site.register(Comment)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Post, PostAdmin)


admin.site.site_header = "Fortune Club Admin Portal"  # Main header in the admin panel
admin.site.site_title = "Fortune Club Admin"         # Title in the browser tab
admin.site.index_title = "Welcome to the Fortune Club Portal" # Sub-header on the main admin page