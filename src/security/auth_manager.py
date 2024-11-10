import os
import json
import bcrypt
import secrets
from datetime import datetime
from typing import Dict, Optional

class AuthManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.clients_file = os.path.join(storage_path, 'clients.json')
        self._init_storage()
    
    def _init_storage(self):
        if not os.path.exists(self.clients_file):
            with open(self.clients_file, 'w') as f:
                json.dump({}, f)
                
    def _load_clients(self) -> Dict:
        with open(self.clients_file, 'r') as f:
            return json.load(f)
            
    def _save_clients(self, clients: Dict):
        with open(self.clients_file, 'w') as f:
            json.dump(clients, f, indent=4)
            
    def register_client(self, username: str, password: str, email: str, 
                       phone: str, purpose: str, ip: str) -> Dict:
        clients = self._load_clients()
        
        if username in clients:
            raise ValueError("Username already exists")
            
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        token = secrets.token_urlsafe(32)
        
        clients[username] = {
            "hashed_password": hashed.decode(),
            "email": email,
            "phone": phone,
            "purpose": purpose,
            "token": token,
            "registered_on": datetime.now().isoformat(),
            "registered_from_ip": ip,
            "last_login": None
        }
        
        self._save_clients(clients)
        return {"username": username, "token": token}
        
    def verify_client(self, username: str, password: str, ip: str) -> Optional[Dict]:
        clients = self._load_clients()
        
        if username not in clients:
            return None
            
        stored = clients[username]
        if bcrypt.checkpw(password.encode(), stored["hashed_password"].encode()):
            clients[username]["last_login"] = datetime.now().isoformat()
            clients[username]["last_login_ip"] = ip
            self._save_clients(clients)
            return {"username": username, "token": stored["token"]}
            
        return None
        
    def verify_token(self, token: str) -> bool:
        clients = self._load_clients()
        return any(client["token"] == token for client in clients.values())