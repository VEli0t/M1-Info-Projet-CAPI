class ExampleClass:
    """
    \brief Une classe d'exemple pour démontrer Doxygen.
    
    Cette classe illustre comment structurer des commentaires
    pour la documentation automatique avec Doxygen.
    """
    
    def __init__(self, value):
        """
        \brief Constructeur de la classe ExampleClass.
        
        \param value Une valeur à attribuer à l'instance.
        """
        self.value = value

    def example_method(self):
        """
        \brief Une méthode d'exemple.

        \return Retourne la valeur de l'instance.
        """
        return self.value
