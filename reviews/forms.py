from django import forms
from django.forms import ModelForm
from .widgets import RadioSelectModified
from django.contrib.auth import get_user_model

from .models import Review, Salary, Interview, Company, Profile, Position


class CompanySearchForm(forms.Form):
    company_name = forms.CharField(label="Wyszukaj firmę", max_length=100)

    
class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'headquarters_city', 'website']

    def clean_website(self):
        """Clean field: 'website', ensure that urls with http, https, 
        with and without www are treated as same."""
        url = self.cleaned_data['website']
        if url.startswith('https'):
            url = url.replace('https', 'http')
        if not url.startswith('http://www.'):
            url = url.replace('http://', 'http://www.')
        # TODO check here if the website returns 200
        return url

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position', 'department', 'location', 
                  'start_date_year', 'start_date_month', 'employment_status']

        labels = {
            'position': 'stanowisko',
            'department': 'departament',
            'location': 'miasto',
            'start_date_year': 'rok',
            'start_date_month': 'miesiąc',
            'employment_status': 'rodzaj umowy',
            }

        widgets = {
            'start_date_year': forms.Select(attrs={'class':'inline'}),
            'start_date_month': forms.Select(attrs={'class':'inline'}),
            }
        
        """
        help_texts = {
            'start_date_year': 'rok',
            'start_date_month': 'miesiąc',
            }
        """
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'advancement',
                  'worklife', 'compensation', 'environment', 'overallscore',
                  'pros', 'cons', 'comment']

        labels = {
            'title': 'tytuł recenzji',
            'advancement': 'możliwości rozwoju',
            'worklife': 'równowaga praca/życie',
            'compensation': 'zarobki',
            'environment': 'atmosfera w pracy',
            'pros': 'zalety',
            'cons': 'wady',
            'ovarallscore': 'ocena ogólna',
            'comment': 'co należy zmienić?',
        }

        widgets = {
            'advancement': RadioSelectModified(),
            'worklife': RadioSelectModified(),
            'compensation': RadioSelectModified(),
            'environment': RadioSelectModified(),
            'overallscore': RadioSelectModified(),
            'pros': forms.Textarea(),
            'cons': forms.Textarea(),
            'comment': forms.Textarea(),
        }

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            'currency',
            'salary_input',
            'period',
            'gross_net',
            'bonus_input',
            'bonus_period',
            'bonus_gross_net',
        ]
        widgets = {
            'currency': forms.TextInput(attrs={'size': 3}),
            'salary_input': forms.NumberInput(attrs={'step': 100, 'value': 1500,
                                                     'class': 'inline'}),
            'period': forms.Select(attrs={'class': 'inline'}),
            'gross_net': forms.Select(attrs={'class': 'inline'}),
            
            'bonus_input': forms.NumberInput(attrs={'step': 1000, 'class': 'inline'}),
            'bonus_period': forms.Select(attrs={'class': 'inline'}),
            'bonus_gross_net': forms.Select(attrs={'class': 'inline'}),
            }
        

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'position',
            'department',
            'how_got',
            'difficulty',
            'got_offer',
            'questions',
            'impressions'
        ]

        widgets = {
            'difficulty': forms.RadioSelect(),
            'impressions': forms.Textarea(),
            'got_offer': forms.RadioSelect(),
            }

        help_texts = {
            'difficulty': '1 - bardzo łatwo, 5 - bardzo trudno',
            }

class CreateProfileForm_user(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

class CreateProfileForm_profile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['sex', 'career_start_year']

        widgets = {
            'sex': forms.RadioSelect()
            }
