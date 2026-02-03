# Est-ce que Trump a encore dit une connerie aujourd'hui ?

Site statique affichant si Trump a dit quelque chose de controversé aujourd'hui.

## Fonctionnalités

- **Indicateur Oui/Non** : Affiche si un événement a été enregistré aujourd'hui
- **Compteur de jours** : Nombre de jours depuis la dernière entrée
- **Titre automatique** : Le titre de l'article est récupéré automatiquement depuis l'URL

## Format des données

Fichier `data/events.md` :

```
YYYY-MM-DD URL
```

**Exemple :**
```
2026-02-03 https://example.com/article
2026-02-01 https://example.com/article2
```

## Construction

```bash
python3 build.py
```

## Déploiement

GitHub Actions déploie sur GitHub Pages :
- À chaque push sur `main`
- Quotidiennement à minuit UTC
- Manuellement via workflow_dispatch
