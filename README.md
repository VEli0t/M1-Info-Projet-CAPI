# M1-Info-Projet-CAPI

Ce projet est développé dans le cadre du cours de **Conception Agile de Projets Informatiques** du Master 1 Informatique.
Il s'agit d'une application de **Planning Poker**, une méthode utilisée pour estimer l'effort ou la complexité des tâches dans le développement logiciel.

## Fonctionnalités

- **Définition des paramètres de la partie** :
  - Définir le nombre de joueurs.
  - Saisir un pseudo pour chaque joueur.
  - Choisir parmi plusieurs règles de Planning Poker (strictes, moyenne, médiane).

- **Proposition de fonctionnalités** :
  - Proposer des fonctionnalités à estimer.
  - Visualiser les fonctionnalités déjà proposées.
  - Supprimer des fonctionnalités si nécessaire.

- **Système de vote** :
  - Voter pour une fonctionnalité à l'aide d'un système de cartes.
  - Validation automatique des estimations selon les règles choisies.
  - Possibilité de revoter si une estimation n'est pas validée.

- **Interface utilisateur** :
  - Utilisation en mode local (tour par tour sur un seul dispositif).
  - Navigation via un menu ergonomique regroupant toutes les options.

- **Fonctionnalités supplémentaires** :
  - Chronomètre pour limiter le temps de vote.
  - Espace de chat intégré pour discuter avec les autres joueurs.

- **Gestion du backlog** :
  - Chargement d'une liste de fonctionnalités au format JSON.
  - Exportation du backlog complété avec les estimations en fichier JSON.
  - Sauvegarde de l'état d'avancement si tous les joueurs choisissent la carte café.
  - Reprise d'une partie après une pause café.

## Installation

1. **Cloner le dépôt** :

   ```bash
   git clone https://github.com/VEli0t/M1-Info-Projet-CAPI.git
   cd M1-Info-Projet-CAPI
   ```

2. **Créer et activer un environnement virtuel** :

   ```bash
   python -m venv env
   # Sous Windows
   env\Scripts\activate.bat
   # Sous Unix ou MacOS
   source env/bin/activate
   ```

3. **Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

1. **Lancer l'application** :

   ```bash
   python app.py
   ```

2. **Accéder à l'application** :

   Ouvrez votre navigateur et rendez-vous sur `http://127.0.0.1:5000/`.

## Tests

Des tests unitaires sont disponibles pour vérifier le bon fonctionnement de l'application.
Pour les exécuter :

```bash
pytest
```

## Auteurs

- **VEli0t** - [Profil GitHub](https://github.com/VEli0t)
- **PaulP01** - [Profil GitHub](https://github.com/PaulP01)
