# Est-ce que Trump a encore dit une connerie aujourd'hui ?

Site statique affichant si Trump a dit quelque chose de controversé aujourd'hui.

## Fonctionnalités

- **Indicateur Oui/Non** : Affiche si un événement a été enregistré aujourd'hui
- **Compteur de jours** : Nombre de jours depuis la dernière entrée
- **Titre automatique** : Le titre de l'article est récupéré automatiquement depuis l'URL
- **Surveillance automatisée** : Un script (`fetch_events.py`) parcourt les flux RSS de sources francophones (Le Monde, France Info, Ouest-France) toutes les 6 heures pour détecter les nouvelles sorties controversées de Trump et les ajouter automatiquement dans `data/events.md`. Seuls les articles dont Trump est le **sujet** (il a dit ou fait quelque chose) sont retenus ; les événements externes (votes, réactions de tiers…) sont filtrés.

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

## Surveillance automatisée

Le workflow `fetch-events.yml` exécute `fetch_events.py` toutes les 6 heures :
1. Parcourt les flux RSS listés dans `data/feeds.txt` (un URL par ligne)
2. Filtre les articles où **Trump est le sujet** (il dit, fait, ordonne…)
3. Exclut les articles où Trump est la cible d'actions de tiers
4. Ajoute les nouveaux articles dans `data/events.md` et pousse les changements

### Ajouter un flux RSS

Ajoutez simplement l'URL dans `data/feeds.txt` :

```
https://www.lemonde.fr/international/rss_full.xml
https://www.franceinfo.fr/monde/usa/presidentielle/donald-trump.rss
```
