from connection import DatabaseConnection


class WatchlistHistoryGateway:
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = "watchlist_history"
