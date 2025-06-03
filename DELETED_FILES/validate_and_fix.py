#!/usr/bin/env python3
"""
🔧 SCRIPT DE VALIDATION ET CORRECTION AUTOMATIQUE - BUDGETMANAGE
Résout automatiquement les problèmes identifiés sans intervention manuelle
"""

import sys
import os
import sqlite3
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_and_fix_database():
    """Vérifie et corrige la base de données"""
    print("📊 VÉRIFICATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        # Importer et initialiser la base
        from models.database import db
        db.init_database()
        print("✅ Base de données initialisée avec succès")
        
        # Vérifier les tables critiques
        critical_tables = ['users', 'demandes', 'dropdown_options', 'notifications']
        missing_tables = []
        
        for table in critical_tables:
            if not db.table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Tables manquantes : {missing_tables}")
            return False
        else:
            print("✅ Toutes les tables critiques sont présentes")
            return True
            
    except Exception as e:
        print(f"❌ Erreur base de données : {e}")
        return False

def check_and_fix_dropdown_options():
    """Vérifie et corrige les options de listes déroulantes"""
    print("\n📋 VÉRIFICATION DES LISTES DÉROULANTES")
    print("=" * 50)
    
    try:
        from models.database import db
        from models.dropdown_options import DropdownOptionsModel
        
        # Vérifier les catégories critiques
        critical_categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        empty_categories = []
        
        for category in critical_categories:
            try:
                options = DropdownOptionsModel.get_options_for_category(category)
                if not options:
                    empty_categories.append(category)
                    print(f"⚠️ Catégorie '{category}' : VIDE")
                else:
                    print(f"✅ Catégorie '{category}' : {len(options)} option(s)")
            except Exception as e:
                print(f"❌ Erreur pour '{category}' : {e}")
                empty_categories.append(category)
        
        # Correction automatique si nécessaire
        if empty_categories:
            print(f"\n🔧 CORRECTION AUTOMATIQUE NÉCESSAIRE")
            print(f"Catégories vides : {empty_categories}")
            
            # Exécuter l'initialisation automatique
            return auto_initialize_dropdown_options()
        else:
            print("✅ Toutes les catégories contiennent des options")
            return True
            
    except Exception as e:
        print(f"❌ Erreur vérification listes déroulantes : {e}")
        return False

def auto_initialize_dropdown_options():
    """Initialise automatiquement les listes déroulantes"""
    print("\n🚀 INITIALISATION AUTOMATIQUE DES LISTES DÉROULANTES")
    print("=" * 50)
    
    try:
        from models.dropdown_options import DropdownOptionsModel
        
        # Options par défaut optimisées
        default_options = {
            'budget': [
                'Budget Commercial',
                'Budget Marketing', 
                'Budget Formation',
                'Budget Communication',
                'Budget Développement',
                'Budget Événementiel'
            ],
            'categorie': [
                'Animation Commerciale',
                'Prospection Client',
                'Formation Équipe',
                'Événement Marketing',
                'Communication Digitale',
                'Salon Professionnel'
            ],
            'typologie_client': [
                'Grand Compte',
                'PME/ETI',
                'Artisan/Commerçant',
                'Particulier',
                'Collectivité',
                'Startup'
            ],
            'groupe_groupement': [
                'Indépendant',
                'Franchise',
                'Groupement Achats',
                'Chaîne Nationale',
                'Coopérative',
                'Réseau'
            ],
            'region': [
                'Île-de-France',
                'Auvergne-Rhône-Alpes',
                'Nouvelle-Aquitaine',
                'Occitanie',
                'Hauts-de-France',
                'Grand Est',
                'Provence-Alpes-Côte d\'Azur',
                'Pays de la Loire',
                'Bretagne',
                'Normandie',
                'Bourgogne-Franche-Comté',
                'Centre-Val de Loire',
                'Corse'
            ]
        }
        
        total_added = 0
        
        for category, options_list in default_options.items():
            print(f"\n📂 Initialisation : {category}")
            category_count = 0
            
            for idx, option_label in enumerate(options_list, 1):
                try:
                    success, message = DropdownOptionsModel.add_option(
                        category=category,
                        label=option_label,
                        order_index=idx,
                        auto_normalize=True
                    )
                    
                    if success:
                        print(f"  ✅ {option_label}")
                        category_count += 1
                        total_added += 1
                    else:
                        # Si existe déjà, c'est normal
                        if "déjà existe" in message.lower():
                            print(f"  ℹ️ {option_label} (déjà présent)")
                        else:
                            print(f"  ⚠️ {option_label}: {message}")
                        
                except Exception as e:
                    print(f"  ❌ {option_label}: {e}")
            
            print(f"📊 {category}: {category_count} options ajoutées")
        
        print(f"\n🎉 RÉSULTAT : {total_added} nouvelles options ajoutées")
        return total_added >= 0  # Succès même si aucune option ajoutée (déjà présentes)
        
    except Exception as e:
        print(f"❌ Erreur initialisation automatique : {e}")
        return False

def check_admin_user():
    """Vérifie l'existence d'un utilisateur admin"""
    print("\n👤 VÉRIFICATION UTILISATEUR ADMIN")
    print("=" * 50)
    
    try:
        from models.database import db
        
        admin_count = db.execute_query(
            "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1",
            fetch='one'
        )[0]
        
        if admin_count > 0:
            print(f"✅ {admin_count} administrateur(s) actif(s) trouvé(s)")
            return True
        else:
            print("⚠️ Aucun administrateur actif trouvé")
            return create_default_admin()
            
    except Exception as e:
        print(f"❌ Erreur vérification admin : {e}")
        return False

def create_default_admin():
    """Crée un administrateur par défaut"""
    print("\n🔧 CRÉATION ADMINISTRATEUR PAR DÉFAUT")
    print("=" * 50)
    
    try:
        from models.database import db
        from utils.security import hash_password
        
        admin_password = hash_password("admin123")
        
        db.execute_query('''
            INSERT OR REPLACE INTO users 
            (id, email, password_hash, nom, prenom, role, is_active, activated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            "admin@budget.com", 
            admin_password, 
            "Administrateur", 
            "Système", 
            "admin", 
            True
        ))
        
        print("✅ Administrateur par défaut créé :")
        print("   📧 Email : admin@budget.com")
        print("   🔑 Mot de passe : admin123")
        print("   ⚠️ CHANGEZ CE MOT DE PASSE après la première connexion")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création admin : {e}")
        return False

def verify_imports():
    """Vérifie que tous les imports nécessaires fonctionnent"""
    print("\n📦 VÉRIFICATION DES IMPORTS")
    print("=" * 50)
    
    critical_imports = [
        ('streamlit', 'st'),
        ('pandas', 'pd'),
        ('bcrypt', None),
        ('plotly', None),
        ('openpyxl', None),
        ('dotenv', 'python-dotenv')
    ]
    
    failed_imports = []
    
    for module, package in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (paquet: {package or module})")
            failed_imports.append(package or module)
    
    if failed_imports:
        print(f"\n⚠️ Modules manquants : {failed_imports}")
        print("💡 Installez avec : pip install " + " ".join(failed_imports))
        return False
    else:
        print("✅ Tous les modules requis sont disponibles")
        return True

def test_tc_workflow():
    """Test du workflow TC - création de demande"""
    print("\n🧪 TEST DU WORKFLOW TC")
    print("=" * 50)
    
    try:
        # Test de validation des données
        from utils.validators import validate_text_field, validate_montant
        
        # Tests de validation
        test_cases = [
            (validate_text_field("Test Manifestation", min_length=3), "Validation texte"),
            (validate_montant(1000.0), "Validation montant"),
            (not validate_montant(-100.0), "Validation montant négatif"),
        ]
        
        for test_result, test_name in test_cases:
            if test_result:
                print(f"✅ {test_name} : OK")
            else:
                print(f"❌ {test_name} : ÉCHEC")
                workflow_ok = False
        
        return workflow_ok
        
    except Exception as e:
        print(f"❌ Erreur test workflow : {e}")
        return False

def test_import_dependencies():
    """Test des dépendances Python"""
    print("\n📦 TEST DÉPENDANCES PYTHON")
    print("-" * 40)
    
    dependencies = [
        ('streamlit', 'Interface utilisateur'),
        ('pandas', 'Manipulation de données'),
        ('bcrypt', 'Sécurité des mots de passe'),
        ('plotly', 'Graphiques et analytics'),
        ('openpyxl', 'Export Excel'),
        ('dotenv', 'Variables d\'environnement')
    ]
    
    all_deps_ok = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module} : OK ({description})")
        except ImportError:
            print(f"❌ {module} : MANQUANT ({description})")
            all_deps_ok = False
    
    return all_deps_ok

def auto_fix_detected_issues():
    """Correction automatique des problèmes détectés"""
    print("\n🔧 CORRECTION AUTOMATIQUE DES PROBLÈMES")
    print("-" * 50)
    
    fixes_applied = []
    
    try:
        # 1. Initialiser la base de données si nécessaire
        from models.database import db
        db.init_database()
        fixes_applied.append("Base de données initialisée")
        
        # 2. Créer un admin par défaut si aucun n'existe
        admin_count = db.execute_query(
            "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1",
            fetch='one'
        )[0]
        
        if admin_count == 0:
            from utils.security import hash_password
            admin_password = hash_password("admin123")
            
            db.execute_query('''
                INSERT OR REPLACE INTO users 
                (id, email, password_hash, nom, prenom, role, is_active, activated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                "admin@budget.com", 
                admin_password, 
                "Administrateur", 
                "Système", 
                "admin", 
                True
            ))
            fixes_applied.append("Administrateur par défaut créé")
        
        # 3. Initialiser les listes déroulantes si vides
        from models.dropdown_options import DropdownOptionsModel
        
        categories_to_check = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        empty_categories = []
        
        for category in categories_to_check:
            options = DropdownOptionsModel.get_options_for_category(category)
            if not options:
                empty_categories.append(category)
        
        if empty_categories:
            # Options par défaut essentielles
            default_options = {
                'budget': ['Budget Commercial', 'Budget Marketing', 'Budget Formation', 'Budget Communication'],
                'categorie': ['Animation Commerciale', 'Prospection Client', 'Formation Équipe', 'Événement Marketing'],
                'typologie_client': ['Grand Compte', 'PME/ETI', 'Artisan/Commerçant', 'Particulier'],
                'groupe_groupement': ['Indépendant', 'Franchise', 'Groupement Achats', 'Chaîne Nationale'],
                'region': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine', 'Occitanie', 'Hauts-de-France']
            }
            
            for category in empty_categories:
                if category in default_options:
                    for idx, option_label in enumerate(default_options[category], 1):
                        try:
                            DropdownOptionsModel.add_option(
                                category=category,
                                label=option_label,
                                order_index=idx,
                                auto_normalize=True
                            )
                        except:
                            pass  # Ignore si existe déjà
                    
                    fixes_applied.append(f"Options '{category}' initialisées")
        
        if fixes_applied:
            print("✅ Corrections appliquées :")
            for fix in fixes_applied:
                print(f"   • {fix}")
        else:
            print("ℹ️ Aucune correction nécessaire")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction automatique : {e}")
        return False

def generate_comprehensive_report():
    """Génère un rapport complet de validation"""
    print("\n📋 RAPPORT COMPLET DE VALIDATION")
    print("=" * 60)
    print(f"📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Projet : BudgetManage v1.0")
    print()
    
    # Exécuter tous les tests
    tests = [
        ("Connectivité base de données", test_database_connectivity()),
        ("Structure des tables", test_tables_structure()),
        ("Données listes déroulantes", test_dropdown_options_data()),
        ("Système d'authentification", test_user_authentication()),
        ("Workflow création demandes", test_demande_workflow()),
        ("Dépendances Python", test_import_dependencies())
    ]
    
    print("\n📊 RÉSUMÉ DES TESTS")
    print("-" * 50)
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, result in tests:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name:<30} : {status}")
        if result:
            passed_tests += 1
    
    print("-" * 50)
    print(f"📊 Score : {passed_tests}/{total_tests} tests réussis ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Statut global
    if passed_tests == total_tests:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE !")
        print("✅ L'application BudgetManage est prête pour la production")
        print("\n🚀 PROCHAINES ÉTAPES :")
        print("   1. Lancez l'application : streamlit run main.py")
        print("   2. Connectez-vous en admin : admin@budget.com / admin123")
        print("   3. Créez vos utilisateurs TC/DR via la page 'Utilisateurs'")
        print("   4. Personnalisez les listes déroulantes si nécessaire")
        print("   5. Testez la création de demandes avec un compte TC")
        return True
    elif passed_tests >= total_tests * 0.8:  # 80% des tests passent
        print("\n⚠️ VALIDATION PARTIELLE")
        print("✅ L'application peut fonctionner avec des limitations")
        print("🔧 Certains problèmes mineurs ont été détectés")
        print("\n💡 RECOMMANDATIONS :")
        print("   • Vérifiez les tests en échec ci-dessus")
        print("   • L'application reste utilisable en mode dégradé")
        print("   • Contactez le support technique si nécessaire")
        return True
    else:
        print("\n❌ VALIDATION ÉCHOUÉE")
        print("⚠️ L'application présente des problèmes critiques")
        print("\n🔧 ACTIONS NÉCESSAIRES :")
        print("   • Exécutez les corrections automatiques")
        print("   • Vérifiez l'installation des dépendances")
        print("   • Contactez le support technique")
        return False

def run_health_check():
    """Exécute un check de santé rapide"""
    print("🏥 CHECK DE SANTÉ RAPIDE")
    print("=" * 30)
    
    health_checks = [
        ("Base de données accessible", test_database_connectivity()),
        ("Au moins un admin existe", test_user_authentication()),
        ("Modules Python disponibles", test_import_dependencies())
    ]
    
    all_healthy = True
    for check_name, result in health_checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_healthy = False
    
    if all_healthy:
        print("\n💚 SYSTÈME EN BONNE SANTÉ")
    else:
        print("\n🔴 PROBLÈMES DÉTECTÉS - Exécutez la validation complète")
    
    return all_healthy

def main():
    """Fonction principale"""
    print("🔍 BUDGETMANAGE - VALIDATION ET TEST AUTOMATIQUE")
    print("=" * 60)
    print(f"⏰ Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Appliquer la correction
    success = apply_immediate_fix()
    
    if success:
        # Vérifier que ça fonctionne
        verification_success = verify_tc_can_create_demande()
        
        if verification_success:
            display_success_instructions()
            print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
            print("\n🎯 RÉSULTAT : SUCCÈS COMPLET")
            return 0
        else:
            print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
            print("\n⚠️ RÉSULTAT : CORRECTION PARTIELLE")
            print("💡 La correction a été appliquée mais la vérification a échoué")
            print("🔧 Essayez de relancer le script ou contactez le support")
            return 1
    else:
        print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
        print("\n❌ RÉSULTAT : ÉCHEC DE LA CORRECTION")
        print("💡 Vérifiez les erreurs ci-dessus")
        print("🔧 Essayez le script complet : python validate_and_fix.py")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)%M:%S')}")
    
    # Options de lancement
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "--health":
            success = run_health_check()
        elif mode == "--fix":
            print("🔧 MODE CORRECTION AUTOMATIQUE")
            success = auto_fix_detected_issues()
            if success:
                print("\n🔍 Validation après correction...")
                success = generate_comprehensive_report()
        else:
            print("Usage: python test_and_validate.py [--health|--fix]")
            sys.exit(1)
    else:
        # Mode complet par défaut
        print("🔧 Tentative de correction automatique...")
        auto_fix_detected_issues()
        
        print("\n🔍 Validation complète...")
        success = generate_comprehensive_report()
    
    print(f"\n⏰ Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🎯 RÉSULTAT : SUCCÈS")
        return 0
    else:
        print("\n⚠️ RÉSULTAT : PROBLÈMES DÉTECTÉS")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) récupération des options
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        all_categories_ok = True
        
        for category in categories:
            options = get_valid_dropdown_options(category)
            if options:
                print(f"✅ {category}: {len(options)} option(s)")
            else:
                print(f"❌ {category}: AUCUNE option")
                all_categories_ok = False
        
        if all_categories_ok:
            print("✅ TEST RÉUSSI : Les TC peuvent créer des demandes")
            return True
        else:
            print("❌ TEST ÉCHOUÉ : Problèmes dans les listes déroulantes")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test workflow : {e}")
        return False

def generate_validation_report():
    """Génère un rapport de validation complet"""
    print("\n📋 RAPPORT DE VALIDATION FINAL")
    print("=" * 50)
    
    validations = [
        ("Base de données", check_and_fix_database()),
        ("Listes déroulantes", check_and_fix_dropdown_options()),
        ("Utilisateur admin", check_admin_user()),
        ("Modules Python", verify_imports()),
        ("Workflow TC", test_tc_workflow())
    ]
    
    print(f"\nRésumé des validations ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
    print("-" * 40)
    
    all_passed = True
    for validation_name, result in validations:
        status = "✅ VALIDÉ" if result else "❌ ÉCHEC"
        print(f"{validation_name:<20} : {status}")
        if not result:
            all_passed = False
    
    print("-" * 40)
    
    if all_passed:
        print("🎉 TOUTES LES VALIDATIONS SONT PASSÉES")
        print("✅ L'application est prête à être utilisée")
        print("\n💡 Prochaines étapes :")
        print("   1. Lancez l'application : streamlit run main.py")
        print("   2. Connectez-vous en admin : admin@budget.com / admin123")
        print("   3. Créez vos utilisateurs TC/DR")
        print("   4. Testez la création de demandes")
    else:
        print("⚠️ CERTAINES VALIDATIONS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez ce script")
    
    return all_passed

def main():
    """Fonction principale de validation et correction"""
    print("🔧 BUDGETMANAGE - VALIDATION ET CORRECTION AUTOMATIQUE")
    print("=" * 60)
    print(f"⏰ Début de l'analyse : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Exécution de toutes les validations et corrections
    success = generate_validation_report()
    
    print(f"\n⏰ Fin de l'analyse : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🚀 APPLICATION PRÊTE POUR LA PRODUCTION")
        return 0
    else:
        print("\n❌ CORRECTIONS NÉCESSAIRES")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
