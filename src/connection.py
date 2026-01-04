
import mysql.connector
import json
import os


class Config:
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self):
        if self._config is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                print(f"Configuration loaded from {config_path}")
            except FileNotFoundError:
                print(f"Config file not found at {config_path}, using defaults.")
                self._config = {
                    "database": {
                        "host": "127.0.0.1",
                        "port": 3306,
                        "user": "uzivatel",
                        "password": "heslo",
                        "database": "animelist"
                    },
                    "app": {
                        "debug": True,
                        "port": 5000,
                        "secret_key": "animelist_secret_key"
                    }
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing config file: {e}")
                raise
        return self._config
    
    def get_database_config(self):
        return self.load().get("database", {})
    
    def get_app_config(self):
        return self.load().get("app", {})


class DatabaseConnection:
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self):
        if self._connection is None or not self._connection.is_connected():
            config = Config().get_database_config()
            self._connection = mysql.connector.connect(
                host=config.get("host", "127.0.0.1"),
                port=config.get("port", 3306),
                user=config.get("user", "uzivatel"),
                password=config.get("password", "heslo"),
                database=config.get("database", "animelist")
            )
            print("Successfully connected to database.")
        return self._connection
    
    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None


if __name__ == "__main__":
    db = DatabaseConnection()
    db.get_connection()
