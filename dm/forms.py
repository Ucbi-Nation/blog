from django import forms

class ChannelMessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"id": "message-to-send","placeholder":"Type your message", "rows": 3, "cols": 10}))