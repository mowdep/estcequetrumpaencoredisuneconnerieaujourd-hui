# Est-ce que Trump a encore dit une connerie aujourd'hui ?

Un site web 100% statique qui affiche si Trump a dit quelque chose de controversé aujourd'hui.

## Fonctionnalités

- **Indicateur Oui/Non** : Affiche si un événement a été enregistré aujourd'hui
- **Compteur de jours** : Nombre de jours depuis la dernière entrée
- **Dernière entrée** : Affiche le lien, titre et miniature (si disponible) de la dernière entrée

## Source de données

Le fichier `data/events.md` est la seule source de données éditable.

### Format du fichier

```
YYYY-MM-DD|URL|Titre|URLMiniature (optionnel)
```

**Exemple :**
```
2026-02-03|https://example.com/article|Trump dit quelque chose|https://example.com/image.jpg
2026-02-01|https://example.com/article2|Une autre déclaration
```

**Règles :**
- 1 ligne = 1 événement
- Les lignes vides sont ignorées
- Aucun commentaire
- Les champs sont séparés par `|`
- La miniature est optionnelle

## Construction locale

```bash
python build.py
```

Le site est généré dans le dossier `public/`.

## Déploiement

Le site est automatiquement déployé sur GitHub Pages via GitHub Actions :
- À chaque push sur la branche `main`
- Quotidiennement à minuit UTC
- Manuellement via workflow_dispatch
