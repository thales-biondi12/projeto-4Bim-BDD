"""Conexao compartilhada com o MongoDB usando variavel de ambiente."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).with_name('.env'))
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
cliente.admin.command('ping')
banco = cliente['laboratorio_python']
