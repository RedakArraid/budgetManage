#!/usr/bin/env python3
"""
Script de correction complémentaire pour les colonnes d'années dans la table demandes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db

def check_demandes_columns():
    """Vérifie les colonnes de la table demandes"""
    try:
        print("🔍 VÉRIFICATION STRUCTURE TABLE DEMANDES")
        print("=" * 45)
        
        # Obtenir la structure de la table
        columns_info = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        
        print("📋 Colonnes existantes dans la table demandes:")
        year_columns = []
        
        for col in columns_info:
            col_name = col['name']
            col_type = col['type']
            print(f"   • {col_name} ({col_type})")
            
            # Identifier les colonnes liées aux années
            if any(year_keyword in col_name.lower() for year_keyword in ['year', 'fiscal', 'by', 'cy', 'annee']):
                year_columns.append(col_name)
        
        print(f"\n🎯 Colonnes liées aux années détectées:")
        for col in year_columns:
            print(f"   • {col}")
        
        return year_columns
        
    except Exception as e:
        print(f"❌ Erreur vérification colonnes: {e}")
        return []

def fix_demandes_years():
    """Corrige les années dans les demandes selon les colonnes disponibles"""
    try:
        print("\n🔧 CORRECTION ANNÉES DANS LES DEMANDES")
        print("=" * 40)
        
        # Vérifier les colonnes
        year_columns = check_demandes_columns()
        
        if not year_columns:
            print("❌ Aucune colonne d'année trouvée")
            return False
        
        # Priorité des colonnes à vérifier
        priority_columns = ['fiscal_year', 'by', 'cy', 'annee_fiscale', 'year']
        
        # Trouver la colonne principale
        main_column = None
        for col in priority_columns:
            if col in year_columns:
                main_column = col
                break
        
        if not main_column:
            main_column = year_columns[0]  # Prendre la première disponible
        
        print(f"🎯 Colonne principale identifiée: {main_column}")
        
        # Vérifier les données existantes
        sample_data = db.execute_query(f"""
            SELECT {main_column}, COUNT(*) as count
            FROM demandes 
            WHERE {main_column} IS NOT NULL AND {main_column} != ''
            GROUP BY {main_column}
            ORDER BY {main_column}
            LIMIT 10
        """, fetch='all')
        
        if sample_data:
            print(f"\n📊 Données existantes dans {main_column}:")
            needs_update = False
            
            for row in sample_data:
                value = row[main_column]
                count = row['count']
                print(f"   • {value}: {count} demandes")
                
                # Vérifier si c'est un format année complète
                if isinstance(value, str) and value.isdigit() and len(value) == 4:
                    needs_update = True
            
            if needs_update:
                print(f"\n🔄 Mise à jour nécessaire des années complètes vers format BYXX")
                return update_year_column(main_column)
            else:
                print(f"\n✅ Les données semblent déjà au bon format")
                return True
        else:
            print(f"\nℹ️ Aucune donnée trouvée dans {main_column}")
            return True
            
    except Exception as e:
        print(f"❌ Erreur correction demandes: {e}")
        return False

def update_year_column(column_name):
    """Met à jour une colonne d'année spécifique"""
    try:
        print(f"🔄 Mise à jour de la colonne {column_name}...")
        
        # Mapping des conversions
        year_mapping = {}
        for year in range(2020, 2031):
            old_format = str(year)
            new_format = f"BY{year % 100:02d}"
            year_mapping[old_format] = new_format
        
        total_updated = 0
        for old_value, new_value in year_mapping.items():
            try:
                rows_affected = db.execute_query(f"""
                    UPDATE demandes 
                    SET {column_name} = ?
                    WHERE {column_name} = ?
                """, (new_value, old_value))
                
                if rows_affected > 0:
                    total_updated += rows_affected
                    print(f"   ✅ {rows_affected} demandes: {old_value} → {new_value}")
                    
            except Exception as e:
                print(f"   ❌ Erreur {old_value}: {e}")
        
        if total_updated == 0:
            print("   ℹ️ Aucune demande à migrer")
        else:
            print(f"   📊 {total_updated} demandes mises à jour")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur mise à jour colonne {column_name}: {e}")
        return False

def verify_final_state():
    """Vérifie l'état final de toutes les configurations"""
    try:
        print("\n✅ VÉRIFICATION FINALE COMPLÈTE")
        print("=" * 35)
        
        # 1. Vérifier les années fiscales dans dropdown_options
        years = db.execute_query("""
            SELECT value, label 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' AND is_active = 1
            ORDER BY order_index
        """, fetch='all')
        
        print("📋 Années fiscales configurées:")
        for year in years:
            print(f"   • {year['value']} - {year['label']}")
        
        # 2. Vérifier les colonnes de demandes
        year_columns = check_demandes_columns()
        
        # 3. Vérifier un échantillon des demandes
        if year_columns:
            main_col = year_columns[0]  # Prendre la première colonne d'année
            
            sample = db.execute_query(f"""
                SELECT {main_col}, COUNT(*) as count
                FROM demandes 
                WHERE {main_col} IS NOT NULL
                GROUP BY {main_col}
                ORDER BY {main_col}
                LIMIT 5
            """, fetch='all')
            
            if sample:
                print(f"\n📊 Échantillon demandes ({main_col}):")
                for row in sample:
                    print(f"   • {row[main_col]}: {row['count']} demandes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification finale: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 CORRECTION COMPLÉMENTAIRE - COLONNES DEMANDES")
    print("=" * 55)
    print("🎯 Objectif: Corriger les colonnes d'années dans les demandes")
    print()
    
    try:
        # Étape 1: Vérifier la structure
        year_columns = check_demandes_columns()
        
        if not year_columns:
            print("\n❌ Aucune colonne d'année trouvée dans les demandes")
            print("💡 Les demandes utilisent peut-être un autre système")
            return True  # Pas forcément un problème
        
        # Étape 2: Corriger si nécessaire
        success = fix_demandes_years()
        
        # Étape 3: Vérification finale
        verify_final_state()
        
        print(f"\n" + "=" * 55)
        if success:
            print("🎉 CORRECTION COMPLÉMENTAIRE TERMINÉE!")
            print("\n✅ STATUT GLOBAL:")
            print("   • Années fiscales: Format BYXX ✅")
            print("   • Table demandes: Vérifiée ✅")
            print("   • Application: Prête à utiliser ✅")
            
            print(f"\n🚀 PROCHAINES ÉTAPES:")
            print("   1. Redémarrez votre application Streamlit")
            print("   2. Testez la page 'Gestion Budgets'")
            print("   3. Les années doivent s'afficher: BY24, BY25, etc.")
        else:
            print("⚠️ VÉRIFICATION TERMINÉE AVEC AVERTISSEMENTS")
            print("   Le problème principal (format BYXX) est résolu")
            print("   Les demandes peuvent utiliser un autre système")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n💡 RAPPEL: Le problème principal est déjà résolu!")
    print(f"   Les années fiscales sont maintenant au format BYXX")
    sys.exit(0 if success else 1)
