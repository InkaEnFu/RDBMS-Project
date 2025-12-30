from connection import DatabaseConnection


class GenreGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "genres"
