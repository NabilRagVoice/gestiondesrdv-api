from flask import Flask, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from datetime import datetime
import os
import uuid

app = Flask(__name__)

# Configuration Cosmos DB
COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
COSMOS_KEY = os.environ.get('COSMOS_KEY')
DATABASE_NAME = 'gestiondesrdv-db'
CONTAINER_NAME = 'Container_1'

# Initialisation client Cosmos DB
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/rdv', methods=['GET'])
def list_rdv():
    """Lister tous les RDV"""
    try:
        query = 'SELECT * FROM c'
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return jsonify({'success': True, 'data': items, 'count': len(items)})
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rdv/<id>', methods=['GET'])
def get_rdv(id):
    """Récupérer un RDV par ID"""
    client_id = request.args.get('clientId')
    if not client_id:
        return jsonify({'success': False, 'error': 'clientId requis en query param'}), 400
    try:
        item = container.read_item(item=id, partition_key=client_id)
        return jsonify({'success': True, 'data': item})
    except exceptions.CosmosResourceNotFoundError:
        return jsonify({'success': False, 'error': 'RDV non trouvé'}), 404
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rdv/client/<client_id>', methods=['GET'])
def list_rdv_by_client(client_id):
    """Lister les RDV d'un client"""
    try:
        query = 'SELECT * FROM c WHERE c.clientId = @clientId'
        params = [{'name': '@clientId', 'value': client_id}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=False))
        return jsonify({'success': True, 'data': items, 'count': len(items)})
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rdv', methods=['POST'])
def create_rdv():
    """Créer un nouveau RDV"""
    data = request.get_json()
    
    # Validation
    required_fields = ['clientId', 'dateRdv', 'service']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Champ requis: {field}'}), 400
    
    # Création du document
    rdv = {
        'id': str(uuid.uuid4()),
        'clientId': data['clientId'],
        'dateRdv': data['dateRdv'],
        'statut': data.get('statut', 'pending'),
        'service': data['service'],
        'notes': data.get('notes', ''),
        'createdAt': datetime.utcnow().isoformat()
    }
    
    try:
        container.create_item(body=rdv)
        return jsonify({'success': True, 'data': rdv, 'message': 'RDV créé'}), 201
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rdv/<id>', methods=['PUT'])
def update_rdv(id):
    """Modifier un RDV"""
    data = request.get_json()
    
    if 'clientId' not in data:
        return jsonify({'success': False, 'error': 'clientId requis'}), 400
    
    try:
        # Récupérer le RDV existant
        existing = container.read_item(item=id, partition_key=data['clientId'])
        
        # Mise à jour des champs
        existing['dateRdv'] = data.get('dateRdv', existing['dateRdv'])
        existing['statut'] = data.get('statut', existing['statut'])
        existing['service'] = data.get('service', existing['service'])
        existing['notes'] = data.get('notes', existing['notes'])
        existing['updatedAt'] = datetime.utcnow().isoformat()
        
        container.replace_item(item=id, body=existing)
        return jsonify({'success': True, 'data': existing, 'message': 'RDV modifié'})
    except exceptions.CosmosResourceNotFoundError:
        return jsonify({'success': False, 'error': 'RDV non trouvé'}), 404
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rdv/<id>', methods=['DELETE'])
def delete_rdv(id):
    """Supprimer un RDV"""
    client_id = request.args.get('clientId')
    if not client_id:
        return jsonify({'success': False, 'error': 'clientId requis en query param'}), 400
    
    try:
        container.delete_item(item=id, partition_key=client_id)
        return jsonify({'success': True, 'message': 'RDV supprimé'})
    except exceptions.CosmosResourceNotFoundError:
        return jsonify({'success': False, 'error': 'RDV non trouvé'}), 404
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
