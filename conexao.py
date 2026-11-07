from pymongo import MongoClient

MONGO_URI = "mongodb+srv://PedroBD:Pedbatata12@clusterprojeto3.b6i8yfw.mongodb.net/?appName=ClusterProjeto3"

cliente = MongoClient(MONGO_URI)

# Testa a comunicação com o MongoDB! (coloquei como recomendação)
cliente.admin.command("ping")

banco = cliente["laboratorio_python"]

print("Conectado ao MongoDB!")