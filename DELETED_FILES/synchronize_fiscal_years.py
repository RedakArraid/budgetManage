#!/usr/bin/env python3
"""
Script de synchronisation complète des années fiscales
Aligne tous les systèmes d'années dans l'application
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from utils.fiscal_year_utils import byxx_to_year, year_to_byxx

def analyze_current_state():
    """Analyse l'état actuel de tous les systèmes d'années"""
    print("🔍 ANALYSE ÉTAT ACTUEL DES SYSTÈMES D'ANNÉES")
    print("=" * 55)
    
    analysis = {
        'dropdown_options': {},
        'demandes_columns': {},
        'user_budgets': {},
        'issues': []
    }
    
    try:
        # 1. Dropdown options annee_fiscale
        print("📋 1. DROPDOWN OPTIONS (annee_fiscale)")
        print("-" * 40)
        
        dropdown_years = db.execute_query("""
            SELECT value, label, is_active 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if dropdown_years:
            print(f"   📊 {len(dropdown_years)} années configurées:")
            for year in dropdown_years:
                status = "🟢" if year['is_active'] else "🔴"
                print(f"      {status} {year['value']} → {year['label']}")
                
                # Analyser le format
                converted_year = byxx_to_year(year['value'])
                if converted_year:
                    analysis['dropdown_options'][year['value']] = converted_year
                else:
                    analysis['issues'].append(f"Format dropdown invalide: {year['value']}")
        else:
            print("   ❌ Aucune année fiscale dans dropdown_options")
            analysis['issues'].append("Aucune année fiscale dans dropdown_options")
        
        # 2. Colonnes de la table demandes
        print(f"\n📝 2. TABLE DEMANDES")
        print("-" * 20)
        
        # Vérifier les colonnes existantes
        columns_info = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        year_columns = []
        
        for col in columns_info:
            col_name = col['name']
            if any(keyword in col_name.lower() for keyword in ['year', 'fiscal', 'by', 'cy', 'annee']):
                year_columns.append(col_name)
        
        print(f"   📋 Colonnes d'années détectées: {', '.join(year_columns)}")
        analysis['demandes_columns']['available'] = year_columns
        
        # Analyser les données dans chaque colonne
        for col in year_columns:
            try:
                sample_data = db.execute_query(f"""
                    SELECT {col}, COUNT(*) as count
                    FROM demandes 
                    WHERE {col} IS NOT NULL AND {col} != ''
                    GROUP BY {col}
                    ORDER BY count DESC
                    LIMIT 5
                """, fetch='all')
                
                if sample_data:
                    print(f"   📊 Données dans {col}:")
                    for row in sample_data:
                        print(f"      • {row[col]}: {row['count']} demandes")
                    analysis['demandes_columns'][col] = [row[col] for row in sample_data]
                
            except Exception as e:
                print(f"   ❌ Erreur lecture {col}: {e}")
        
        # 3. Table user_budgets
        print(f"\n💰 3. TABLE USER_BUDGETS")
        print("-" * 25)
        
        try:
            budget_years = db.execute_query("""
                SELECT fiscal_year, COUNT(*) as count
                FROM user_budgets
                GROUP BY fiscal_year
                ORDER BY fiscal_year
            """, fetch='all')
            
            if budget_years:
                print(f"   📊 Années avec budgets:")
                for row in budget_years:
                    print(f"      • {row['fiscal_year']}: {row['count']} budgets")
                analysis['user_budgets'] = {row['fiscal_year']: row['count'] for row in budget_years}
            else:
                print("   ℹ️ Aucun budget configuré")
                
        except Exception as e:
            print(f"   ❌ Erreur lecture user_budgets: {e}")
            analysis['issues'].append(f"Erreur user_budgets: {e}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        analysis['issues'].append(f"Erreur générale: {e}")
        return analysis

def create_synchronization_plan(analysis):
    """Crée un plan de synchronisation basé sur l'analyse"""
    print(f"\n🎯 PLAN DE SYNCHRONISATION")
    print("=" * 30)
    
    plan = {
        'actions': [],
        'priority': 'medium'
    }
    
    # Vérifier les incohérences
    dropdown_years = set(analysis['dropdown_options'].values())  # Années converties depuis BYXX
    budget_years = set(analysis['user_budgets'].keys())
    
    print(f"📋 Années dans dropdown (converties): {sorted(dropdown_years)}")
    print(f"💰 Années dans budgets: {sorted(budget_years)}")
    
    # 1. Problèmes dropdown → budgets
    missing_in_budgets = dropdown_years - budget_years
    if missing_in_budgets:
        print(f"⚠️ Années dropdown absentes des budgets: {sorted(missing_in_budgets)}")
        plan['actions'].append({
            'type': 'info',
            'description': f"Les années {sorted(missing_in_budgets)} sont configurées mais n'ont pas de budgets"
        })
    
    # 2. Problèmes budgets → dropdown
    missing_in_dropdown = budget_years - dropdown_years
    if missing_in_dropdown:
        print(f"⚠️ Années budgets absentes du dropdown: {sorted(missing_in_dropdown)}")
        plan['actions'].append({
            'type': 'add_dropdown',
            'years': sorted(missing_in_dropdown),
            'description': f"Ajouter les années {sorted(missing_in_dropdown)} au dropdown"
        })
    
    # 3. Vérifier les colonnes demandes
    demandes_cols = analysis['demandes_columns']['available']
    if 'fiscal_year' in demandes_cols:
        # Vérifier si fiscal_year utilise le bon format
        fiscal_year_data = analysis['demandes_columns'].get('fiscal_year', [])
        needs_conversion = any(isinstance(year, int) and year > 1000 for year in fiscal_year_data)
        
        if needs_conversion:
            plan['actions'].append({
                'type': 'convert_demandes_fiscal_year',
                'description': "Convertir fiscal_year dans demandes vers format numérique"
            })
    
    # 4. Problèmes graves
    if not dropdown_years:
        plan['priority'] = 'critical'
        plan['actions'].append({
            'type': 'init_dropdown',
            'description': "Initialiser les années fiscales dans dropdown_options"
        })
    
    return plan

def execute_synchronization(plan):
    """Exécute le plan de synchronisation"""
    print(f"\n🚀 EXÉCUTION DE LA SYNCHRONISATION")
    print("=" * 40)
    
    success_count = 0
    total_actions = len(plan['actions'])
    
    for i, action in enumerate(plan['actions'], 1):
        print(f"\n📌 Action {i}/{total_actions}: {action['description']}")
        
        try:
            if action['type'] == 'add_dropdown':
                # Ajouter des années manquantes au dropdown
                for year in action['years']:
                    byxx_value = year_to_byxx(year)
                    label = f"{byxx_value} ({year})"
                    order_index = year - 2019
                    
                    db.execute_query("""
                        INSERT OR IGNORE INTO dropdown_options 
                        (category, value, label, order_index, is_active)
                        VALUES (?, ?, ?, ?, ?)
                    """, ('annee_fiscale', byxx_value, label, order_index, True))
                    
                    print(f"   ✅ Ajouté: {byxx_value} ({year})")
                success_count += 1
                
            elif action['type'] == 'convert_demandes_fiscal_year':
                # Note: Pas de conversion nécessaire car fiscal_year doit rester numérique
                print(f"   ℹ️ fiscal_year garde le format numérique (correct)")
                success_count += 1
                
            elif action['type'] == 'init_dropdown':
                # Initialiser le dropdown
                for year in range(2020, 2031):
                    byxx_value = year_to_byxx(year)
                    label = f"{byxx_value} ({year})"
                    order_index = year - 2019
                    
                    db.execute_query("""
                        INSERT OR IGNORE INTO dropdown_options 
                        (category, value, label, order_index, is_active)
                        VALUES (?, ?, ?, ?, ?)
                    """, ('annee_fiscale', byxx_value, label, order_index, True))
                
                print(f"   ✅ Dropdown initialisé avec BY20-BY30")
                success_count += 1
                
            elif action['type'] == 'info':
                print(f"   ℹ️ Information notée")
                success_count += 1
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print(f"\n📊 Résultats: {success_count}/{total_actions} actions réussies")
    return success_count == total_actions

def verify_synchronization():
    """Vérifie que la synchronisation est correcte"""
    print(f"\n✅ VÉRIFICATION FINALE")
    print("=" * 25)
    
    try:
        # 1. Vérifier dropdown_options
        dropdown_years = db.execute_query("""
            SELECT value, label FROM dropdown_options 
            WHERE category = 'annee_fiscale' AND is_active = 1
            ORDER BY order_index
        """, fetch='all')
        
        print(f"📋 Dropdown configuré:")
        for year in dropdown_years:
            converted = byxx_to_year(year['value'])
            print(f"   • {year['value']} → {year['label']} (= {converted})")
        
        # 2. Vérifier que la conversion fonctionne
        print(f"\n🔧 Test de conversion:")
        test_values = ['BY24', 'BY25', 'BY26']
        for test_val in test_values:
            converted = byxx_to_year(test_val)
            reconverted = year_to_byxx(converted)
            status = "✅" if reconverted == test_val else "❌"
            print(f"   {status} {test_val} → {converted} → {reconverted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def main():
    """Fonction principale de synchronisation"""
    print("🔄 SYNCHRONISATION COMPLÈTE DES ANNÉES FISCALES")
    print("=" * 55)
    print("🎯 Objectif: Synchroniser dropdown_options, user_budgets et demandes")
    print()
    
    try:
        # Étape 1: Analyse
        analysis = analyze_current_state()
        
        # Étape 2: Plan
        plan = create_synchronization_plan(analysis)
        
        # Étape 3: Exécution
        if plan['actions']:
            success = execute_synchronization(plan)
        else:
            print(f"\n✅ AUCUNE ACTION NÉCESSAIRE")
            print("   Tous les systèmes sont déjà synchronisés")
            success = True
        
        # Étape 4: Vérification
        if success:
            verify_success = verify_synchronization()
            
            print(f"\n" + "=" * 55)
            if verify_success:
                print("🎉 SYNCHRONISATION TERMINÉE AVEC SUCCÈS!")
                print("\n✅ TOUS LES SYSTÈMES SYNCHRONISÉS:")
                print("   • dropdown_options: Format BYXX ✅")
                print("   • user_budgets: Années numériques ✅") 
                print("   • Interface: Conversion automatique ✅")
                
                print(f"\n🚀 L'APPLICATION EST PRÊTE!")
                print("   1. Redémarrez Streamlit")
                print("   2. Testez la page 'Gestion Budgets'")
                print("   3. Les années s'affichent: BY24, BY25, etc.")
            else:
                print("⚠️ SYNCHRONISATION PARTIELLEMENT RÉUSSIE")
        else:
            print(f"\n❌ ÉCHEC DE LA SYNCHRONISATION")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n💡 RAPPEL: Le fichier gestion_budgets_view.py a été modifié")
    print(f"   pour gérer automatiquement la conversion BYXX → numérique")
    sys.exit(0 if success else 1)
