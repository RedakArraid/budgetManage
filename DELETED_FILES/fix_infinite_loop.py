#!/usr/bin/env python3
"""
Script de correction rapide pour le problème de boucle infinie
lors de la création de demandes
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

def fix_infinite_loop():
    """Corrige le problème de boucle infinie dans nouvelle_demande_view.py"""
    
    project_path = Path(".")
    backup_dir = project_path / f"backup_loop_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("🔧 Correction du problème de boucle infinie...")
    
    # Créer une sauvegarde
    try:
        backup_dir.mkdir(exist_ok=True)
        
        original_file = project_path / "views" / "nouvelle_demande_view.py"
        if original_file.exists():
            shutil.copy2(original_file, backup_dir / "nouvelle_demande_view.py")
            print(f"✅ Sauvegarde créée: {backup_dir}")
        
        # Appliquer la correction
        fixed_file = project_path / "views" / "nouvelle_demande_view_fixed.py"
        if fixed_file.exists():
            shutil.copy2(fixed_file, original_file)
            print("✅ Correction appliquée")
            
            # Nettoyer l'état de session si l'app tourne
            print("\n📋 Instructions:")
            print("1. Redémarrez votre application Streamlit")
            print("2. La boucle infinie est maintenant corrigée")
            print("3. Les demandes se créeront normalement")
            
            return True
        else:
            print("❌ Fichier de correction non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def clean_session_state():
    """Nettoie l'état de session problématique"""
    try:
        # Créer un script de nettoyage
        cleanup_script = '''
import streamlit as st

# Nettoyer les états problématiques
keys_to_clean = [
    'demande_created', 'created_demande_id', 'created_demande_nom',
    'created_demande_montant', 'created_demande_type'
]

for key in keys_to_clean:
    if key in st.session_state:
        del st.session_state[key]

st.success("✅ État de session nettoyé!")
st.info("Vous pouvez maintenant créer des demandes normalement.")
'''
        
        with open("cleanup_session.py", "w") as f:
            f.write(cleanup_script)
        
        print("✅ Script de nettoyage créé: cleanup_session.py")
        print("   Exécutez: streamlit run cleanup_session.py")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création script: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Correction du Problème de Boucle Infinie - BudgetManage")
    print("=" * 60)
    
    if not Path("main.py").exists():
        print("❌ Exécutez ce script depuis le dossier racine de BudgetManage")
        exit(1)
    
    # Appliquer la correction
    success = fix_infinite_loop()
    
    # Créer le script de nettoyage
    clean_session_state()
    
    if success:
        print("\n🎉 CORRECTION APPLIQUÉE AVEC SUCCÈS!")
        print("\n🚀 Actions suivantes:")
        print("   1. Arrêtez votre application Streamlit (Ctrl+C)")
        print("   2. Redémarrez: streamlit run main.py")
        print("   3. Testez la création d'une demande")
        print("\n💡 Si le problème persiste:")
        print("   - Exécutez: streamlit run cleanup_session.py")
        print("   - Puis redémarrez l'application principale")
    else:
        print("\n❌ ÉCHEC DE LA CORRECTION")
        print("   Vérifiez que tous les fichiers sont présents")
