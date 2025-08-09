# Guide d'ajout du Logo FI.ZA.TO

## Comment ajouter le logo FI.ZA.TO dans l'interface d'administration

### Étapes à suivre :

1. **Accédez à l'interface d'administration Django**
   - Ouvrez votre navigateur et allez sur `http://localhost:8000/admin/`
   - Connectez-vous avec vos identifiants administrateur

2. **Naviguez vers les Associations**
   - Cliquez sur "Associations" dans la section "MEMBRES"
   - Sélectionnez l'association pour laquelle vous voulez ajouter le logo FI.ZA.TO

3. **Ajoutez le logo dans la section "Logos"**
   - Faites défiler jusqu'à la section "Logos"
   - Vous verrez maintenant trois champs :
     - Logo Association
     - Logo Université  
     - **Logo FI.ZA.TO** (nouveau champ ajouté)

4. **Uploadez votre logo FI.ZA.TO**
   - Cliquez sur "Choisir le fichier" à côté de "Logo FI.ZA.TO"
   - Sélectionnez votre fichier image (PNG, JPG, etc.)
   - Le logo sera automatiquement stocké dans `media/logos/fizato/`

5. **Sauvegardez les modifications**
   - Cliquez sur "Enregistrer" en bas de la page

### Résultat sur la carte membre :

Une fois le logo ajouté, il apparaîtra automatiquement sur la carte membre dans la section droite, en bas, sous la devise.

Le logo FI.ZA.TO a un design spécial avec :
- Fond coloré avec la couleur de thème FI.ZA.TO (bleu-vert)
- Bordure avec effet glassmorphism
- Taille adaptée au format carte (16px x 16px)
- Icône de fallback si aucun logo n'est uploadé

### Spécifications techniques du logo :

- **Format recommandé** : PNG avec transparence ou JPG
- **Taille recommandée** : 200x200px minimum
- **Ratio** : 1:1 (carré)
- **Couleurs** : Préférablement sur fond transparent
- **Poids** : Maximum 2MB

### Note importante :

Le logo FI.ZA.TO représente l'association mère de toutes les associations. Il sera affiché sur toutes les cartes membres pour identifier l'organisation principale, en complément du logo de l'université et de la devise.
