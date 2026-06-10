# G-360 — Gestion Commerciale pour PME

> Application web de gestion commerciale destinée aux petits commerces du Sénégal.
> Développée avec Django, PostgreSQL et Docker.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black)

---

## Fonctionnalités

- Authentification sécurisée par boutique
- Gestion du stock — entrées, sorties, alertes de rupture
- Ventes & Factures — génération PDF, paiement partiel
- Suivi des clients et des dettes
- Tableau de bord dynamique avec statistiques
- Historique complet des mouvements
- Interface trilingue — Français, Wolof, Italien
- Modes de paiement — Cash, Orange Money, Wave

---

## Stack technique

| Technologie | Usage |
|---|---|
| Python 3.12 | Langage principal |
| Django 6 | Framework web |
| PostgreSQL | Base de données |
| Docker & Docker Compose | Containerisation |
| GitHub Actions | CI/CD |
| WeasyPrint | Génération PDF |
| Gunicorn | Serveur de production |
| WhiteNoise | Fichiers statiques |

---

## Installation locale

### Prérequis
- Python 3.12+
- Docker & Docker Compose
- Git

### Avec Docker (recommandé)

```bash
git clone git@github.com:Fred0242/G-360.git
cd G-360
cp .env.example .env
docker-compose up --build
```

Accès : http://localhost:8000

### Sans Docker

```bash
git clone git@github.com:Fred0242/G-360.git
cd G-360
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Variables d'environnement

Crée un fichier `.env` à la racine :

```env
SECRET_KEY=ta-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

---

## Structure du projet
G-360/
├── core/           → Configuration Django
├── dashboard/      → Tableau de bord
├── clients/        → Gestion clients & dettes
├── produits/       → Stock & mouvements
├── factures/       → Ventes & factures PDF
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
---

## CI/CD

Chaque push sur `main` déclenche automatiquement :

1. Tests Django automatisés
2. Build de l'image Docker
3. Déploiement en production

---

## Auteur

**Franchir Madzou**
Étudiant Web Solution Architecture — ITS ICT Piemonte, Torino
GitHub : [@Fred0242](https://github.com/Fred0242)
Portfolio : [fred0242.github.io](https://fred0242.github.io)
