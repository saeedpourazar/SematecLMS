from django import forms
from django.contrib.auth.models import User
from .models import Course, Instructor


class SignUpForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password'
            }
        )
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your password'
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your username'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your email'
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError(
                'Passwords do not match.'
            )

        return cleaned_data



class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = [
            'title',
            'description',
            'instructor',
            'categories',
            'duration',
            'price',
            'image',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'instructor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categories': forms.CheckboxSelectMultiple(),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }

class InstructorForm(forms.ModelForm):

    class Meta:
        model = Instructor
        fields = [
            'name',
            'family',
            'bio',
            'image',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'family': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }