# BudgetManage - Système de Gestion Budget

Application Streamlit moderne pour la gestion des demandes budgétaires avec workflow de validation hiérarchique.

## 🏗️ Architecture MVC

### Structure du Projet

```
budgetmanage/
├── main.py                    # Point d'entrée principal
├── config/                    # Configuration
│   ├── __init__.py
│   └── settings.py           # Paramètres de l'application
├── models/                    # Modèles de données
│   ├── __init__.py
│   ├── database.py           # Gestionnaire de base de données
│   ├── user.py              # Modèle utilisateur
│   ├── demande.py           # Modèle demande
│   ├── notification.py      # Modèle notification
│   └── activity_log.py      # Modèle logs d'activité
├── controllers/               # Contrôleurs métier
│   ├── __init__.py
│   ├── auth_controller.py    # Contrôleur authentification
│   ├── user_controller.py    # Contrôleur utilisateur
│   └── demande_controller.py # Contrôleur demande
├── services/                  # Services métier
│   ├── __init__.py
│   ├── email_service.py      # Service email
│   ├── notification_service.py # Service notifications
│   └── workflow_service.py   # Service workflow
├── views/                     # Vues Streamlit
│   ├── __init__.py
│   ├── login_view.py         # Page connexion
│   ├── dashboard_view.py     # Page tableau de bord
│   ├── nouvelle_demande_view.py # Page nouvelle demande
│   ├── demandes_view.py      # Page gestion demandes
│   ├── gestion_utilisateurs_view.py # Page admin utilisateurs
│   ├── validations_view.py   # Page validations
│   ├── analytics_view.py     # Page analytics
│   └── notifications_view.py # Page notifications
├── utils/                     # Utilitaires
│   ├── __init__.py
│   ├── security.py          # Utilitaires sécurité
│   ├── validators.py        # Validateurs
│   └── date_utils.py        # Utilitaires de date
├── static/                    # Ressources statiques
│   └── styles.py            # Styles CSS
├── .env.template             # Template variables d'environnement
├── requirements.txt          # Dépendances Python
├── budget_workflow.db        # Base de données SQLite
├── start.bat / start.sh      # Scripts de démarrage
├── DELETED_FILES/            # Fichiers supprimés (ancienne version)
└── README.md                # Documentation
```

## 🧹 Nettoyage et Corrections (23 Mai 2025)

### Corrections Apportées
Tous les problèmes de validation ont été résolus :
- ✅ **Validation DR** : Passage correct vers `en_attente_financier`
- ✅ **Validation Financier** : Boutons fonctionnels 
- ✅ **Validation DG** : Support complet avec colonnes dédiées
- ✅ **Page Admin** : Analytics corrigées
- ✅ **Workflow complet** : TC → DR → Financier/DG → Validée

### Fichiers de Correction
Tous les scripts de diagnostic, correction et test ont été déplacés dans :
`DELETED_FILES/corrections_validation/`

Ces fichiers incluent :
- Scripts de diagnostic des problèmes
- Scripts de migration base de données
- Tests de validation du workflow
- Documentation des corrections

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.8+
- Windows (pour les notifications Outlook, optionnel)

### Installation

1. **Cloner et accéder au projet**
```bash
cd budgetmanage
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration**
```bash
# Copier le template de configuration
cp .env.template .env

# Éditer .env avec vos paramètres
# EMAIL_ADDRESS=votre-email@gmail.com
# EMAIL_PASSWORD=votre-mot-de-passe-app
```

4. **Démarrer l'application**
```bash
# Démarrage de l'application
streamlit run main.py

# Ou utiliser les scripts
./start.sh    # Linux/macOS
start.bat     # Windows
```

## 🏛️ Architecture MVC Moderne

### ✅ Avantages de l'Architecture

1. **Séparation des Responsabilités**
   - **Models** : Gestion des données et base de données
   - **Views** : Interface utilisateur Streamlit
   - **Controllers** : Logique métier et coordination
   - **Services** : Services transversaux (email, notifications)

2. **Maintenabilité**
   - Code modulaire et réutilisable
   - Tests unitaires facilités
   - Évolutions plus simples

3. **Configuration Externalisée**
   - Paramètres dans `config/settings.py`
   - Variables d'environnement avec `.env`
   - Configuration par rôle centralisée

4. **Sécurité Renforcée**
   - Validation centralisée dans `utils/validators.py`
   - Utilitaires de sécurité dans `utils/security.py`
   - Contrôle d'accès par décorateurs

5. **Services Découplés**
   - Service email indépendant
   - Service notifications réutilisable
   - Service workflow modulaire

## 🔧 Version 2.0 - Architecture Refactorisée

Cette version représente une refactorisation complète depuis une version monolithique vers une architecture MVC moderne :

- **Meilleure organisation** du code
- **Performance améliorée** grâce à la modularité
- **Facilité de maintenance** et d'évolution
- **Tests unitaires** possibles
- **Documentation** intégrée
- **Code plus propre** et maintenable

> 📁 Les anciens fichiers ont été déplacés dans `DELETED_FILES/` pour référence

## 👥 Rôles et Permissions

### Rôles Supportés
- **Admin** : Gestion complète du système
- **TC** (Technico-Commercial) : Création demandes budget
- **DR** (Directeur Régional) : Validation équipe + demandes propres
- **DR Financier** : Validation financière finale
- **DG** (Directeur Général) : Validation financière finale
- **Marketing** : Demandes marketing spécifiques

### Workflow de Validation
1. **TC** → **DR** → **Financier/DG** (demandes budget)
2. **Marketing** → **Financier/DG/Admin** (demandes marketing)

## 📊 Fonctionnalités

- ✅ Authentification sécurisée
- ✅ Gestion utilisateurs complète
- ✅ Workflow de validation hiérarchique
- ✅ Notifications email automatiques
- ✅ Dashboard avec métriques
- ✅ Analytics et rapports
- ✅ Export Excel/CSV
- ✅ Interface responsive
- ✅ Logs d'activité complets

## 🔧 Configuration Avancée

### Email (Outlook)
```python
# config/settings.py
EMAIL_CONFIG = {
    'use_outlook': True,  # Utiliser Outlook COM
    'smtp_server': 'smtp.gmail.com',  # Fallback SMTP
    'smtp_port': 587
}
```

### Base de Données
```python
# config/settings.py  
DATABASE_CONFIG = {
    'name': 'budget_workflow.db',
    'path': 'chemin/vers/la/base.db'
}
```

### Rôles et Permissions
```python
# config/settings.py
ROLE_CONFIG = {
    'roles': {
        'admin': {
            'permissions': ['create_user', 'view_all'],
            'color': '#ff6b6b'
        }
    }
}
```

## 🐛 Debug et Logs

Les logs d'activité sont automatiquement créés pour :
- Connexions/déconnexions
- Créations/modifications d'utilisateurs
- Workflow des demandes
- Actions administratives

## 🚀 Déploiement

Pour un déploiement en production :

1. **Modifier la base de données** (PostgreSQL/MySQL)
2. **Configurer un serveur SMTP** dédié
3. **Ajouter HTTPS** et authentification avancée
4. **Implémenter la haute disponibilité**
5. **Ajouter monitoring** et alertes

## 📝 Contribution

L'architecture MVC facilite les contributions :

1. **Ajouter une vue** : Créer dans `views/`
2. **Ajouter un modèle** : Créer dans `models/`
3. **Ajouter un service** : Créer dans `services/`
4. **Modifier la config** : Éditer `config/settings.py`

## 🧹 Nettoyage du Projet

### Fichiers Supprimés
- `app.py` - Ancienne version monolithique
- `requirements_old.txt` - Anciens requirements
- Fichiers `.backup` - Tentatives de migration SharePoint
- `budget_workflow_local.db` - Base de données redondante
- Fichiers système (`.DS_Store`)

Tous ces fichiers sont disponibles dans `DELETED_FILES/` si nécessaire.

## 📧 Support

- **Issues** : Créer une issue GitHub
- **Améliorations** : Proposer une Pull Request
- **Questions** : Contacter l'équipe de développement

## 📄 Licence

Projet interne - Tous droits réservés

---

**Version** : 2.0 (Architecture MVC refactorisée)  
**Dernière mise à jour** : Mai 2025
**Nettoyage** : Fichiers obsolètes supprimés
