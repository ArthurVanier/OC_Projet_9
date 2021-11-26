from django import forms
from django.forms import Textarea


class login_form(forms.Form):
    username = forms.CharField(max_length=26)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=26)


class sign_up_form(forms.Form):
    username = forms.CharField(max_length=26)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=26)
    email = forms.EmailField()


class ticket_form(forms.Form):
    title = forms.CharField()
    description = forms.CharField(max_length=128, widget=Textarea(attrs={'cols': 80, 'rows': 10}))
    image = forms.ImageField(error_messages={'required': ''})


CHOICES = (('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5))


class review_form(forms.Form):
    title = forms.CharField(max_length=128)
    description = forms.CharField(max_length=2048)
    image = forms.ImageField(label='background image', required=False)

    headline = forms.CharField(max_length=128)
    body = forms.CharField(max_length=8192, widget=Textarea(attrs={'cols': 80, 'rows': 10}))
    rating = forms.ChoiceField(widget=forms.RadioSelect(), choices=CHOICES)

    def __init__(self, is_read_only=False, *args, **kwargs):
        super(review_form, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = is_read_only
        self.fields['description'].widget.attrs['readonly'] = is_read_only
        self.fields['image'].widget.attrs['readonly'] = is_read_only


class review_to_ticket_form(forms.Form):
    headline = forms.CharField(max_length=128)
    body = forms.CharField(max_length=8192, widget=Textarea(attrs={'cols': 80, 'rows': 10}))
    rating = forms.ChoiceField(widget=forms.RadioSelect(), choices=CHOICES)


class subscription_form(forms.Form):
    username = forms.CharField(max_length=26)
