# 💰 BudgetManage - Système de Gestion Budget

> Application Streamlit moderne pour la gestion des demandes budgétaires avec workflow de validation hiérarchique

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)](https://sqlite.org/)
[![Architecture](https://img.shields.io/badge/Architecture-MVC-orange.svg)](#architecture)

## 🚀 Fonctionnalités

- ✅ **Workflow de validation hiérarchique** (TC → DR → Financier/DG)
- ✅ **Système de permissions granulaires** basé sur les rôles
- ✅ **Notifications email automatiques** (Outlook + SMTP)
- ✅ **Analytics et rapports avancés** avec graphiques temps réel
- ✅ **Interface moderne** avec Streamlit
- ✅ **Architecture MVC** maintenable et évolutive
- ✅ **Base de données optimisée** avec migrations automatiques
- ✅ **Sécurité robuste** avec authentification bcrypt

## 🏗️ Architecture

```
budgetmanage/
├── 📱 main.py                 # Point d'entrée et routeur
├── ⚙️ config/                 # Configuration centralisée
├── 💾 models/                 # Couche de données (User, Demande, etc.)
├── 🎮 controllers/            # Logique métier
├── 🔧 services/               # Services transversaux
├── 🖥️ views/                  # Interface utilisateur Streamlit
├── 🛠️ utils/                  # Utilitaires et helpers
└── 🎨 static/                 # Styles et ressources
```

## 👥 Rôles et Workflow

| Rôle | Permissions | Workflow |
|------|-------------|----------|
| **Admin** | Gestion complète | Tous accès |
| **TC** | Création demandes | TC → DR → Financier |
| **DR** | Validation équipe | Validation première étape |
| **Financier/DG** | Validation finale | Approbation budgétaire |
| **Marketing** | Demandes marketing | Marketing → Financier |

## 🚀 Installation Rapide

```bash
# Clone du projet
git clone https://github.com/VOTRE-USERNAME/budgetmanage.git
cd budgetmanage

# Installation des dépendances
pip install -r requirements.txt

# Configuration
cp .env.template .env
# Éditer .env avec vos paramètres email

# Démarrage
streamlit run main.py
```

## ⚙️ Configuration

### Email (Notifications)
```bash
# .env
EMAIL_ADDRESS=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app
```

### Première Connexion
- **URL** : http://localhost:8501
- **Admin** : admin@budget.com / admin123
- **Changez le mot de passe** après la première connexion !

## 📊 Captures d'Écran

### Tableau de Bord
![Dashboard](docs/screenshots/dashboard.png)

### Workflow de Validation
![Workflow](docs/screenshots/workflow.png)

### Analytics
![Analytics](docs/screenshots/analytics.png)

## 🧪 Tests et Qualité

```bash
# Tests unitaires (à implémenter)
python -m pytest tests/

# Lint et formatage
black .
flake8 .
```

## 🔧 Technologies

- **Frontend** : Streamlit, HTML/CSS/JavaScript
- **Backend** : Python 3.8+, SQLite
- **Sécurité** : bcrypt, session management
- **Email** : SMTP, Outlook COM
- **Analytics** : Plotly, Pandas
- **Architecture** : MVC Pattern

## 🚢 Déploiement

### Production
- **Base de données** : PostgreSQL/MySQL recommandé
- **HTTPS** : Certificat SSL obligatoire
- **Email** : Service SMTP dédié (SendGrid, Mailgun)
- **Monitoring** : Logs et métriques

### Docker (à venir)
```bash
docker build -t budgetmanage .
docker run -p 8501:8501 budgetmanage
```

## 📋 Roadmap

### v2.1 (Q3 2025)
- [ ] Tests unitaires complets
- [ ] API REST
- [ ] Docker containerization
- [ ] CI/CD Pipeline

### v2.2 (Q4 2025)
- [ ] Base PostgreSQL
- [ ] Authentification SSO
- [ ] Interface mobile/PWA
- [ ] Intégrations ERP

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/amelioration`)
3. **Commit** vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/amelioration`)
5. **Ouvrir** une Pull Request

## 📄 Licence

Ce projet est sous licence privée - Tous droits réservés.

## 👨‍💻 Auteur

**Votre Nom** - [GitHub](https://github.com/VOTRE-USERNAME)

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/VOTRE-USERNAME/budgetmanage/issues)
- **Documentation** : [Wiki](https://github.com/VOTRE-USERNAME/budgetmanage/wiki)

---

⭐ **Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !**
