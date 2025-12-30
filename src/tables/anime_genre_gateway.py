from connection import DatabaseConnection


class AnimeGenreGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "anime_genres"
