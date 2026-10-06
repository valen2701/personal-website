from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author_name', 'body')
        widgets = {
            'author_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'body': forms.Textarea(attrs={'rows': 4}),
        }
