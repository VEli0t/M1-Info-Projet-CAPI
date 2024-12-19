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