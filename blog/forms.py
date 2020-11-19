from django import forms
from tinymce import TinyMCE
from .models import Post, Comments,Category,Tag
from mptt.forms import TreeNodeChoiceField

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

class NewCommentForms(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 6, 'rows': 1}
        )
    )

    class Meta:
        model = Post
        fields = ('title', 'content', 'thumbnail',
                  'categories', 'featured')




class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 1}
        )
    )

    class Meta:
        model = Post
        fields = ('title', 'content', 'thumbnail',
        'categories', 'tag')

class PostFor(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 1}
        )
    )

    title = forms.CharField(widget=forms.Textarea(attrs={'overflow': 'auto', 'class': 'status-textarea', 'cols': 30, 'rows': 1, 'placeholder': 'Write something (title)'}))
    categories = forms.ModelChoiceField(queryset= Category.objects.all().order_by('title'), initial= 0, widget=forms.Select(attrs={'class': 'form-control','style':'width:50%;'}))
    tag = forms.ModelMultipleChoiceField(queryset= Tag.objects.all(), initial= 0, widget=forms.Select(attrs={'class': 'form-control', 'style':'width:50%;'}))

    class Meta:
        model = Post
        fields = ('title', 'content', 'thumbnail', 'categories', 'tag')





class NewCommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comments.objects.all())
    thumbnail = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update(
            {'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comments
        fields = ('parent', 'content','thumbnail')

        widgets = {
            'content': forms.Textarea(attrs={'class': 'col-12','placeholder': 'Type your comment',
        'id': 'usercomment',
        'rows': '4'}),
        }

    def save(self, *args, **kwargs):
        Comments.objects.rebuild()
        return super(NewCommentForm, self).save(*args, **kwargs)