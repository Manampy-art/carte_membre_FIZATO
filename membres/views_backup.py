from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Association, Membre, CarteMembre
from .forms import AssociationForm, MembreForm, SelectMembresForm

def dashboard(request):
    """Vue principale avec statistiques"""
    context = {
        'total_associations': Association.objects.count(),
        'total_membres': Membre.objects.count(),
        'total_cartes': CarteMembre.objects.count(),
        'cartes_imprimees': CarteMembre.objects.filter(est_imprimee=True).count(),
    }
    return render(request, 'membres/dashboard.html', context)

def liste_associations(request):
    """Liste des associations"""
    associations = Association.objects.all()
    return render(request, 'membres/liste_associations.html', {'associations': associations})

def ajouter_association(request):
    """Ajouter une nouvelle association"""
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Association ajoutée avec succès!')
            return redirect('liste_associations')
    else:
        form = AssociationForm()
    
    return render(request, 'membres/ajouter_association.html', {'form': form})

def modifier_association(request, association_id):
    """Modifier une association existante"""
    association = get_object_or_404(Association, pk=association_id)
    
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES, instance=association)
        if form.is_valid():
            form.save()
            messages.success(request, 'Association modifiée avec succès!')
            return redirect('liste_associations')
    else:
        form = AssociationForm(instance=association)
    
    return render(request, 'membres/ajouter_association.html', {
        'form': form, 
        'association': association, 
        'is_edit': True
    })

def supprimer_association(request, association_id):
    """Supprimer une association"""
    association = get_object_or_404(Association, pk=association_id)
    
    if request.method == 'POST':
        nom_association = association.nom
        association.delete()
        messages.success(request, f'Association {nom_association} supprimée avec succès!')
        return redirect('liste_associations')
    
    return render(request, 'membres/confirmer_suppression_association.html', {'association': association})

def liste_membres(request):
    """Liste des membres avec actions"""
    membres = Membre.objects.select_related('association').prefetch_related('carte')
    return render(request, 'membres/liste_membres.html', {'membres': membres})

def ajouter_membre(request):
    """Ajouter un nouveau membre"""
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre ajouté avec succès!')
            return redirect('liste_membres')
    else:
        form = MembreForm()
    
    return render(request, 'membres/ajouter_membre.html', {'form': form})

def modifier_membre(request, membre_id):
    """Modifier un membre existant"""
    membre = get_object_or_404(Membre, pk=membre_id)
    
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES, instance=membre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre modifié avec succès!')
            return redirect('liste_membres')
    else:
        form = MembreForm(instance=membre)
    
    return render(request, 'membres/ajouter_membre.html', {
        'form': form, 
        'membre': membre, 
        'is_edit': True
    })

def supprimer_membre(request, membre_id):
    """Supprimer un membre"""
    membre = get_object_or_404(Membre, pk=membre_id)
    
    if request.method == 'POST':
        nom_complet = f"{membre.prenom} {membre.nom}"
        membre.delete()
        messages.success(request, f'Membre {nom_complet} supprimé avec succès!')
        return redirect('liste_membres')
    
    return render(request, 'membres/confirmer_suppression.html', {'membre': membre})

def generer_cartes(request):
    """Sélectionner les membres pour générer leurs cartes"""
    if request.method == 'POST':
        form = SelectMembresForm(request.POST)
        if form.is_valid():
            membres_selectionnes = form.cleaned_data['membres']
            cartes_creees = 0
            
            for membre in membres_selectionnes:
                # Créer une carte si elle n'existe pas déjà
                carte, created = CarteMembre.objects.get_or_create(
                    membre=membre,
                    defaults={'est_imprimee': False}
                )
                if created:
                    cartes_creees += 1
            
            if cartes_creees > 0:
                messages.success(request, f'{cartes_creees} carte(s) membre(s) générée(s) avec succès!')
            else:
                messages.info(request, 'Tous les membres sélectionnés avaient déjà une carte.')
                
            return redirect('liste_cartes_membres')
    else:
        form = SelectMembresForm()
    
    return render(request, 'membres/generer_cartes.html', {'form': form})

def liste_cartes_membres(request):
    """Liste des membres ayant une carte"""
    cartes = CarteMembre.objects.select_related('membre__association').all()
    return render(request, 'membres/liste_cartes_membres.html', {'cartes': cartes})

def print_carte_membre(request, membre_id):
    """Imprimer la carte d'un membre spécifique"""
    return HttpResponse(f"Imprimer carte membre {membre_id}")
