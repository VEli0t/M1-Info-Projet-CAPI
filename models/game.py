def valider_vote(liste_vote, type_vote):
    if not liste_vote: # si la liste est vide
        return (False, False)
    if type_vote == 'unanime':
        return ((len(set(liste_vote)) <= 1), liste_vote[0]) # un set ne contient que des valeurs différentes
    elif type_vote == 'majorite': # Majorité absolue
        for elem in set(liste_vote):  # Parcourir chaque élément unique
            if liste_vote.count(elem) >= len(liste_vote) / 2:
                return (True, elem)
        return (False, False)
    
