from django import forms
from django.core.exceptions import ValidationError
from .models import Association, Membre, CarteMembre, InfoFizato, FonctionBureau, MembreBureau, Mandat, ComiteDoyen

class AssociationForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['nom', 'logo_association', 'logo_universite', 'devise', 'fondateurs', 'description', 'date_creation']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'association'
            }),
            'devise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Devise de l\'association'
            }),
            'fondateurs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Séparez les noms par des virgules'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de l\'association'
            }),
            'date_creation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'logo_association': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'logo_universite': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class MembreForm(forms.ModelForm):
    date_naissance = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    etablissement = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom de l\'établissement'
    }))
    adresse = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Adresse ou Cité universitaire'
    }))
    telephone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Téléphone'
    }))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    nom_facebook = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom Facebook'
    }))

    def __init__(self, *args, **kwargs):
        association_id = kwargs.pop('association_id', None)
        super().__init__(*args, **kwargs)
        
        # Si association_id est fourni, limiter le choix à cette association
        if association_id:
            try:
                association = Association.objects.get(id=association_id)
                self.fields['association'].queryset = Association.objects.filter(id=association_id)
                self.fields['association'].initial = association
                self.fields['association'].widget = forms.HiddenInput()
            except Association.DoesNotExist:
                pass
        
        # S'assurer que les champs obligatoires le restent
        self.fields['association'].required = True
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['numero_cin'].required = True
        self.fields['filiere'].required = True
        self.fields['parcours'].required = True
        
        # Les champs optionnels
        self.fields['date_naissance'].required = False
        self.fields['etablissement'].required = False
        self.fields['adresse'].required = False
        self.fields['telephone'].required = False
        self.fields['email'].required = False
        self.fields['nom_facebook'].required = False
        self.fields['photo'].required = False

    class Meta:
        model = Membre
        fields = ['association', 'nom', 'prenom', 'numero_cin', 
                 'filiere', 'parcours', 'photo', 'date_naissance', 'etablissement', 'adresse', 'telephone', 'email', 'nom_facebook']
        widgets = {
            'association': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du membre'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du membre'
            }),
            'numero_cin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro CIN'
            }),
            'filiere': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Filière d\'études'
            }),
            'parcours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parcours'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_date_debut(self):
        date_debut = self.cleaned_data.get('date_debut')
        if not date_debut:
            # Si la date n'est pas fournie, utiliser le début de l'année scolaire
            from datetime import datetime, date
            current_year = datetime.now().year
            date_debut = date(current_year, 9, 1)  # 1er septembre
        return date_debut

    def clean_date_fin(self):
        date_debut = self.cleaned_data.get('date_debut')
        date_fin = self.cleaned_data.get('date_fin')
        
        if not date_fin:
            # Si la date n'est pas fournie, utiliser la fin de l'année scolaire
            from datetime import datetime, date
            current_year = datetime.now().year
            date_fin = date(current_year + 1, 8, 31)  # 31 août
        
        if date_debut and date_fin:
            if date_fin <= date_debut:
                raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        return date_fin

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        # Double vérification : si les dates sont toujours None, les assigner
        from datetime import datetime, date
        current_year = datetime.now().year
        
        if not date_debut:
            cleaned_data['date_debut'] = date(current_year, 9, 1)
        if not date_fin:
            cleaned_data['date_fin'] = date(current_year + 1, 8, 31)
            
        return cleaned_data

class MembreAutoEditForm(forms.ModelForm):
    """Formulaire pour permettre aux membres de modifier leurs propres informations"""
    date_naissance = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    etablissement = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom de l\'établissement'
    }))
    adresse = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Adresse ou Cité universitaire'
    }))
    telephone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Téléphone'
    }))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    nom_facebook = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom Facebook'
    }))

    class Meta:
        model = Membre
        # Exclure association et numero_carte - ces champs ne peuvent pas être modifiés par l'utilisateur
        fields = ['nom', 'prenom', 'numero_cin', 'filiere', 'parcours', 'photo', 
                 'date_naissance', 'etablissement', 'adresse', 'telephone', 'email', 'nom_facebook']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du membre'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du membre'
            }),
            'numero_cin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro CIN'
            }),
            'filiere': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Filière d\'études'
            }),
            'parcours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parcours'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tous les champs de base restent requis sauf les champs optionnels
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['numero_cin'].required = True
        self.fields['filiere'].required = True
        self.fields['parcours'].required = True
        
        # Les champs optionnels
        self.fields['date_naissance'].required = False
        self.fields['etablissement'].required = False
        self.fields['adresse'].required = False
        self.fields['telephone'].required = False
        self.fields['email'].required = False
        self.fields['nom_facebook'].required = False
        self.fields['photo'].required = False

class GenerationCarteForm(forms.Form):
    membres = forms.ModelMultipleChoiceField(
        queryset=Membre.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=True,
        label="Sélectionner les membres"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ne montrer que les membres qui n'ont pas encore de carte
        self.fields['membres'].queryset = Membre.objects.filter(carte__isnull=True)


class InfoFizatoForm(forms.ModelForm):
    class Meta:
        model = InfoFizato
        fields = ['nom', 'nom_complet', 'date_creation', 'devise', 'fondateurs', 'description', 'logo']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'organisation'
            }),
            'nom_complet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet de l\'organisation'
            }),
            'date_creation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'devise': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Devise de l\'organisation'
            }),
            'fondateurs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Séparez les noms par des virgules'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Description de l\'organisation'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class FonctionBureauForm(forms.ModelForm):
    class Meta:
        model = FonctionBureau
        fields = ['nom', 'niveau_hierarchique', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la fonction (ex: Président, Secrétaire...)'
            }),
            'niveau_hierarchique': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '1 = Président, 2 = Vice-président, etc.'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la fonction'
            }),
        }


class MembreBureauForm(forms.ModelForm):
    class Meta:
        model = MembreBureau
        fields = ['membre', 'fonction', 'date_debut', 'date_fin', 'est_actuel']
        widgets = {
            'membre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fonction': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'est_actuel': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordonner les membres par nom
        self.fields['membre'].queryset = Membre.objects.all().order_by('nom', 'prenom')
        # Ordonner les fonctions par niveau hiérarchique
        self.fields['fonction'].queryset = FonctionBureau.objects.all().order_by('niveau_hierarchique', 'nom')


class MandatForm(forms.ModelForm):
    motif_fin = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Motif de la fin du mandat'
        }),
        label='Motif de fin'
    )
    
    class Meta:
        model = Mandat
        fields = ['nom', 'date_debut', 'date_fin', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mandat 2024-2026'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on est en mode édition/terminaison, rendre date_fin obligatoire
        if self.instance.pk:
            self.fields['date_fin'].required = True
            self.fields['motif_fin'].required = True


class CreerMandatForm(forms.ModelForm):
    """Formulaire pour créer un nouveau mandat (sans date de fin)"""
    
    class Meta:
        model = Mandat
        fields = ['nom', 'date_debut', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mandat 2024-2026'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du mandat'}),
        }
        labels = {
            'nom': 'Nom du mandat',
            'date_debut': 'Date de début',
            'description': 'Description'
        }


class ComiteDoyenForm(forms.ModelForm):
    class Meta:
        model = ComiteDoyen
        fields = ['membre', 'titre', 'date_nomination', 'ordre_affichage']
        widgets = {
            'membre': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_nomination': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ordre_affichage': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
