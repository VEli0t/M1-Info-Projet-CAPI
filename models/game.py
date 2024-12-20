def valider_vote(liste_vote, type_vote):
    """
    @brief Valide un vote en fonction du type de vote demandé.

    @param liste_vote La liste des votes exprimés (chaque élément représente un vote).
    @param type_vote Le type de validation à effectuer : 'unanime' ou 'majorite'.
    @return Un tuple contenant :
        - Un booléen indiquant si la validation est réussie.
        - La valeur majoritaire ou unanime, si applicable, sinon False.

    @details
    - Les votes "cafe" et "interro" sont traités comme des cas spécifiques.
    - Pour un vote 'unanime', tous les éléments doivent être identiques.
    - Pour un vote 'majorite', un élément doit apparaître dans au moins la moitié des votes.
    """
    # Liste des types de vote valides
    liste_type_vote = ['unanime', 'majorite']

    # Vérification des préconditions
    if not liste_vote:  # Vérifie si la liste est vide
        return (False, False)

    if type_vote not in liste_type_vote:  # Vérifie si le type de vote est valide
        raise AttributeError(f"Type de vote non supporté : '{type_vote}'. Types valides : {liste_type_vote}")

    # Gestion des votes spéciaux "cafe" et "interro"
    resultat_special = gerer_votes_speciaux(liste_vote, type_vote)
    if resultat_special is not None:
        return resultat_special

    # Filtrer les votes spéciaux avant de continuer
    votes_sans_speciaux = [v for v in liste_vote if v not in ["cafe", "interro"]]

    # Validation des votes restants
    if type_vote == 'unanime':
        return valider_unanimite(votes_sans_speciaux)
    elif type_vote == 'majorite':
        return valider_majorite(votes_sans_speciaux)


def gerer_votes_speciaux(liste_vote, type_vote):
    """
    @brief Gère les votes spéciaux ("cafe" et "interro") selon le type de vote.

    @param liste_vote La liste des votes exprimés.
    @param type_vote Le type de validation à effectuer : 'unanime' ou 'majorite'.
    @return Un tuple si un cas spécial est détecté, sinon None.
    """
    if type_vote == 'unanime':
        if all(v == "cafe" for v in liste_vote):
            return (True, "cafe")
        if all(v == "interro" for v in liste_vote):
            return (True, "interro")

    elif type_vote == 'majorite':
        if liste_vote.count("cafe") > len(liste_vote) / 2:
            return (True, "cafe")
        if liste_vote.count("interro") > len(liste_vote) / 2:
            return (True, "interro")

    return None


def valider_unanimite(votes):
    """
    @brief Valide un vote unanime.

    @param votes La liste des votes après filtrage des votes spéciaux.
    @return Un tuple contenant :
        - Un booléen indiquant si la validation est réussie.
        - La valeur unanime, sinon False.
    """
    if len(set(votes)) == 1 and votes:
        return (True, votes[0])
    return (False, False)


def valider_majorite(votes):
    """
    @brief Valide un vote à la majorité absolue.

    @param votes La liste des votes après filtrage des votes spéciaux.
    @return Un tuple contenant :
        - Un booléen indiquant si la validation est réussie.
        - La valeur majoritaire, sinon False.
    """
    for elem in set(votes):
        if votes.count(elem) > len(votes) / 2:
            return (True, elem)
    return (False, False)