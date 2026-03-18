"""
SM601 - Théorie des graphes
Projet : Recherche des chemins les plus courts
         à l'aide de l'algorithme de Floyd-Warshall
"""

import os
import sys

INF = float('inf')


# ─────────────────────────────────────────────
#  1. LECTURE DU FICHIER
# ─────────────────────────────────────────────

def lire_graphe(numero):
    """Charge un graphe depuis le fichier <numero>.txt et retourne (n, arcs).
    arcs est une liste de tuples (i, j, valeur).
    """
    nom_fichier = f"{numero}.txt"
    if not os.path.isfile(nom_fichier):
        print(f"  ✗ Fichier '{nom_fichier}' introuvable.")
        return None, None

    with open(nom_fichier, "r") as f:
        lignes = [l.strip() for l in f if l.strip() != ""]

    try:
        n = int(lignes[0])
        nb_arcs = int(lignes[1])
        arcs = []
        for i in range(2, 2 + nb_arcs):
            parts = lignes[i].split()
            u, v, w = int(parts[0]), int(parts[1]), int(parts[2])
            arcs.append((u, v, w))
    except (IndexError, ValueError) as e:
        print(f"  ✗ Erreur de lecture dans '{nom_fichier}' : {e}")
        return None, None

    return n, arcs


# ─────────────────────────────────────────────
#  2. CONSTRUCTION DES MATRICES INITIALES
# ─────────────────────────────────────────────

def construire_matrices(n, arcs):
    """Retourne (L, P) initiaux.
    L[i][j] = valeur de l'arc (i,j), INF si absent, 0 si i==j.
    P[i][j] = j si arc direct, None sinon.
    """
    L = [[INF] * n for _ in range(n)]
    P = [[None] * n for _ in range(n)]

    for i in range(n):
        L[i][i] = 0

    for (u, v, w) in arcs:
        L[u][v] = w
        P[u][v] = v

    return L, P


# ─────────────────────────────────────────────
#  3. AFFICHAGE MATRICIEL
# ─────────────────────────────────────────────

def _largeur_col(n):
    """Largeur de colonne adaptée au contenu possible."""
    return max(6, len(str(n - 1)) + 1)

def afficher_matrice_L(L, n, titre="L"):
    """Affiche la matrice des distances avec alignement."""
    col = _largeur_col(n)
    en_tete = " " * (col + 1) + "".join(str(j).rjust(col) for j in range(n))
    separateur = " " * (col + 1) + "-" * col * n
    print(f"\n  Matrice {titre} :")
    print(en_tete)
    print(separateur)
    for i in range(n):
        ligne = str(i).rjust(col) + " |"
        for j in range(n):
            val = L[i][j]
            if val == INF:
                ligne += "∞".rjust(col)
            else:
                ligne += str(val).rjust(col)
        print(ligne)

def afficher_matrice_P(P, n, titre="P"):
    """Affiche la matrice des prédécesseurs."""
    col = _largeur_col(n)
    en_tete = " " * (col + 1) + "".join(str(j).rjust(col) for j in range(n))
    separateur = " " * (col + 1) + "-" * col * n
    print(f"\n  Matrice {titre} :")
    print(en_tete)
    print(separateur)
    for i in range(n):
        ligne = str(i).rjust(col) + " |"
        for j in range(n):
            val = P[i][j]
            ligne += ("-" if val is None else str(val)).rjust(col)
        print(ligne)


# ─────────────────────────────────────────────
#  4. ALGORITHME DE FLOYD-WARSHALL
# ─────────────────────────────────────────────

def floyd_warshall(n, L0, P0):
    """Exécute Floyd-Warshall et affiche les matrices intermédiaires.
    Retourne (L_final, P_final).
    """
    # Copie des matrices initiales
    L = [row[:] for row in L0]
    P = [row[:] for row in P0]

    print("\n" + "=" * 60)
    print("  ALGORITHME DE FLOYD-WARSHALL — itérations")
    print("=" * 60)
    print("  (Matrices initiales k=0)")
    afficher_matrice_L(L, n, titre="L⁰")
    afficher_matrice_P(P, n, titre="P⁰")

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if L[i][k] != INF and L[k][j] != INF:
                    nouveau = L[i][k] + L[k][j]
                    if nouveau < L[i][j]:
                        L[i][j] = nouveau
                        P[i][j] = P[i][k]

        print(f"\n  --- Après itération k={k} (sommet intermédiaire {k}) ---")
        afficher_matrice_L(L, n, titre=f"L{k+1}")
        afficher_matrice_P(P, n, titre=f"P{k+1}")

    return L, P


# ─────────────────────────────────────────────
#  5. DÉTECTION DE CIRCUIT ABSORBANT
# ─────────────────────────────────────────────

def detecter_circuit_absorbant(L, n):
    """Retourne True si au moins un circuit absorbant est détecté (L[i][i] < 0)."""
    for i in range(n):
        if L[i][i] < 0:
            return True
    return False


# ─────────────────────────────────────────────
#  6. RECONSTRUCTION D'UN CHEMIN
# ─────────────────────────────────────────────

def reconstruire_chemin(P, src, dst, n):
    """Retourne la liste des sommets du chemin de src à dst, ou None si impossible."""
    if P[src][dst] is None:
        return None
    chemin = [src]
    courant = src
    visites = set()
    while courant != dst:
        if courant in visites:
            return None  # cycle détecté (sécurité)
        visites.add(courant)
        suivant = P[courant][dst]
        if suivant is None:
            return None
        chemin.append(suivant)
        courant = suivant
    return chemin

def afficher_chemin(L, P, src, dst, n):
    """Affiche le chemin minimal de src à dst."""
    if src < 0 or src >= n or dst < 0 or dst >= n:
        print(f"  ✗ Sommets invalides (les sommets vont de 0 à {n-1}).")
        return
    if src == dst:
        print(f"  Chemin de {src} à {dst} : {src}  (distance = 0)")
        return
    dist = L[src][dst]
    if dist == INF:
        print(f"  ✗ Aucun chemin de {src} à {dst}.")
        return
    chemin = reconstruire_chemin(P, src, dst, n)
    if chemin is None:
        print(f"  ✗ Impossible de reconstruire le chemin de {src} à {dst}.")
        return
    chemin_str = " → ".join(str(s) for s in chemin)
    print(f"  Chemin de {src} à {dst} : {chemin_str}  (distance = {dist})")


# ─────────────────────────────────────────────
#  7. AFFICHAGE GRAPHE INITIAL
# ─────────────────────────────────────────────

def afficher_graphe(n, arcs):
    print(f"\n  Graphe : {n} sommet(s), {len(arcs)} arc(s)")
    print("  Arcs :")
    for (u, v, w) in arcs:
        print(f"    {u} → {v}  (valeur = {w})")


# ─────────────────────────────────────────────
#  8. TRAITEMENT COMPLET D'UN GRAPHE
# ─────────────────────────────────────────────

def traiter_graphe(numero):
    print("\n" + "=" * 60)
    print(f"  GRAPHE N°{numero}")
    print("=" * 60)

    # Lecture
    n, arcs = lire_graphe(numero)
    if n is None:
        return

    # Affichage description
    afficher_graphe(n, arcs)

    # Construction matrices
    L0, P0 = construire_matrices(n, arcs)

    # Affichage matrice initiale
    print("\n  Matrice de valeurs initiale du graphe :")
    afficher_matrice_L(L0, n, titre="L⁰ (initiale)")

    # Floyd-Warshall
    L, P = floyd_warshall(n, L0, P0)

    # Résultat final
    print("\n" + "=" * 60)
    print("  RÉSULTAT FINAL")
    print("=" * 60)
    afficher_matrice_L(L, n, titre="L (finale)")
    afficher_matrice_P(P, n, titre="P (finale)")

    # Circuit absorbant ?
    if detecter_circuit_absorbant(L, n):
        print("\n  ⚠  Le graphe contient au moins un CIRCUIT ABSORBANT.")
        print("     Les chemins minimaux ne peuvent pas être déterminés.")
        return

    print("\n  ✓ Aucun circuit absorbant détecté.")

    # Affichage des chemins
    print("\n" + "=" * 60)
    print("  CONSULTATION DES CHEMINS MINIMAUX")
    print("=" * 60)

    while True:
        rep = input("\n  Voulez-vous afficher un chemin minimal ? (o/n) : ").strip().lower()
        if rep not in ("o", "oui", "y", "yes"):
            break
        try:
            src = int(input(f"  Sommet de départ  (0 à {n-1}) : "))
            dst = int(input(f"  Sommet d'arrivée  (0 à {n-1}) : "))
        except ValueError:
            print("  ✗ Entrée invalide, veuillez entrer des entiers.")
            continue
        afficher_chemin(L, P, src, dst, n)


# ─────────────────────────────────────────────
#  9. BOUCLE PRINCIPALE
# ─────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   SM601 – Théorie des graphes                           ║")
    print("║   Algorithme de Floyd-Warshall                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Les graphes sont lus depuis des fichiers texte nommés")
    print("  <numéro>.txt situés dans le répertoire courant.")

    while True:
        print("\n" + "-" * 60)
        rep = input("  Entrez le numéro du graphe à analyser (ou 'q' pour quitter) : ").strip()
        if rep.lower() in ("q", "quit", "exit"):
            print("\n  Au revoir !\n")
            break
        if not rep.isdigit():
            print("  ✗ Veuillez entrer un numéro entier positif.")
            continue
        traiter_graphe(rep)


if __name__ == "__main__":
    main()
