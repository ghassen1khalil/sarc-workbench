# 🤖 AI DIRECTIVES : WORKBENCH ARCHITECTURE & STANDARDS

**IMPORTANT :** Ce fichier définit la "Constitution Technique" du projet Workbench.
Toute IA (Copilot, ChatGPT, Claude) assistant un développeur sur ce projet DOIT lire et appliquer ces directives AVANT de générer la moindre ligne de code.

---

## 1. PHILOSOPHIE DU PROJET
Ce projet est un **Workbench Modulaire** composé d'un hôte (Host) et de plugins.
L'architecture est strictement découplée :
* **Backend (Microservices)** : Logique métier pure exposée via REST (FastAPI).
* **Frontend (Microfrontends)** : Interface utilisateur pure (PyQt6) qui consomme les APIs.

**⚠️ INTERDICTION ABSOLUE :** Le code du Frontend ne doit JAMAIS importer ou appeler directement le code du Backend. La communication se fait EXCLUSIVEMENT via HTTP (`requests`).

---

## 2. STRUCTURE DES FICHIERS (Directory Layout)
Tout nouveau plugin doit être scindé physiquement en deux arborescences distinctes.
Exemple pour un plugin nommé `my_plugin` :

```text
project_root/
├── backend/plugins/my_plugin/    # SERVICE (API & LOGIQUE)
│   ├── __init__.py
│   ├── main.py                   # Point d'entrée FastAPI
│   ├── service.py                # Logique métier interne
│   └── models.py                 # Schémas Pydantic
│
└── frontend/plugins/my_plugin/   # INTERFACE (WIDGETS)
    ├── __init__.py
    └── ui.py                     # Widget PyQt6 (View)
```

## 3. STANDARDS BACKEND (Service)
**Stack** : Python 3.10+, FastAPI, Uvicorn, Pydantic.

**Règles d'Or :**
1. **Isolation** : Pas de dépendance à `PyQt`, `tkinter` ou autre lib graphique.
2. **Configuration** : Le port et les paramètres doivent être configurables (via `conf/application_config.yaml` géré par le Core).
3. **Logging Centralisé :**
    - Ne jamais utiliser `print()`.
    - Utiliser `logging`. Configurer un Handler pour envoyer les logs critiques au **Core Service** (`POST /system/logs`).

**Template Obligatoire (`main.py`) :**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configuration du Logger (Template simplifié)
logger = logging.getLogger("my_plugin")

app = FastAPI(title="My Plugin API", version="1.0.0")

@app.get("/health")
def health_check():
    """Endpoint requis pour le Discovery du Workbench"""
    return {"status": "up", "module": "my_plugin"}

# Définir les routes métiers ici...
```

## 4. STANDARDS FRONTEND (Interface)
**Stack** : Python 3.10+, PyQt6, Requests.

**Règles d'Or :**
1. **Héritage :** Le composant principal doit être un QWidget (jamais QMainWindow ni QApplication).
2. **Dumb UI :** L'interface ne fait que de l'affichage et de la capture d'événements.
3. **Appels API :**
    - Utiliser la librairie requests.
    - Base URL : http://localhost:{PORT_DU_SERVICE}.
4. **Responsivité (Anti-Freeze) :**
    - Tout appel réseau ou traitement > 100ms doit être exécuté dans un QThread ou via un Worker asynchrone.
    - Afficher un indicateur de chargement (spinner ou texte) pendant les requêtes.
5. **Nettoyage :** Implémenter le nettoyage des threads/timers à la fermeture du widget (closeEvent).

**Template Obligatoire (`ui.py`) :**
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot
import requests

class PluginWidget(QWidget):
    def __init__(self, api_url="http://localhost:8001"):
        super().__init__()
        self.api_url = api_url
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.label = QLabel("Prêt")
        self.btn = QPushButton("Action")
        self.btn.clicked.connect(self.on_action_clicked)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

    def on_action_clicked(self):
        # Exemple d'appel sécurisé (devrait idéalement être dans un QThread)
        try:
            self.label.setText("Chargement...")
            resp = requests.get(f"{self.api_url}/health", timeout=2)
            self.label.setText(f"Réponse : {resp.json()}")
        except Exception as e:
            self.label.setText("Erreur API")
            # Log local ou notification utilisateur
```

## 5. GESTION DE LA CONFIGURATION
- **Interdit :** Créer des fichiers `.ini`, `.json` ou `.env` locaux dans le dossier du plugin.
- **Standard :** Le plugin reçoit sa configuration :
    - Soit par injection lors de l'instanciation du Widget (Frontend).
    - Soit en interrogeant le **Core Service** (`GET /config`) (Backend).
- **Administration :** L'activation/Désactivation se gère via le fichier global `conf/application_config.yaml`.

## 6. SÉCURITÉ & ROBUSTESSE
1. **Validation des Entrées :** Le Backend doit valider toutes les entrées via Pydantic.
2. **Gestion d'Erreur UI :** Si le Backend est éteint, le Frontend ne doit pas crasher. Il doit afficher un message "Service indisponible" ou un bouton "Retry".
3. **Dépendances :** Si le plugin nécessite une lib externe (ex: `pandas`), l'ajouter explicitement dans un fichier `requirements.txt` propre au plugin ou au projet global.

#### **FIN DES DIRECTIVES.** Si tu as compris, analyse la tâche demandée et génère le code en respectant scrupuleusement ces séparations.