#!/usr/bin/env python3
"""
Script de correction automatique pour BudgetManage
Version améliorée qui corrige toutes les incohérences identifiées
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BudgetManageCorrector:
    """Classe pour appliquer automatiquement toutes les corrections"""
    
    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()
        self.backup_dir = self.project_path / f"backup_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.success_count = 0
        self.error_count = 0
        self.corrections_applied = []
        
    def log(self, message, level="INFO"):
        """Logger avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        if level == "ERROR":
            logger.error(message)
        else:
            logger.info(message)
    
    def create_backup(self):
        """Créer une sauvegarde complète avant corrections"""
        try:
            self.log("🔄 Création de la sauvegarde...")
            
            self.backup_dir.mkdir(exist_ok=True)
            
            # Fichiers critiques à sauvegarder
            critical_files = [
                "main.py",
                "models/database.py",
                "controllers/auth_controller.py",
                "services/permission_service.py",
                "utils/session_manager.py",
                "utils/validators.py",
                "requirements.txt",
                "config/settings.py"
            ]
            
            # Sauvegarde base de données
            db_path = self.project_path / "budget_workflow.db"
            if db_path.exists():
                shutil.copy2(db_path, self.backup_dir / "budget_workflow.db")
                self.log("✅ Base de données sauvegardée")
            
            # Sauvegarde fichiers critiques
            for file_path in critical_files:
                src = self.project_path / file_path
                if src.exists():
                    dst = self.backup_dir / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    self.log(f"✅ {file_path} sauvegardé")
            
            self.log(f"🎉 Sauvegarde créée dans: {self.backup_dir}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde: {e}", "ERROR")
            return False
    
    def fix_permission_service(self):
        """Corriger le service de permissions"""
        try:
            self.log("🔄 Correction du PermissionService...")
            
            # Copier le fichier corrigé vers l'emplacement final
            corrected_file = self.project_path / "services" / "permission_service_corrected.py"
            target_file = self.project_path / "services" / "permission_service.py"
            
            if corrected_file.exists():
                shutil.copy2(corrected_file, target_file)
                self.log("✅ PermissionService corrigé")
                self.success_count += 1
                self.corrections_applied.append("PermissionService compatible")
                return True
            else:
                self.log("❌ Fichier de correction permission_service_corrected.py non trouvé", "ERROR")
                self.error_count += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur correction PermissionService: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def fix_session_manager(self):
        """Corriger le gestionnaire de session"""
        try:
            self.log("🔄 Correction du SessionManager...")
            
            corrected_file = self.project_path / "utils" / "session_manager_corrected.py"
            target_file = self.project_path / "utils" / "session_manager.py"
            
            if corrected_file.exists():
                shutil.copy2(corrected_file, target_file)
                self.log("✅ SessionManager corrigé")
                self.success_count += 1
                self.corrections_applied.append("SessionManager fonctionnel")
                return True
            else:
                self.log("❌ Fichier de correction session_manager_corrected.py non trouvé", "ERROR")
                self.error_count += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur correction SessionManager: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def fix_validators(self):
        """Corriger les validateurs"""
        try:
            self.log("🔄 Correction des Validators...")
            
            corrected_file = self.project_path / "utils" / "validators_corrected.py"
            target_file = self.project_path / "utils" / "validators.py"
            
            if corrected_file.exists():
                shutil.copy2(corrected_file, target_file)
                self.log("✅ Validators corrigés")
                self.success_count += 1
                self.corrections_applied.append("Validation mot de passe robuste")
                return True
            else:
                self.log("❌ Fichier de correction validators_corrected.py non trouvé", "ERROR")
                self.error_count += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur correction Validators: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def fix_requirements(self):
        """Corriger le fichier requirements.txt"""
        try:
            self.log("🔄 Correction du requirements.txt...")
            
            corrected_requirements = """# Core dependencies
streamlit==1.28.1
pandas==2.1.4
bcrypt==4.1.2
plotly==5.17.0
openpyxl==3.1.2
python-dotenv==1.0.0

# Windows-specific (uncomment on Windows)
# pywin32==306

# Email dependencies
email-validator==2.1.0

# Development dependencies (optional)
# pytest==7.4.3
# black==23.11.0
# flake8==6.1.0
"""
            
            requirements_file = self.project_path / "requirements.txt"
            requirements_file.write_text(corrected_requirements)
            
            self.log("✅ Requirements.txt corrigé")
            self.success_count += 1
            self.corrections_applied.append("Dépendances fixées et cohérentes")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur correction requirements.txt: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def add_user_budget_model(self):
        """Ajouter le modèle UserBudget manquant"""
        try:
            self.log("🔄 Ajout du modèle UserBudget...")
            
            user_budget_file = self.project_path / "models" / "user_budget.py"
            
            if user_budget_file.exists():
                self.log("✅ Modèle UserBudget déjà présent")
                self.success_count += 1
                self.corrections_applied.append("Modèle UserBudget ajouté")
                return True
            else:
                self.log("❌ Fichier user_budget.py non trouvé dans models/", "ERROR")
                self.error_count += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur ajout UserBudget: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def fix_database_init(self):
        """Corriger l'initialisation de la base de données"""
        try:
            self.log("🔄 Correction de l'initialisation DB...")
            
            # Ajouter le script d'initialisation des dropdown si absent
            init_script = self.project_path / "init_dropdown_options.py"
            if not init_script.exists():
                init_code = '''#!/usr/bin/env python3
"""
Script d'initialisation des options de listes déroulantes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def init_dropdown_options():
    """Initialiser les options de listes déroulantes"""
    try:
        print("🔄 Initialisation des options de listes déroulantes...")
        
        # S'assurer que la base est initialisée
        db.init_database()
        
        # Vérifier si des options existent déjà
        existing_options = db.execute_query(
            "SELECT COUNT(*) as count FROM dropdown_options", 
            fetch='one'
        )
        
        if existing_options and existing_options['count'] > 0:
            print(f"✅ {existing_options['count']} options déjà présentes")
            return True
        
        # Options par défaut étendues
        default_options = [
            # Budgets
            ('budget', 'budget_commercial', 'Budget Commercial', 1),
            ('budget', 'budget_marketing', 'Budget Marketing', 2),
            ('budget', 'budget_formation', 'Budget Formation', 3),
            ('budget', 'budget_communication', 'Budget Communication', 4),
            ('budget', 'budget_developpement', 'Budget Développement', 5),
            
            # Catégories
            ('categorie', 'animation_commerciale', 'Animation Commerciale', 1),
            ('categorie', 'prospection', 'Prospection', 2),
            ('categorie', 'formation', 'Formation', 3),
            ('categorie', 'evenement', 'Événement', 4),
            ('categorie', 'communication', 'Communication', 5),
            
            # Typologies clients
            ('typologie_client', 'grand_compte', 'Grand Compte', 1),
            ('typologie_client', 'pme_eti', 'PME/ETI', 2),
            ('typologie_client', 'artisan', 'Artisan', 3),
            ('typologie_client', 'particulier', 'Particulier', 4),
            ('typologie_client', 'collectivite', 'Collectivité', 5),
            
            # Groupes/Groupements
            ('groupe_groupement', 'independant', 'Indépendant', 1),
            ('groupe_groupement', 'franchise', 'Franchise', 2),
            ('groupe_groupement', 'groupement', 'Groupement', 3),
            ('groupe_groupement', 'chaine', 'Chaîne', 4),
            ('groupe_groupement', 'cooperative', 'Coopérative', 5),
            
            # Régions françaises
            ('region', 'ile_de_france', 'Île-de-France', 1),
            ('region', 'auvergne_rhone_alpes', 'Auvergne-Rhône-Alpes', 2),
            ('region', 'hauts_de_france', 'Hauts-de-France', 3),
            ('region', 'nouvelle_aquitaine', 'Nouvelle-Aquitaine', 4),
            ('region', 'occitanie', 'Occitanie', 5),
            ('region', 'grand_est', 'Grand Est', 6),
            ('region', 'provence_alpes_cote_azur', 'Provence-Alpes-Côte d\\'Azur', 7),
            ('region', 'normandie', 'Normandie', 8),
            ('region', 'bretagne', 'Bretagne', 9),
            ('region', 'centre_val_de_loire', 'Centre-Val de Loire', 10),
            ('region', 'bourgogne_franche_comte', 'Bourgogne-Franche-Comté', 11),
            ('region', 'pays_de_la_loire', 'Pays de la Loire', 12),
        ]
        
        success_count = 0
        for category, value, label, order_index in default_options:
            try:
                db.execute_query(\\'''
                    INSERT OR IGNORE INTO dropdown_options (category, value, label, order_index)
                    VALUES (?, ?, ?, ?)
                \\''', (category, value, label, order_index))
                success_count += 1
            except Exception as e:
                print(f"Erreur insertion option {value}: {e}")
        
        print(f"✅ {success_count} options initialisées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation options: {e}")
        return False

if __name__ == "__main__":
    init_dropdown_options()
'''
                init_script.write_text(init_code)
                self.log("✅ Script d'initialisation dropdown créé")
            
            self.success_count += 1
            self.corrections_applied.append("Initialisation DB corrigée")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur correction DB init: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def test_corrections(self):
        """Tester que les corrections fonctionnent"""
        try:
            self.log("🧪 Tests des corrections appliquées...")
            
            # Ajouter le projet au path pour les imports
            sys.path.insert(0, str(self.project_path))
            
            # Test 1: Import PermissionService
            try:
                from services.permission_service import permission_service, Permission
                # Test basique
                assert hasattr(permission_service, 'has_permission')
                assert hasattr(Permission, 'CREATE_USER')
                self.log("✅ Test PermissionService: OK")
            except Exception as e:
                self.log(f"❌ Test PermissionService échoué: {e}", "ERROR")
                return False
            
            # Test 2: Import SessionManager
            try:
                from utils.session_manager import session_manager
                assert hasattr(session_manager, 'init_session')
                assert hasattr(session_manager, 'login_user')
                self.log("✅ Test SessionManager: OK")
            except Exception as e:
                self.log(f"❌ Test SessionManager échoué: {e}", "ERROR")
                return False
            
            # Test 3: Import Validators
            try:
                from utils.validators import validate_password, validate_email
                # Test validation mot de passe
                assert validate_password("Test123!") == True
                assert validate_password("faible") == False
                assert validate_email("test@example.com") == True
                self.log("✅ Test Validators: OK")
            except Exception as e:
                self.log(f"❌ Test Validators échoué: {e}", "ERROR")
                return False
            
            # Test 4: Import UserBudget
            try:
                from models.user_budget import UserBudgetModel
                assert hasattr(UserBudgetModel, 'create_budget')
                self.log("✅ Test UserBudget: OK")
            except Exception as e:
                self.log(f"❌ Test UserBudget échoué: {e}", "ERROR")
                return False
            
            # Test 5: Import Database
            try:
                from models.database import db
                assert hasattr(db, 'init_database')
                self.log("✅ Test Database: OK")
            except Exception as e:
                self.log(f"❌ Test Database échoué: {e}", "ERROR")
                return False
            
            self.log("🎉 Tous les tests réussis")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur tests: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def run_database_migration(self):
        """Exécuter les migrations de base de données"""
        try:
            self.log("🔄 Exécution des migrations DB...")
            
            sys.path.insert(0, str(self.project_path))
            from models.database import db
            
            # Initialiser la base avec toutes les tables
            db.init_database()
            
            # Vérifier que toutes les tables existent
            required_tables = [
                'users', 'user_budgets', 'demandes', 'demande_validations', 
                'demande_participants', 'notifications', 'activity_logs', 'dropdown_options'
            ]
            
            missing_tables = []
            for table in required_tables:
                if not db.table_exists(table):
                    missing_tables.append(table)
            
            if missing_tables:
                self.log(f"❌ Tables manquantes: {missing_tables}", "ERROR")
                self.error_count += 1
                return False
            
            self.log("✅ Migration DB réussie")
            self.success_count += 1
            self.corrections_applied.append("Base de données migrée")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur migration DB: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def initialize_dropdown_data(self):
        """Initialiser les données dropdown si nécessaire"""
        try:
            self.log("🔄 Initialisation des données dropdown...")
            
            # Exécuter le script d'initialisation
            init_script = self.project_path / "init_dropdown_options.py"
            if init_script.exists():
                # Importer et exécuter
                sys.path.insert(0, str(self.project_path))
                
                # Import dynamique du script
                import importlib.util
                spec = importlib.util.spec_from_file_location("init_dropdown", init_script)
                init_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(init_module)
                
                # Appeler la fonction d'initialisation
                result = init_module.init_dropdown_options()
                
                if result:
                    self.log("✅ Données dropdown initialisées")
                    self.success_count += 1
                    self.corrections_applied.append("Options dropdown initialisées")
                    return True
                else:
                    self.log("❌ Échec initialisation dropdown", "ERROR")
                    self.error_count += 1
                    return False
            else:
                self.log("❌ Script init_dropdown_options.py non trouvé", "ERROR")
                self.error_count += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur initialisation dropdown: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def cleanup_temp_files(self):
        """Nettoyer les fichiers temporaires"""
        try:
            self.log("🧹 Nettoyage des fichiers temporaires...")
            
            temp_files = [
                "services/permission_service_corrected.py",
                "utils/session_manager_corrected.py", 
                "utils/validators_corrected.py"
            ]
            
            for temp_file in temp_files:
                file_path = self.project_path / temp_file
                if file_path.exists():
                    file_path.unlink()
                    self.log(f"🗑️ Supprimé: {temp_file}")
            
            self.log("✅ Nettoyage terminé")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur nettoyage: {e}", "ERROR")
            return False
    
    def generate_summary(self):
        """Générer un résumé des corrections"""
        self.log("\n" + "="*60)
        self.log("📊 RÉSUMÉ DES CORRECTIONS APPLIQUÉES")
        self.log("="*60)
        
        self.log(f"✅ Corrections réussies: {self.success_count}")
        self.log(f"❌ Erreurs rencontrées: {self.error_count}")
        
        if self.corrections_applied:
            self.log("\n📋 Corrections appliquées:")
            for i, correction in enumerate(self.corrections_applied, 1):
                self.log(f"   {i}. {correction}")
        
        if self.error_count == 0:
            self.log("\n🎉 TOUTES LES CORRECTIONS ONT ÉTÉ APPLIQUÉES AVEC SUCCÈS!")
            
            self.log("\n🚀 PROCHAINES ÉTAPES:")
            self.log("   1. Redémarrer l'application: streamlit run main.py")
            self.log("   2. Se connecter avec: admin@budget.com / admin123")
            self.log("   3. Tester les nouvelles fonctionnalités")
            self.log("   4. Créer de nouveaux utilisateurs si nécessaire")
            
        else:
            self.log("\n⚠️ CERTAINES CORRECTIONS ONT ÉCHOUÉ")
            self.log("📋 Actions recommandées:")
            self.log("   1. Vérifier les logs d'erreur ci-dessus")
            self.log("   2. Corriger manuellement les problèmes")
            self.log("   3. Relancer le script si nécessaire")
            self.log(f"   4. Restaurer depuis le backup: {self.backup_dir}")
        
        self.log("="*60)
    
    def run(self):
        """Exécuter toutes les corrections"""
        self.log("🚀 DÉBUT DE L'APPLICATION DES CORRECTIONS BUDGETMANAGE")
        self.log("="*60)
        
        # Étape 1: Sauvegarde
        if not self.create_backup():
            self.log("❌ Arrêt: Échec de la sauvegarde", "ERROR")
            return False
        
        # Étape 2: Corrections des fichiers
        self.fix_permission_service()
        self.fix_session_manager()
        self.fix_validators()
        self.fix_requirements()
        self.add_user_budget_model()
        self.fix_database_init()
        
        # Étape 3: Migration base de données
        self.run_database_migration()
        
        # Étape 4: Initialisation données
        self.initialize_dropdown_data()
        
        # Étape 5: Tests
        self.test_corrections()
        
        # Étape 6: Nettoyage
        self.cleanup_temp_files()
        
        # Étape 7: Résumé
        self.generate_summary()
        
        return self.error_count == 0

def main():
    """Fonction principale"""
    print("🎯 Script de Correction Automatique BudgetManage v2.0")
    print("=" * 55)
    
    # Vérifier qu'on est dans le bon dossier
    if not Path("main.py").exists():
        print("❌ ERREUR: main.py non trouvé")
        print("   Exécutez ce script depuis le dossier racine de BudgetManage")
        return False
    
    # Demander confirmation
    response = input("\n⚠️  Ce script va modifier votre projet BudgetManage.\n"
                    "   Une sauvegarde sera créée automatiquement.\n"
                    "   Continuer? (o/N): ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Opération annulée par l'utilisateur")
        return False
    
    # Lancer les corrections
    corrector = BudgetManageCorrector()
    success = corrector.run()
    
    if success:
        print("\n🎉 CORRECTIONS APPLIQUÉES AVEC SUCCÈS!")
        print("   Vous pouvez maintenant redémarrer votre application.")
        print("   Commande: streamlit run main.py")
    else:
        print("\n❌ CERTAINES CORRECTIONS ONT ÉCHOUÉ")
        print("   Consultez les logs ci-dessus pour plus de détails.")
    
    return success

if __name__ == "__main__":
    main()
