from django import forms
from .models import Site, Post
from crispy_forms.helper import FormHelper

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
<<<<<<< HEAD
        fields = ['url']  # include the new fields
=======
        fields = ['title', 'description', 'url']  # include the new fields
>>>>>>> 01e5779932cb5b80a3b140e4d4d7a2e2d1408720


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'url', 'content']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
