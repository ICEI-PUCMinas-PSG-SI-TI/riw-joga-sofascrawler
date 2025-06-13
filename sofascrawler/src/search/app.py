from flask import Flask, request, jsonify, render_template
import json
import math
from collections import defaultdict
import numpy as np

app = Flask(__name__)

# Carrega os índices
with open('data/normalized/inverted_index.json', 'r') as f:
    index_data = json.load(f)
    inverted_index = index_data['index']
    doc_lengths = index_data['doc_lengths']
    doc_count = index_data['doc_count']

with open('data/normalized/search_metadata.json', 'r') as f:
    metadata = json.load(f)

class SearchEngine:
    def __init__(self):
        self.index = inverted_index
        self.doc_lengths = doc_lengths
        self.documents = metadata['documents']
    
    def cosine_similarity(self, query_weights, doc_weights, doc_id):
        """Calcula similaridade cosseno entre query e documento"""
        dot_product = sum(qw * dw for qw, dw in zip(query_weights, doc_weights))
        query_norm = math.sqrt(sum(qw ** 2 for qw in query_weights))
        doc_norm = math.sqrt(sum(dw ** 2 for dw in doc_weights))
        
        if query_norm == 0 or doc_norm == 0:
            return 0
        return dot_product / (query_norm * doc_norm)
    
    def search(self, query, top_k=10):
        """Executa uma consulta no índice invertido"""
        # Pré-processa a query (mesmo processo usado na indexação)
        normalizer = DataNormalizer()
        query_terms = normalizer.preprocess_text(query)
        
        # Calcula pesos da query (TF-IDF)
        query_weights = []
        term_weights = {}
        
        for term in query_terms:
            # IDF do termo (log(N/df))
            df = len(self.index.get(term, {}))
            idf = math.log(doc_count / (df + 1)) if df > 0 else 0
            
            # TF da query (1 + log(tf))
            tf = query_terms.count(term)
            tf_weight = 1 + math.log(tf) if tf > 0 else 0
            
            term_weights[term] = tf_weight * idf
        
        # Para cada documento, calcula similaridade
        scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index:
                for doc_id, weight in self.index[term].items():
                    # Peso do termo no documento * peso do termo na query
                    scores[doc_id] += weight * term_weights[term]
        
        # Normaliza pelos comprimentos dos documentos
        for doc_id in scores:
            scores[doc_id] /= (self.doc_lengths[doc_id] + 0.1)
        
        # Ordena resultados
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Adiciona metadados
        results = []
        for doc_id, score in sorted_results:
            doc_type, *parts = doc_id.split(':')
            if doc_type == 'team':
                results.append({
                    'type': 'team',
                    'name': parts[0],
                    'tournament': parts[1],
                    'score': score,
                    'snippet': self.documents[doc_id][:200] + '...'
                })
            elif doc_type == 'player':
                results.append({
                    'type': 'player',
                    'name': parts[0],
                    'team': parts[1],
                    'tournament': parts[2],
                    'score': score,
                    'snippet': self.documents[doc_id][:200] + '...'
                })
        
        return results

search_engine = SearchEngine()

@app.route('/')
def home():
    return render_template('search.html', tournaments=metadata['tournaments'])

@app.route('/search')
def search():
    query = request.args.get('q', '')
    tournament_filter = request.args.get('tournament', None)
    
    results = search_engine.search(query)
    
    # Aplica filtros
    if tournament_filter:
        results = [r for r in results if r['tournament'] == tournament_filter]
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)