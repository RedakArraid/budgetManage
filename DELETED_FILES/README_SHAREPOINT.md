# 📁 BudgetManage - Guide SharePoint Sync

## 🚀 Utilisation depuis SharePoint Synchronisé

### ✅ Prérequis
- SharePoint synchronisé avec votre PC (OneDrive ou SharePoint Sync)
- Windows 10/11 avec droits d'exécution
- Connexion Internet (pour la première configuration)

### 📁 Structure des Fichiers
```
📁 SharePoint/BudgetManage/
├── BudgetManage.exe          ← Application principale
├── start_sharepoint.bat      ← Script de lancement
├── README.md                 ← Ce guide
└── data/                     ← Vos données (créé automatiquement)
```

## 🎯 Comment Utiliser

### 1️⃣ **Premier Lancement**
1. Ouvrir le dossier SharePoint synchronisé
2. Aller dans le dossier `BudgetManage`
3. **Double-cliquer** sur `start_sharepoint.bat`
4. Attendre que l'application se lance (10-30s)
5. Le navigateur s'ouvre automatiquement

### 2️⃣ **Connexion**
- **URL** : http://localhost:8501
- **Email** : admin@budget.com
- **Mot de passe** : admin123

⚠️ **IMPORTANT** : Changez le mot de passe après la première connexion !

### 3️⃣ **Utilisation Quotidienne**
- **Lancer** : Double-clic sur `start_sharepoint.bat`
- **Accéder** : Aller sur http://localhost:8501 dans votre navigateur
- **Arrêter** : Fermer la fenêtre de commande

## 💾 Données et Synchronisation

### 🔄 **Ce qui se Synchronise**
- ✅ Application (BudgetManage.exe)
- ✅ Scripts (start_sharepoint.bat)
- ✅ Documentation

### 💾 **Ce qui reste Local**
- ❌ Votre base de données (dossier `data/`)
- ❌ Vos utilisateurs créés
- ❌ Vos demandes budget

> **Pourquoi ?** Pour éviter les conflits entre utilisateurs et préserver la confidentialité.

## 🆘 Résolution de Problèmes

### **❌ "BudgetManage.exe non trouvé"**
- Vérifier que SharePoint est bien synchronisé
- Attendre la fin de la synchronisation
- Rafraîchir le dossier (F5)

### **❌ "Port 8501 déjà utilisé"**
- Une autre instance est déjà lancée
- Fermer les autres fenêtres BudgetManage
- Redémarrer votre PC si nécessaire

### **❌ "L'application ne se lance pas"**
- Vérifier les droits d'exécution
- Contacter votre IT si bloqué par antivirus
- Essayer en tant qu'administrateur

### **🌐 "Le navigateur ne s'ouvre pas"**
- Ouvrir manuellement : http://localhost:8501
- Vérifier que l'application est bien lancée
- Attendre un peu plus (peut prendre 1-2 minutes)

## 🔧 Configuration Avancée

### **Changer le Port (si 8501 occupé)**
1. Éditer `start_sharepoint.bat`
2. Remplacer `8501` par `8502` (ou autre)
3. Sauvegarder et relancer

### **Partager avec Équipe**
- Chaque utilisateur doit lancer sa propre instance
- Chacun aura sa base de données séparée
- Pour partager : utiliser l'export Excel

## 📞 Support

- **Documentation** : README.md dans ce dossier
- **Problèmes** : Contacter l'administrateur
- **Mise à jour** : Automatique via SharePoint Sync

## 🔄 Mises à Jour

Les mises à jour se font automatiquement :
1. Nouvelle version uploadée sur SharePoint
2. SharePoint sync télécharge automatiquement
3. Redémarrer BudgetManage pour utiliser la nouvelle version

---

**Version** : 1.0.0  
**Dernière mise à jour** : Juin 2025  
**Compatible** : Windows 10/11
