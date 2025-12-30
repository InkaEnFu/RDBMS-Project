from connection import DatabaseConnection


class WatchlistEntryGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "watchlist_entries"
