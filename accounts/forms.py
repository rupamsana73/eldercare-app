from django import forms
from .models import Medicine, UserProfile, Prescription


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'frequency_type',
            'dose_per_day',
            'days_of_week',
            'duration_days',
            'end_date',
            'food_timing',
            'notes'
        ]


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    """
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'date_of_birth', 'emergency_note']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'type': 'tel'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'emergency_note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter emergency information',
                'rows': 4
            }),
        }


class UserProfilePhotoForm(forms.ModelForm):
    """
    Form for uploading user profile picture.
    """
    class Meta:
        model = UserProfile
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'profile-image-input'
            }),
        }


class PrescriptionUploadForm(forms.Form):
    """
    Form for uploading prescription images.
    Validates file type and size.
    """
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'accept': 'image/jpeg,image/png,image/jpg',
            'id': 'prescription-file-input',
        }),
        help_text='Upload a prescription image (JPG or PNG, max 10 MB).'
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (10 MB limit)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10 MB.')
            # Check file extension
            ext = image.name.rsplit('.', 1)[-1].lower() if '.' in image.name else ''
            if ext not in ('jpg', 'jpeg', 'png'):
                raise forms.ValidationError('Only JPG and PNG files are supported.')
        return image


class PrescriptionMedicineForm(forms.Form):
    """
    Dynamic form for adding medicines from prescription with dosage details.
    """
    medicine_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Medicine name',
        })
    )
    
    dose_per_day = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doses per day',
        })
    )
    
    frequency_type = forms.ChoiceField(
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly (specific days)'),
            ('custom_week', 'Custom days'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    food_timing = forms.ChoiceField(
        choices=[
            ('Before Food', 'Before Food'),
            ('After Food', 'After Food'),
        ],
        initial='After Food',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    duration_days = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Duration in days (optional)',
        })
    )
    
    times_per_day = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 8:00 AM, 2:00 PM, 8:00 PM (comma-separated)',
            'type': 'text'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Additional notes (optional)',
            'rows': 2
        })
    )


class PrescriptionConfirmForm(forms.Form):
    """
    Form for confirming detected medicines from prescription.
    User selects which medicines to add.
    """
    medicines = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    # JSON string of selected medicines with their details
    selected_medicines = forms.CharField(
        widget=forms.HiddenInput()
    )

