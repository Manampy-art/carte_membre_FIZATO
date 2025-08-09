from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Créer un utilisateur administrateur pour FIZATO'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nom d\'utilisateur')
        parser.add_argument('--email', type=str, help='Email de l\'administrateur')
        parser.add_argument('--password', type=str, help='Mot de passe')
        parser.add_argument('--firstname', type=str, help='Prénom')
        parser.add_argument('--lastname', type=str, help='Nom de famille')

    def handle(self, *args, **options):
        # Demander les informations si non fournies
        username = options['username'] or input('Nom d\'utilisateur: ')
        email = options['email'] or input('Email: ')
        first_name = options['firstname'] or input('Prénom: ')
        last_name = options['lastname'] or input('Nom de famille: ')
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'L\'utilisateur "{username}" existe déjà!')
            )
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Un utilisateur avec l\'email "{email}" existe déjà!')
            )
            return

        # Mot de passe
        if options['password']:
            password = options['password']
        else:
            import getpass
            password = getpass.getpass('Mot de passe: ')
            password_confirm = getpass.getpass('Confirmer le mot de passe: ')
            
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Les mots de passe ne correspondent pas!')
                )
                return

        try:
            # Créer l'utilisateur administrateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,  # Accès à l'admin Django
                is_superuser=False  # Pas de superuser par défaut
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Administrateur "{username}" créé avec succès!\n'
                    f'Email: {email}\n'
                    f'Nom complet: {first_name} {last_name}\n'
                    f'Permissions: Staff (peut gérer les membres et associations)'
                )
            )
            
            # Instructions pour l'utilisation
            self.stdout.write(
                self.style.WARNING(
                    '\n=== Instructions ===\n'
                    '1. Connectez-vous avec ces identifiants\n'
                    '2. Vous pouvez maintenant:\n'
                    '   - Ajouter des associations\n'
                    '   - Ajouter des membres\n'
                    '   - Générer des cartes\n'
                    '   - Gérer les utilisateurs via l\'admin Django\n'
                    f'3. URL d\'administration: http://127.0.0.1:8000/admin/\n'
                    f'4. URL de l\'application: http://127.0.0.1:8000/'
                )
            )
            
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur de validation: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la création: {e}')
            )
