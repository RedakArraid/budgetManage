"""
Migration pour mettre à jour les valeurs stockées des listes déroulantes
Applique la logique : value = replace(lower(label), espaces par _)
"""
import sys
import os
import re

# Ajouter le répertoire parent au chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

def normalize_value_from_label(label: str) -> str:
    """
    Normalise un label en valeur stockée selon la règle :
    value = replace(lower(label), espaces par _)
    + nettoyage caractères spéciaux
    """
    if not label:
        return ""
    
    # 1. Mettre en minuscules
    value = label.lower()
    
    # 2. Remplacer les espaces par des underscores
    value = value.replace(' ', '_')
    
    # 3. Remplacer d'autres caractères problématiques
    value = value.replace('-', '_')
    value = value.replace('/', '_')
    value = value.replace('\\', '_')
    value = value.replace('.', '_')
    value = value.replace(',', '_')
    value = value.replace(';', '_')
    value = value.replace(':', '_')
    value = value.replace('(', '')
    value = value.replace(')', '')
    value = value.replace('[', '')
    value = value.replace(']', '')
    value = value.replace('{', '')
    value = value.replace('}', '')
    value = value.replace("'", '')
    value = value.replace('"', '')
    
    # 4. Supprimer les caractères spéciaux et garder uniquement lettres, chiffres et underscores
    value = re.sub(r'[^a-z0-9_àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', '', value)
    
    # 5. Remplacer les caractères accentués
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'æ': 'ae',
        'ç': 'c',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ð': 'd', 'ñ': 'n',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'þ': 'th', 'ÿ': 'y'
    }
    
    for accented, replacement in replacements.items():
        value = value.replace(accented, replacement)
    
    # 6. Supprimer les underscores multiples et en début/fin
    value = re.sub(r'_+', '_', value)
    value = value.strip('_')
    
    # 7. S'assurer qu'on a au moins quelque chose
    if not value:
        value = "option_vide"
    
    return value

def update_dropdown_values():
    """
    Met à jour toutes les valeurs stockées existantes selon la nouvelle logique
    """
    try:
        print("🔄 Début de la migration des valeurs des listes déroulantes...")
        
        # 1. Récupérer toutes les options existantes
        options = db.execute_query('''
            SELECT id, category, value, label
            FROM dropdown_options
            ORDER BY category, id
        ''', fetch='all')
        
        if not options:
            print("ℹ️ Aucune option trouvée dans la base de données")
            return True
        
        print(f"📊 {len(options)} options trouvées à traiter")
        
        # 2. Traiter chaque option
        updated_count = 0
        conflicts = []
        
        for option in options:
            option_id = option['id']
            category = option['category']
            old_value = option['value']
            label = option['label']
            
            # Calculer la nouvelle valeur
            new_value = normalize_value_from_label(label)
            
            print(f"📝 ID #{option_id} ({category}): '{label}' -> '{old_value}' => '{new_value}'")
            
            # Si la valeur ne change pas, passer au suivant
            if old_value == new_value:
                print(f"  ✅ Déjà correct")
                continue
            
            # Vérifier s'il y a conflit avec une autre option de la même catégorie
            existing = db.execute_query('''
                SELECT id, label FROM dropdown_options
                WHERE category = ? AND value = ? AND id != ?
            ''', (category, new_value, option_id), fetch='one')
            
            if existing:
                conflict_info = {
                    'option_id': option_id,
                    'category': category,
                    'label': label,
                    'old_value': old_value,
                    'new_value': new_value,
                    'conflict_id': existing['id'],
                    'conflict_label': existing['label']
                }
                conflicts.append(conflict_info)
                print(f"  ⚠️ CONFLIT: La valeur '{new_value}' existe déjà (ID #{existing['id']}: '{existing['label']}')")
                continue
            
            # Mettre à jour la valeur
            try:
                # D'abord, vérifier si cette valeur est utilisée dans les demandes
                usage_count = 0
                try:
                    usage_count = db.execute_query(f'''
                        SELECT COUNT(*) FROM demandes WHERE {category} = ?
                    ''', (old_value,), fetch='one')[0]
                except:
                    # Certaines catégories peuvent ne pas avoir de colonne correspondante
                    pass
                
                # Mettre à jour l'option
                db.execute_query('''
                    UPDATE dropdown_options 
                    SET value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_value, option_id))
                
                # Si des demandes utilisent cette valeur, les mettre à jour aussi
                if usage_count > 0:
                    try:
                        db.execute_query(f'''
                            UPDATE demandes 
                            SET {category} = ?
                            WHERE {category} = ?
                        ''', (new_value, old_value))
                        print(f"  📊 {usage_count} demande(s) mises à jour")
                    except Exception as e:
                        print(f"  ⚠️ Erreur mise à jour demandes: {e}")
                
                updated_count += 1
                print(f"  ✅ Mis à jour")
                
            except Exception as e:
                print(f"  ❌ Erreur mise à jour: {e}")
        
        # 3. Rapport final
        print(f"\n📊 Résumé de la migration:")
        print(f"  • Options traitées: {len(options)}")
        print(f"  • Options mises à jour: {updated_count}")
        print(f"  • Conflits détectés: {len(conflicts)}")
        
        if conflicts:
            print(f"\n⚠️ CONFLITS DÉTECTÉS:")
            for conflict in conflicts:
                print(f"  • ID #{conflict['option_id']} '{conflict['label']}' -> '{conflict['new_value']}'")
                print(f"    CONFLIT avec ID #{conflict['conflict_id']} '{conflict['conflict_label']}'")
        
        print(f"\n✅ Migration terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_normalization():
    """
    Teste la fonction de normalisation avec différents exemples
    """
    print("\n🧪 Test de la fonction de normalisation:")
    
    test_cases = [
        "NORD EST",
        "Île-de-France", 
        "Budget Marketing",
        "Salon/Foire",
        "Client VIP",
        "Grande Distribution",
        "Événement Interne",
        "Budget Comm'",
        "Région Sud-Est",
        "Groupement (Spécialisé)",
        "Animation: Client Premium"
    ]
    
    for test_label in test_cases:
        normalized = normalize_value_from_label(test_label)
        print(f"  '{test_label}' -> '{normalized}'")

def show_current_state():
    """
    Affiche l'état actuel des options dans la base
    """
    try:
        print("\n📊 État actuel des options:")
        
        categories = db.execute_query('''
            SELECT DISTINCT category FROM dropdown_options ORDER BY category
        ''', fetch='all')
        
        for cat_row in categories:
            category = cat_row[0]
            print(f"\n📂 {category.upper()}:")
            
            options = db.execute_query('''
                SELECT id, value, label FROM dropdown_options
                WHERE category = ? ORDER BY order_index, label
            ''', (category,), fetch='all')
            
            for opt in options:
                print(f"  #{opt['id']}: '{opt['label']}' -> '{opt['value']}'")
    
    except Exception as e:
        print(f"❌ Erreur affichage état: {e}")

if __name__ == "__main__":
    print("🚀 Migration des valeurs des listes déroulantes")
    print("=" * 60)
    
    # Afficher l'état actuel
    show_current_state()
    
    # Tester la fonction de normalisation
    test_normalization()
    
    # Demander confirmation
    print(f"\n❓ Voulez-vous appliquer la migration ? (y/N): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes', 'oui']:
        success = update_dropdown_values()
        if success:
            print(f"\n🎉 Migration terminée avec succès!")
        else:
            print(f"\n💥 Échec de la migration!")
    else:
        print(f"\n🚫 Migration annulée")
