from django import forms
from .models import Site, Post
from crispy_forms.helper import FormHelper

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['url']  # include the new fields


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'url', 'content']

