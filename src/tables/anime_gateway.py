from connection import DatabaseConnection


class AnimeGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "anime"
