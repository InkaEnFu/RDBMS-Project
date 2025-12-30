from connection import DatabaseConnection


class UserGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "users"
