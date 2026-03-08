# 🗓️ API Gestion de RDV

API REST Flask pour la gestion de rendez-vous avec Azure Cosmos DB.

## 🚀 Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/rdv` | Lister tous les RDV |
| `GET` | `/api/rdv/<id>?clientId=xxx` | Récupérer un RDV par ID |
| `GET` | `/api/rdv/client/<clientId>` | Lister les RDV d'un client |
| `POST` | `/api/rdv` | Créer un nouveau RDV |
| `PUT` | `/api/rdv/<id>` | Modifier un RDV |
| `DELETE` | `/api/rdv/<id>?clientId=xxx` | Supprimer un RDV |
| `GET` | `/health` | Health check |

## 📦 Installation

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Copier `.env.example` vers `.env` et configurer :

```
COSMOS_ENDPOINT=https://abonnements-cosmos.documents.azure.com:443/
COSMOS_KEY=your_key_here
COSMOS_DATABASE=gestiondesrdv-db
COSMOS_CONTAINER=Container_1
```

## 🏃 Lancement

```bash
python app.py
```

## 🐳 Docker

```bash
docker build -t gestiondesrdv-api .
docker run -p 5000:5000 --env-file .env gestiondesrdv-api
```

## 📄 Exemple de document RDV

```json
{
  "id": "rdv-001",
  "clientId": "client-123",
  "dateRdv": "2025-02-15T10:30:00Z",
  "statut": "confirmed",
  "service": "Consultation",
  "notes": "Premier rendez-vous",
  "createdAt": "2025-02-10T08:00:00Z"
}
```
