from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Comment, Publication, User


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "password"):
            self.fields[name].widget.attrs.update(
                {"class": "form-control", "autocomplete": "username" if name == "username" else "current-password"}
            )


class CitizenRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ in ("TextInput", "EmailInput", "PasswordInput"):
                field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.ROLE_CITIZEN
        if commit:
            user.save()
        return user


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ("title", "content", "image", "is_published")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 12, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {"is_published": "Visible sur le site"}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Votre message… Utilisez @nom_utilisateur pour mentionner quelqu'un.",
                    "autocomplete": "off",
                }
            ),
        }
