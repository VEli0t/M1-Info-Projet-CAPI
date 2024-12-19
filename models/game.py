def valider_vote(liste_vote, type_vote):
    """
    @brief Valide un vote en fonction du type de vote demandé.
    
    @param liste_vote La liste des votes exprimés (chaque élément représente un vote).
    @param type_vote Le type de validation à effectuer : 'unanime' ou 'majorite'.
    @return Un tuple contenant :
        - Un booléen indiquant si la validation est réussie.
        - La valeur majoritaire ou unanime, si applicable, sinon False.
    
    @details
    - Pour un vote unanime ('unanime'), tous les éléments de la liste doivent être identiques.
    - Pour un vote à la majorité absolue ('majorite'), un élément doit apparaître dans au moins la moitié des votes.
    """
    if not liste_vote:  # Vérifie si la liste est vide
        return (False, False)

    if type_vote == 'unanime':
        # Vérifie si tous les votes sont identiques en comparant les valeurs uniques
        return ((len(set(liste_vote)) <= 1), liste_vote[0])  # 'set' contient uniquement des valeurs uniques

    elif type_vote == 'majorite':  # Validation par majorité absolue
        # Parcourt chaque élément unique dans la liste
        for elem in set(liste_vote):
            # Vérifie si un élément apparaît au moins la moitié des fois
            if liste_vote.count(elem) >= len(liste_vote) / 2:
                return (True, elem)
        return (False, False)