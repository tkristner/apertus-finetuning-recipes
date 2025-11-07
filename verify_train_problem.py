#!/usr/bin/env python3
"""
Vérifie la solution correcte du problème de trains
et teste un modèle dessus
"""

def solve_train_problem():
    """
    Résout le problème de trains de manière correcte
    """
    print("=" * 80)
    print("🚂 SOLUTION CORRECTE DU PROBLÈME DE TRAINS")
    print("=" * 80)
    print()
    
    print("📝 ÉNONCÉ:")
    print("Un train part de Paris à 14h et roule à 120 km/h.")
    print("Un autre train part de Lyon (450 km de Paris) à 14h30 et roule à 100 km/h vers Paris.")
    print("À quelle heure et à quelle distance de Paris se croiseront-ils?")
    print()
    
    print("=" * 80)
    print("🧮 SOLUTION ÉTAPE PAR ÉTAPE")
    print("=" * 80)
    print()
    
    # Données
    v1 = 120  # km/h (Paris -> Lyon)
    v2 = 100  # km/h (Lyon -> Paris)
    distance_totale = 450  # km
    decalage = 0.5  # heures (30 minutes)
    
    print("📊 DONNÉES:")
    print(f"   - Train 1 (Paris): vitesse = {v1} km/h, départ = 14h00")
    print(f"   - Train 2 (Lyon): vitesse = {v2} km/h, départ = 14h30")
    print(f"   - Distance Paris-Lyon: {distance_totale} km")
    print()
    
    # Étape 1: Distance parcourue par train 1 avant le départ du train 2
    print("ÉTAPE 1: Distance parcourue par le train 1 avant 14h30")
    distance_train1_avant = v1 * decalage
    print(f"   Distance = vitesse × temps = {v1} km/h × {decalage} h = {distance_train1_avant} km")
    print()
    
    # Étape 2: Distance restante entre les deux trains à 14h30
    print("ÉTAPE 2: Distance restante entre les trains à 14h30")
    distance_restante = distance_totale - distance_train1_avant
    print(f"   Distance restante = {distance_totale} km - {distance_train1_avant} km = {distance_restante} km")
    print()
    
    # Étape 3: Vitesse d'approche (vitesses s'additionnent car directions opposées)
    print("ÉTAPE 3: Vitesse d'approche des deux trains")
    vitesse_approche = v1 + v2
    print(f"   Vitesse d'approche = {v1} km/h + {v2} km/h = {vitesse_approche} km/h")
    print(f"   (Les vitesses s'additionnent car ils vont l'un vers l'autre)")
    print()
    
    # Étape 4: Temps pour se croiser après 14h30
    print("ÉTAPE 4: Temps pour se croiser (après 14h30)")
    temps_croisement = distance_restante / vitesse_approche
    print(f"   Temps = distance / vitesse = {distance_restante} km / {vitesse_approche} km/h")
    print(f"   Temps = {temps_croisement:.4f} heures")
    print(f"   Temps = {temps_croisement * 60:.1f} minutes")
    print()
    
    # Étape 5: Heure de croisement
    print("ÉTAPE 5: Heure de croisement")
    heures = int(temps_croisement)
    minutes = int((temps_croisement - heures) * 60)
    print(f"   14h30 + {heures}h{minutes:02d}min = 16h{16:02d}min")
    heure_croisement = 14.5 + temps_croisement
    print(f"   Heure exacte: {heure_croisement:.2f}h (≈ 16h16)")
    print()
    
    # Étape 6: Distance de Paris
    print("ÉTAPE 6: Distance de Paris au point de croisement")
    distance_paris = distance_train1_avant + (v1 * temps_croisement)
    print(f"   Distance = distance initiale + distance parcourue après 14h30")
    print(f"   Distance = {distance_train1_avant} km + ({v1} km/h × {temps_croisement:.4f} h)")
    print(f"   Distance = {distance_train1_avant} km + {v1 * temps_croisement:.1f} km")
    print(f"   Distance = {distance_paris:.1f} km de Paris")
    print()
    
    # Vérification
    print("✅ VÉRIFICATION:")
    distance_lyon = distance_totale - distance_paris
    distance_train2 = v2 * temps_croisement
    print(f"   - Train 1 a parcouru: {distance_paris:.1f} km depuis Paris")
    print(f"   - Train 2 a parcouru: {distance_train2:.1f} km depuis Lyon")
    print(f"   - Distance restante depuis Lyon: {distance_lyon:.1f} km")
    print(f"   - Vérification: {distance_train2:.1f} ≈ {distance_lyon:.1f} km ✓")
    print()
    
    print("=" * 80)
    print("🎯 RÉPONSE FINALE")
    print("=" * 80)
    print(f"   ⏰ Heure de croisement: 16h16")
    print(f"   📍 Distance de Paris: {distance_paris:.0f} km")
    print("=" * 80)
    print()
    
    return {
        'heure': '16h16',
        'distance': distance_paris,
        'temps_apres_14h30': temps_croisement * 60  # en minutes
    }

def compare_with_model_answer(model_answer):
    """
    Compare la réponse d'un modèle avec la solution correcte
    """
    correct = solve_train_problem()
    
    print("\n" + "=" * 80)
    print("📊 COMPARAISON AVEC LA RÉPONSE DU MODÈLE")
    print("=" * 80)
    print()
    
    print("✅ RÉPONSE CORRECTE:")
    print(f"   - Heure: {correct['heure']}")
    print(f"   - Distance: {correct['distance']:.0f} km de Paris")
    print()
    
    print("🤖 RÉPONSE DU MODÈLE:")
    print(model_answer)
    print()
    
    print("💡 CRITÈRES D'ÉVALUATION:")
    print("   - Heure proche de 16h16 (±10 min)")
    print("   - Distance proche de 272 km (±20 km)")
    print("   - Raisonnement étape par étape présent")
    print("   - Calculs intermédiaires corrects")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Si un argument est fourni, c'est la réponse du modèle
        model_answer = " ".join(sys.argv[1:])
        compare_with_model_answer(model_answer)
    else:
        # Sinon, juste afficher la solution
        solve_train_problem()
