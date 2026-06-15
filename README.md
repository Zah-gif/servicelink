# ServiceLink

**Plateforme numérique de mise en relation entre clients et prestataires de services à Abidjan**

ServiceLink est une application web full-stack qui permet aux habitants d'Abidjan de trouver, réserver et payer des prestataires de services vérifiés (plombiers, électriciens, coiffeurs, menuisiers, aides-ménagères, etc.), tout en garantissant la confiance et la sécurité des transactions grâce à un système de paiement sous séquestre.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture technique](#architecture-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration de la base de données](#configuration-de-la-base-de-données)
- [Lancement du projet](#lancement-du-projet)
- [Structure du projet](#structure-du-projet)
- [Principales routes API](#principales-routes-api)
- [Comptes de test](#comptes-de-test)
- [Auteur](#auteur)

---

## Fonctionnalités

### Pour les clients
- Inscription et authentification sécurisée (JWT)
- Recherche de prestataires par catégorie, métier et commune
- Consultation des profils détaillés (services, tarifs, avis, note moyenne)
- Réservation en ligne et suivi des demandes
- Paiement sécurisé via Mobile Money (Orange Money, MTN MoMo, Wave)
- Système de paiement sous séquestre avec code de validation
- Dépôt d'avis après une prestation terminée
- Gestion d'une liste de favoris
- Messagerie avec les prestataires

### Pour les prestataires
- Inscription avec création d'un premier service
- Gestion des services proposés (création, activation/désactivation)
- Réception et confirmation des demandes (avec fixation du montant)
- Validation des paiements par code
- Gestion de la photo de profil
- Souscription à un abonnement Premium (visibilité accrue)

### Pour l'administrateur
- Interface d'administration complète (Django Admin)
- Gestion des utilisateurs, services, réservations et avis
- Vérification des prestataires et activation du statut Premium
- Consultation des messages de contact

---

## Architecture technique

ServiceLink repose sur une architecture client-serveur découplée.

| Composant | Technologie |
|-----------|-------------|
| Backend / API REST | Django & Django REST Framework (Python) |
| Authentification | JSON Web Tokens (JWT) |
| Frontend | React.js & Redux |
| Base de données | MySQL |
| Gestion d'état | Redux Toolkit |
| Requêtes HTTP | Axios |

---

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- Python 3.12 ou supérieur
- Node.js 18 ou supérieur
- MySQL 8.0 ou supérieur
- Git

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/VOTRE-UTILISATEUR/servicelink.git
cd servicelink
```

### 2. Configuration du backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration du frontend

```bash
cd frontend
npm install
```

---

## Configuration de la base de données

### 1. Créer la base de données MySQL

```sql
CREATE DATABASE servicelink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configurer les paramètres de connexion

Dans le fichier de configuration Django (`backend/servicelink/settings.py`), renseignez vos identifiants MySQL :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'servicelink',
        'USER': 'votre_utilisateur',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Appliquer les migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un super-utilisateur (administrateur)

```bash
python manage.py createsuperuser
```

### 5. (Optionnel) Peupler la base avec des données de test

```bash
python populate_db.py
```

---

## Lancement du projet

### Démarrer le backend (port 8000)

```bash
cd backend
python manage.py runserver
```

L'API est accessible sur `http://localhost:8000/`
L'interface d'administration sur `http://localhost:8000/admin/`

### Démarrer le frontend (port 3000)

```bash
cd frontend
npm start
```

L'application est accessible sur `http://localhost:3000/`

---

## Structure du projet

```
servicelink/
├── backend/
│   ├── servicelink/        # Configuration du projet Django
│   ├── users/              # Gestion des utilisateurs, clients, prestataires
│   ├── services/           # Catégories, métiers, communes, services
│   ├── reservations/       # Réservations, avis, messagerie
│   ├── payments/           # Paiements et abonnements Premium
│   ├── populate_db.py      # Script de peuplement de la base
│   └── manage.py
│
└── frontend/
    ├── public/
    └── src/
        ├── api/            # Configuration Axios
        ├── components/     # Composants réutilisables
        ├── pages/          # Pages de l'application
        ├── store/          # Configuration Redux
        └── assets/         # Images et ressources
```

---

## Principales routes API

### Authentification
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/users/inscription/client/` | Inscription d'un client |
| POST | `/api/users/inscription/prestataire/` | Inscription d'un prestataire |
| POST | `/api/users/connexion/` | Connexion |
| GET | `/api/users/profil/` | Profil de l'utilisateur connecté |

### Services
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/services/recherche/` | Recherche de prestataires |
| GET | `/api/services/categories/` | Liste des catégories |
| GET | `/api/services/communes/` | Liste des communes |

### Réservations
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/reservations/creer/` | Créer une réservation |
| POST | `/api/reservations/<id>/confirmer/` | Confirmer et fixer le montant |
| POST | `/api/reservations/<id>/payer/` | Payer (séquestre) |
| POST | `/api/reservations/<id>/valider-code/` | Valider par code |

### Paiements
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/payments/abonnement/souscrire/` | Souscrire un abonnement Premium |

---

## Comptes de test

Après avoir exécuté le script de peuplement, vous pouvez utiliser les comptes suivants (mot de passe : `ServiceLink2025!`) :

| Rôle | Email |
|------|-------|
| Client | laure@gmail.com |
| Prestataire | fidelkouassi@gmail.com |

> Ces identifiants sont générés par le script de peuplement et destinés uniquement aux tests.

---

## Sécurité

- Authentification par jetons JWT
- Système de paiement sous séquestre (les fonds sont bloqués jusqu'à validation)
- Contrôle des accès par rôle (client / prestataire / administrateur)
- Commission de 5 % prélevée par la plateforme à la libération des fonds

---

## Auteur

**Zah Bi Zah Wilfried Vianney**
Master 1 — Génie Informatique
Université Nangui Abrogoua, Abidjan, Côte d'Ivoire

Projet académique réalisé dans le cadre du cours de développement web.

---

## Licence

Ce projet est réalisé dans un cadre académique.