# 🌟 ServiceLink — Plateforme de Services à Abidjan

> Plateforme numérique mettant en relation clients et prestataires de services à Abidjan, Côte d'Ivoire.

---

## 🏗️ Stack Technique

| Couche | Technologie |
|---|---|
| Backend | Django 4.x + Django REST Framework + JWT |
| Frontend | React 18 + Redux Toolkit |
| Base de données | MySQL 8 |
| Auth | djangorestframework-simplejwt |
| Médias | Pillow (photos profil, messages) |

---

## 📁 Structure du projet

```
servicelink/
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── users/
│   │   ├── models.py        ← Utilisateur, Client, Prestataire, Favori
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── services/
│   │   ├── models.py        ← Categorie, Metier, Commune, Service
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── reservations/
│   │   ├── models.py        ← Reservation, Avis, Message
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── media/               ← Photos uploadées
│
└── frontend/
    └── src/
        ├── pages/
        │   ├── Accueil.js           ← Carrousel + Hero + CTA
        │   ├── Connexion.js
        │   ├── InscriptionClient.js
        │   ├── InscriptionPrestataire.js  ← 2 étapes, cases communes
        │   ├── Recherche.js         ← Filtres + favoris sur cards
        │   ├── ProfilPrestataire.js ← Stats + avis + favoris
        │   ├── Reservation.js
        │   ├── TableauBordClient.js ← Réservations + favoris + paiement
        │   ├── TableauBordPrestataire.js  ← Demandes + code validation
        │   └── Paiement.js          ← Simulation Orange/MTN/Wave
        ├── components/
        │   ├── Navbar.js
        │   ├── Logo.js
        │   └── Chat.js              ← Messagerie complète
        └── store/
            └── authSlice.js
```

---

## 🔑 Fonctionnalités clés

### 👤 Utilisateurs
- Inscription Client / Prestataire (2 étapes)
- Authentification JWT
- Photo de profil (upload)

### 🔍 Recherche
- Filtres : catégorie, commune, note, premium
- Bouton ❤️ favoris sur chaque card
- Prix de départ visible

### 📅 Réservations
- Réservation directe ou devis
- Statuts : en_attente → confirmee → terminee
- Annulation possible

### 💬 Messagerie (Chat.js)
- Messages texte
- Envoi de photos 📷
- Localisation GPS 📍
- Modifier / Supprimer (clic droit → menu contextuel)
- Agrandir / Réduire / Minimiser

### 💳 Paiement Séquestre
- Simulation Orange Money 🟠 / MTN MoMo 🟡 / Wave 🔵
- Argent bloqué chez ServiceLink
- Code de validation généré (ex: SL4892)
- Commission 5% automatique
- Système de litige

### ❤️ Favoris
- Ajouter/Retirer depuis la recherche ou le profil
- Liste dans le tableau de bord client

### ⭐ Avis
- Note 1-5 étoiles
- Barre de progression par note
- Stats : missions, note moyenne, membre depuis

---

## 🎨 Charte graphique

| Élément | Couleur |
|---|---|
| Bleu principal | `#1A3C6E` |
| Vert prestataire | `#065f46` |
| Jaune accent | `#F59E0B` |
| Fond | `#F8FAFC` |
| Police | Poppins |

---

## 🚀 Lancer le projet

### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

---

## 🔐 Comptes de test

| Rôle | Email | Statut |
|---|---|---|
| Client | laure@gmail.com | Actif |
| Prestataire | fidelkouassi@gmail.com | Actif |

---

## 📡 Endpoints principaux

```
POST   /api/users/inscription/client/
POST   /api/users/inscription/prestataire/
POST   /api/users/connexion/
GET    /api/users/prestataire/<id>/
POST   /api/users/favoris/<id>/
POST   /api/users/prestataire/photo/

GET    /api/services/recherche/
GET    /api/services/categories/
GET    /api/services/communes/

POST   /api/reservations/creer/
GET    /api/reservations/mes-reservations/
POST   /api/reservations/<id>/payer/
POST   /api/reservations/<id>/valider-code/
POST   /api/reservations/<id>/litige/
POST   /api/reservations/messages/envoyer/
POST   /api/reservations/messages/photo/
```

---

---

## 🤖 PROMPT POUR CLAUDE (VS Code)

> **Copie ce prompt dans Claude de ton IDE pour les retouches finales :**

---

```
Tu es un expert React/UI designer. Tu vas améliorer l'interface de ServiceLink,
une plateforme de services à Abidjan (Côte d'Ivoire).

## Fichiers à améliorer

Parcours et améliore ces fichiers dans cet ordre :

1. src/components/Chat.js
2. src/pages/TableauBordClient.js
3. src/pages/TableauBordPrestataire.js
4. src/pages/Paiement.js
5. src/pages/Accueil.js

## Améliorations à apporter

### 1. Icônes et visuels

MESSAGERIE (Chat.js) :
- Remplace le bouton "Messages" par une icône bulle de chat style WhatsApp
  avec un badge de notification rouge si non lus
- Le bouton d'envoi doit ressembler au bouton send de WhatsApp (rond, bleu/vert)
- L'icône 📷 photo et 📍 localisation doivent être des icônes modernes
  style WhatsApp (utilise react-icons/fi ou des emojis stylisés)

PAIEMENT (Paiement.js) :
- Orange Money : affiche un cercle orange avec "OM" en blanc en gras
  à la place du emoji 🟠. Style officiel Orange Money.
- MTN MoMo : affiche un cercle jaune avec "MTN" en noir en gras.
  Style officiel MTN.
- Wave : affiche un cercle bleu ciel avec "W~" en blanc en gras.
  Style officiel Wave.
- Chaque carte de mode de paiement doit avoir une ombre colorée
  correspondant à la couleur de l'opérateur au hover.

TABLEAU DE BORD CLIENT (TableauBordClient.js) :
- Le bouton "💳 Payer" doit avoir une icône carte bancaire animée
- Le code de validation doit être affiché dans une box style SMS/OTP
  avec chaque lettre dans sa propre case (comme les codes OTP)
- Le bouton "❤️ Favoris" dans la sidebar doit avoir un compteur badge

TABLEAU DE BORD PRESTATAIRE (TableauBordPrestataire.js) :
- La zone de saisie du code doit ressembler à un vrai input OTP
  avec 6 cases séparées, une lettre par case
- Quand le code est validé, afficher une animation de succès
  (coche verte qui apparaît)
- Le badge "🔒 Fonds sécurisés" doit être plus visible avec
  une animation de pulsation

PAGE ACCUEIL (Accueil.js) :
- Les tags "Plombier", "Électricien" etc. doivent avoir des emojis
  correspondants : 🔧 Plombier, ⚡ Électricien, ✂️ Coiffeur, 🪚 Menuisier
- Le formulaire de recherche flottant doit avoir un effet glassmorphism
  (backdrop-filter: blur)

### 2. Micro-animations
- Ajouter une animation de chargement skeleton sur les listes
- Les boutons doivent avoir un effet de "press" (scale 0.97) au clic
- Les cards doivent avoir une transition plus fluide au hover

### 3. Cohérence visuelle
- Tous les avatars doivent avoir le même style (initiales centrées,
  gradient de couleur selon le rôle)
- Les badges de statut (En attente, Confirmée, etc.) doivent avoir
  des icônes cohérentes

## Contraintes
- Ne pas changer la logique métier
- Ne pas modifier les appels API
- Garder la police Poppins
- Garder la charte graphique : #1A3C6E (bleu), #F59E0B (jaune), #065f46 (vert)
- Le code doit rester lisible et maintenable
- Utiliser uniquement des bibliothèques déjà installées :
  react-icons/fi, inline styles React

## Important
Améliore fichier par fichier en expliquant brièvement ce que tu as changé.
Commence par Chat.js.
```

---

*README généré le 26/05/2026 — ServiceLink v1.0*