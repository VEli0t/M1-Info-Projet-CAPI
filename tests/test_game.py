import pytest
from models.game import valider_vote


def test_valider_vote_unanime_success():
    """
    Test de la fonction valider_vote avec un vote unanime.
    Vérifie que la validation réussit si tous les votes sont identiques.
    """
    votes = [5, 5, 5]
    result, value = valider_vote(votes, 'unanime')
    assert result is True
    assert value == 5


def test_valider_vote_unanime_fail():
    """
    Test de la fonction valider_vote avec un vote unanime échoué.
    Vérifie que la validation échoue si les votes ne sont pas identiques.
    """
    votes = [5, 3, 5]
    result, _ = valider_vote(votes, 'unanime')
    assert result is False


def test_valider_vote_majorite_success():
    """
    Test de la fonction valider_vote avec un vote à la majorité simple réussi.
    Vérifie que la validation réussit si un élément atteint la majorité.
    """
    votes = [3, 3, 2]
    result, value = valider_vote(votes, 'majorite')
    assert result is True
    assert value == 3


def test_valider_vote_majorite_fail():
    """
    Test de la fonction valider_vote avec un vote à la majorité échoué.
    Vérifie que la validation échoue si aucun élément n'atteint la majorité.
    """
    votes = [3, 4, 5]
    result, _ = valider_vote(votes, 'majorite')
    assert result is False


def test_valider_vote_empty_list():
    """
    Test de la fonction valider_vote avec une liste vide.
    Vérifie que la validation échoue si la liste est vide.
    """
    votes = []
    result, _ = valider_vote(votes, 'unanime')
    assert result is False

    result, _ = valider_vote(votes, 'majorite')
    assert result is False


def test_valider_vote_invalid_type():
    """
    Test de la fonction valider_vote avec un type de vote non supporté.
    Vérifie que la validation échoue si le type de vote est incorrect.
    """
    votes = [3, 3, 2]
    with pytest.raises(AttributeError):
        valider_vote(votes, 'invalide')


def test_valider_vote_edge_case_majorite():
    """
    Test de la fonction valider_vote pour un cas limite de majorité.
    Vérifie que la validation réussit si un élément atteint juste la moitié.
    """
    votes = [3, 3, 3, 2, 2]
    result, value = valider_vote(votes, 'majorite')
    assert result is True
    assert value == 3


import pytest
from models.game import valider_vote


def test_tous_interro_unanime():
    """
    @brief Teste si la fonction détecte correctement que tous les joueurs ont voté "interro" en mode 'unanime'.
    """
    votes = ["interro", "interro", "interro"]
    resultat, valeur = valider_vote(votes, "unanime")
    assert resultat is True
    assert valeur == "interro"


def test_majorite_interro():
    """
    @brief Teste si la fonction détecte une majorité de votes "interro" en mode 'majorite'.
    """
    votes = ["interro", "interro", "1"]
    resultat, valeur = valider_vote(votes, "majorite")
    assert resultat is True
    assert valeur == "interro"


def test_pas_majorite_interro():
    """
    @brief Vérifie qu'il n'y a pas de majorité pour "interro".
    """
    votes = ["interro", "1", "2"]
    resultat, valeur = valider_vote(votes, "majorite")
    assert resultat is False
    assert valeur is False


def test_retire_interro_avant_unanime():
    """
    @brief Vérifie que les votes "interro" sont retirés avant de valider les autres votes en mode 'unanime'.
    """
    votes = ["1", "interro", "1"]
    resultat, valeur = valider_vote(votes, "unanime")
    assert resultat is True
    assert valeur == "1"


def test_retire_interro_avant_majorite():
    """
    @brief Vérifie que les votes "interro" sont retirés avant de valider les autres votes en mode 'majorite'.
    """
    votes = ["1", "interro", "1", "1"]
    resultat, valeur = valider_vote(votes, "majorite")
    assert resultat is True
    assert valeur == "1"


def test_mix_cafe_et_interro():
    """
    @brief Teste que la fonction gère correctement un mélange de votes "cafe" et "interro".
    """
    votes = ["cafe", "interro", "cafe", "interro"]
    resultat, valeur = valider_vote(votes, "majorite")
    assert resultat is False
    assert valeur is False
