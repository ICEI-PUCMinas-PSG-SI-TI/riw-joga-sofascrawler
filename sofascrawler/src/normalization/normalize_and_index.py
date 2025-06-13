import json
import pandas as pd
from collections import defaultdict
import math
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

# Baixe os recursos necessários do NLTK
nltk.download('stopwords')

class DataNormalizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english') | set(stopwords.words('portuguese')))
        self.stemmer = PorterStemmer()
        self.translator = str.maketrans('', '', string.punctuation)
    
    def preprocess_text(self, text):
        """Normaliza texto para indexação"""
        # Remove pontuação e converte para minúsculas
        text = text.translate(self.translator).lower()
        
        # Tokenização simples
        tokens = text.split()
        
        # Remove stopwords e aplica stemming
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return processed_tokens

class InvertedIndexBuilder:
    def __init__(self):
        self.index = defaultdict(dict)
        self.doc_lengths = {}
        self.doc_count = 0
    
    def add_document(self, doc_id, text):
        """Adiciona um documento ao índice invertido"""
        terms = DataNormalizer().preprocess_text(text)
        self.doc_count += 1
        
        # Calcula frequência dos termos no documento
        term_freq = defaultdict(int)
        for term in terms:
            term_freq[term] += 1
        
        # Atualiza o índice
        for term, freq in term_freq.items():
            if doc_id not in self.index[term]:
                self.index[term][doc_id] = 0
            self.index[term][doc_id] += freq
        
        # Armazena o comprimento do documento (para normalização)
        self.doc_lengths[doc_id] = len(terms)
    
    def calculate_tfidf(self):
        """Calcula pesos TF-IDF para todos os termos"""
        for term, doc_dict in self.index.items():
            idf = math.log(self.doc_count / len(doc_dict))
            for doc_id, tf in doc_dict.items():
                # TF-IDF = (1 + log(tf)) * log(N/df)
                tf_weight = 1 + math.log(tf) if tf > 0 else 0
                self.index[term][doc_id] = tf_weight * idf
    
    def save_index(self, filename):
        """Salva o índice em disco"""
        with open(filename, 'w') as f:
            json.dump({
                'index': self.index,
                'doc_lengths': self.doc_lengths,
                'doc_count': self.doc_count
            }, f)

def process_data_for_search():
    # Carrega os dados extraídos
    with open('data/processed/tournaments_data.json', 'r') as f:
        data = json.load(f)
    
    # Prepara documentos para indexação
    documents = {}
    
    # 1. Cria documentos para times
    for tournament, t_data in data.items():
        for team in t_data['teams']:
            doc_id = f"team:{team['name']}:{tournament}"
            doc_text = f"""
            Time de futebol {team['name']} participando do campeonato {tournament}.
            Estatísticas: {', '.join(f'{k}={v}' for k, v in team['stats'].items())}.
            Jogadores: {', '.join(p['name'] for p in team['players'])}.
            """
            documents[doc_id] = doc_text
    
    # 2. Cria documentos para jogadores
    for tournament, t_data in data.items():
        for team in t_data['teams']:
            for player in team['players']:
                doc_id = f"player:{player['name']}:{team['name']}:{tournament}"
                doc_text = f"""
                Jogador {player['name']} atuando pelo time {team['name']} no campeonato {tournament}.
                Posição: {player['position']}. Idade: {player['age']}.
                Nacionalidade: {player['nationality']}.
                Estatísticas: {player['matches']} jogos, {player['goals']} gols, 
                {player['assists']} assistências, média de {player['rating']}.
                """
                documents[doc_id] = doc_text
    
    # 3. Constrói o índice invertido
    index_builder = InvertedIndexBuilder()
    for doc_id, text in documents.items():
        index_builder.add_document(doc_id, text)
    
    index_builder.calculate_tfidf()
    index_builder.save_index('data/normalized/inverted_index.json')
    
    # 4. Salva metadados para recuperação
    metadata = {
        'documents': documents,
        'tournaments': list(data.keys())
    }
    with open('data/normalized/search_metadata.json', 'w') as f:
        json.dump(metadata, f)

if __name__ == "__main__":
    process_data_for_search()