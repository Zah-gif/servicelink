-- ============================================================
--  ServiceLink — Script SQL MySQL
--  Généré depuis le MCD/MLD MERISE
--  Auteur : Zah Bi Zah Wilfried Vianney
--  Encadrant : Docteur Zézé
--  Date : 2025
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS intervient_dans;
DROP TABLE IF EXISTS MESSAGE;
DROP TABLE IF EXISTS AVIS;
DROP TABLE IF EXISTS PAIEMENT;
DROP TABLE IF EXISTS RESERVATION;
DROP TABLE IF EXISTS ABONNEMENT;
DROP TABLE IF EXISTS PRESTATAIRE;
DROP TABLE IF EXISTS CLIENT;
DROP TABLE IF EXISTS UTILISATEUR;
DROP TABLE IF EXISTS METIER;
DROP TABLE IF EXISTS CATEGORIE;
DROP TABLE IF EXISTS COMMUNE;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
--  1. UTILISATEUR  (entité mère de l'héritage XT)
-- ============================================================
CREATE TABLE UTILISATEUR (
    id_utilisateur  INT AUTO_INCREMENT PRIMARY KEY,
    nom             VARCHAR(50)  NOT NULL,
    prenoms         VARCHAR(50)  NOT NULL,
    email           VARCHAR(50)  NOT NULL UNIQUE,
    telephone       VARCHAR(50)  NOT NULL UNIQUE,
    mot_de_passe    VARCHAR(255) NOT NULL,
    est_actif       BOOLEAN      NOT NULL DEFAULT TRUE,
    date_inscription DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  2. CLIENT  (entité fille — héritage XT)
-- ============================================================
CREATE TABLE CLIENT (
    id_client           INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur      INT          NOT NULL UNIQUE,
    commune_residence   VARCHAR(50),
    CONSTRAINT fk_client_utilisateur
        FOREIGN KEY (id_utilisateur) REFERENCES UTILISATEUR(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  3. CATEGORIE
-- ============================================================
CREATE TABLE CATEGORIE (
    id_categorie    INT AUTO_INCREMENT PRIMARY KEY,
    nom_categorie   VARCHAR(50)  NOT NULL UNIQUE,
    icone           VARCHAR(100),
    est_active      BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  4. METIER
-- ============================================================
CREATE TABLE METIER (
    id_metier       INT AUTO_INCREMENT PRIMARY KEY,
    id_categorie    INT          NOT NULL,
    nom_metier      VARCHAR(80)  NOT NULL,
    est_actif       BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_metier_categorie
        FOREIGN KEY (id_categorie) REFERENCES CATEGORIE(id_categorie)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  5. COMMUNE
-- ============================================================
CREATE TABLE COMMUNE (
    id_commune      INT AUTO_INCREMENT PRIMARY KEY,
    nom_commune     VARCHAR(50)     NOT NULL UNIQUE,
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  6. PRESTATAIRE  (entité fille — héritage XT)
-- ============================================================
CREATE TABLE PRESTATAIRE (
    id_prestataire      INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur      INT          NOT NULL UNIQUE,
    id_metier           INT          NOT NULL,
    id_categorie        INT          NOT NULL,
    description         TEXT,
    photo_profil        VARCHAR(255),
    est_premium         BOOLEAN      NOT NULL DEFAULT FALSE,
    est_verifie         BOOLEAN      NOT NULL DEFAULT FALSE,
    date_fin_premium    DATE,
    note_moyenne        DECIMAL(4,2) DEFAULT 0.00,
    badge_top           BOOLEAN      NOT NULL DEFAULT FALSE,
    nombre_avis         INT          NOT NULL DEFAULT 0,
    est_actif           BOOLEAN      NOT NULL DEFAULT TRUE,
    est_disponible      BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_prestataire_utilisateur
        FOREIGN KEY (id_utilisateur) REFERENCES UTILISATEUR(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_prestataire_metier
        FOREIGN KEY (id_metier) REFERENCES METIER(id_metier)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prestataire_categorie
        FOREIGN KEY (id_categorie) REFERENCES CATEGORIE(id_categorie)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  7. ABONNEMENT
-- ============================================================
CREATE TABLE ABONNEMENT (
    id_abonnement   INT AUTO_INCREMENT PRIMARY KEY,
    id_prestataire  INT          NOT NULL,
    type_offre      VARCHAR(20)  NOT NULL COMMENT 'mensuel ou annuel',
    montant_paye    DECIMAL(10,2) NOT NULL,
    date_debut      DATE         NOT NULL,
    date_fin        DATE         NOT NULL,
    est_actif       BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_abonnement_prestataire
        FOREIGN KEY (id_prestataire) REFERENCES PRESTATAIRE(id_prestataire)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  8. INTERVIENT_DANS  (table de liaison PRESTATAIRE ↔ COMMUNE)
-- ============================================================
CREATE TABLE intervient_dans (
    id_prestataire  INT NOT NULL,
    id_commune      INT NOT NULL,
    PRIMARY KEY (id_prestataire, id_commune),
    CONSTRAINT fk_intervient_prestataire
        FOREIGN KEY (id_prestataire) REFERENCES PRESTATAIRE(id_prestataire)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_intervient_commune
        FOREIGN KEY (id_commune) REFERENCES COMMUNE(id_commune)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  9. RESERVATION
-- ============================================================
CREATE TABLE RESERVATION (
    id_reservation      INT AUTO_INCREMENT PRIMARY KEY,
    id_client           INT          NOT NULL,
    id_prestataire      INT          NOT NULL,
    type_demande        VARCHAR(20)  NOT NULL COMMENT 'directe ou devis',
    statut              VARCHAR(20)  NOT NULL DEFAULT 'en_attente'
                        COMMENT 'en_attente, confirmee, en_cours, terminee, annulee',
    description_besoin  TEXT,
    date_souhaitee      DATE,
    montant             DECIMAL(12,2),
    date_creation       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_confirmation   DATETIME,
    CONSTRAINT fk_reservation_client
        FOREIGN KEY (id_client) REFERENCES CLIENT(id_client)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reservation_prestataire
        FOREIGN KEY (id_prestataire) REFERENCES PRESTATAIRE(id_prestataire)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  10. PAIEMENT
-- ============================================================
CREATE TABLE PAIEMENT (
    id_paiement         INT AUTO_INCREMENT PRIMARY KEY,
    id_reservation      INT          NOT NULL UNIQUE,
    montant_paye        DECIMAL(10,2) NOT NULL,
    operateur           VARCHAR(20)  NOT NULL COMMENT 'orange, mtn, wave, moov',
    statut_paiement     VARCHAR(50)  NOT NULL DEFAULT 'en_attente'
                        COMMENT 'en_attente, confirme, reverse, bloque',
    reference_paiement  VARCHAR(100) UNIQUE,
    date_paiement       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_reversement    DATETIME,
    CONSTRAINT fk_paiement_reservation
        FOREIGN KEY (id_reservation) REFERENCES RESERVATION(id_reservation)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  11. AVIS
-- ============================================================
CREATE TABLE AVIS (
    id_avis         INT AUTO_INCREMENT PRIMARY KEY,
    id_reservation  INT          NOT NULL UNIQUE,
    note            INT          NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire     TEXT,
    date_avis       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    est_modere      BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_avis_reservation
        FOREIGN KEY (id_reservation) REFERENCES RESERVATION(id_reservation)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  12. MESSAGE
-- ============================================================
CREATE TABLE MESSAGE (
    id_message      INT AUTO_INCREMENT PRIMARY KEY,
    id_reservation  INT          NOT NULL,
    id_expediteur   INT          NOT NULL,
    id_destinataire INT          NOT NULL,
    contenu         TEXT         NOT NULL,
    date_envoi      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    est_lu          BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_message_reservation
        FOREIGN KEY (id_reservation) REFERENCES RESERVATION(id_reservation)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_message_expediteur
        FOREIGN KEY (id_expediteur) REFERENCES UTILISATEUR(id_utilisateur)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_message_destinataire
        FOREIGN KEY (id_destinataire) REFERENCES UTILISATEUR(id_utilisateur)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  DONNÉES DE TEST — 10 Communes d'Abidjan
-- ============================================================
INSERT INTO COMMUNE (nom_commune, latitude, longitude) VALUES
('Cocody',      5.3599517,  -3.9951919),
('Yopougon',    5.3364430,  -4.0752500),
('Plateau',     5.3196853,  -4.0166010),
('Marcory',     5.2980000,  -3.9980000),
('Treichville', 5.2980000,  -4.0070000),
('Adjamé',      5.3580000,  -4.0260000),
('Abobo',       5.4150000,  -4.0160000),
('Koumassi',    5.2900000,  -3.9730000),
('Port-Bouët',  5.2550000,  -3.9270000),
('Attécoubé',   5.3330000,  -4.0500000);

-- ============================================================
--  DONNÉES DE TEST — Catégories et Métiers
-- ============================================================
INSERT INTO CATEGORIE (nom_categorie, icone, est_active) VALUES
('Artisanat',           'artisanat.png',    TRUE),
('Travaux à domicile',  'travaux.png',      TRUE),
('Beauté & Bien-être',  'beaute.png',       TRUE),
('Réparation',          'reparation.png',   TRUE),
('Ménage & Entretien',  'menage.png',       TRUE);

INSERT INTO METIER (id_categorie, nom_metier, est_actif) VALUES
(1, 'Menuisier',            TRUE),
(1, 'Maçon',                TRUE),
(1, 'Soudeur',              TRUE),
(2, 'Plombier',             TRUE),
(2, 'Électricien',          TRUE),
(2, 'Peintre',              TRUE),
(3, 'Coiffeur',             TRUE),
(3, 'Esthéticienne',        TRUE),
(4, 'Technicien électro',   TRUE),
(4, 'Mécanicien',           TRUE),
(5, 'Aide ménagère',        TRUE),
(5, 'Jardinier',            TRUE);

-- ============================================================
--  FIN DU SCRIPT
-- ============================================================
