from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile, Report, CustomUser

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    telephone = forms.CharField(max_length=10, required=False)
    adresse = forms.CharField(max_length=255, required=False)
    date_de_naissance = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 
                 'adresse', 'date_de_naissance', 'profile_picture', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        max_length=500
    )
    location = forms.CharField(max_length=100, required=False)
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des labels
        self.fields['bio'].label = 'Biographie'
        self.fields['location'].label = 'Localisation'
        self.fields['birth_date'].label = 'Date de naissance'
        self.fields['avatar'].label = 'Photo de profil'

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].label = 'Type de signalement'
        self.fields['description'].label = 'Description'

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'date_de_naissance', 'profile_picture']
        widgets = {
            'date_de_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des labels
        self.fields['first_name'].label = 'Prénom'
        self.fields['last_name'].label = 'Nom'
        self.fields['email'].label = 'Email'
        self.fields['telephone'].label = 'Téléphone'
        self.fields['adresse'].label = 'Adresse'
        self.fields['date_de_naissance'].label = 'Date de naissance'
        self.fields['profile_picture'].label = 'Photo de profil' 