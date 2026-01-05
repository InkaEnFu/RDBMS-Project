import os
from connection import Config


class DatabaseSetup:
    
    SQL_SCRIPT_TEMPLATE = """
CREATE DATABASE IF NOT EXISTS {database_name}
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED WITH mysql_native_password BY '{password}';
ALTER USER '{username}'@'%' IDENTIFIED WITH mysql_native_password BY '{password}';

GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'%';
FLUSH PRIVILEGES;

USE {database_name};

-- 1) users
CREATE TABLE users (
  id int AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) NOT NULL UNIQUE,
  email VARCHAR(128) NOT NULL UNIQUE,
  is_admin BOOLEAN NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2) anime
CREATE TABLE anime (
  id int AUTO_INCREMENT PRIMARY KEY,
  title_romaji VARCHAR(200) NOT NULL,
  title_english VARCHAR(200),
  episodes_total INT NOT NULL DEFAULT 0,
  status ENUM('ONGOING','FINISHED') NOT NULL,
  start_date DATE,
  external_score FLOAT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3) genres
CREATE TABLE genres (
  id int AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(40) NOT NULL UNIQUE
);

-- 4) anime_genres (M:N)
CREATE TABLE anime_genres (
  anime_id int NOT NULL,
  genre_id int NOT NULL,
  PRIMARY KEY (anime_id, genre_id),
  FOREIGN KEY (anime_id) REFERENCES anime(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genres(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 5) watchlist_entries (user's list)
CREATE TABLE watchlist_entries (
  user_id int NOT NULL,
  anime_id int NOT NULL,
  state ENUM('WATCHING','PLAN_TO_WATCH','COMPLETED','DROPPED') NOT NULL,
  rating int,
  progress INT NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, anime_id),
  FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (anime_id) REFERENCES anime(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6) watchlist_history (change history)
CREATE TABLE watchlist_history (
  id int AUTO_INCREMENT PRIMARY KEY,
  user_id int NOT NULL,
  anime_id int NOT NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  old_state ENUM('WATCHING','PLAN_TO_WATCH','COMPLETED','DROPPED') NOT NULL,
  new_state ENUM('WATCHING','PLAN_TO_WATCH','COMPLETED','DROPPED') NOT NULL,

  old_rating int,
  new_rating int,

  old_progress INT NOT NULL,
  new_progress INT NOT NULL,

  action_type ENUM('INSERT','UPDATE','DELETE') NOT NULL DEFAULT 'UPDATE',

  FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (anime_id) REFERENCES anime(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);

DELIMITER //

CREATE TRIGGER watchlist_entry_insert_trigger
AFTER INSERT ON watchlist_entries
FOR EACH ROW
BEGIN
    INSERT INTO watchlist_history 
        (user_id, anime_id, old_state, new_state, old_rating, new_rating, old_progress, new_progress, action_type)
    VALUES 
        (NEW.user_id, NEW.anime_id, NEW.state, NEW.state, NULL, NEW.rating, 0, NEW.progress, 'INSERT');
END //

CREATE TRIGGER watchlist_entry_update_trigger
AFTER UPDATE ON watchlist_entries
FOR EACH ROW
BEGIN
    INSERT INTO watchlist_history 
        (user_id, anime_id, old_state, new_state, old_rating, new_rating, old_progress, new_progress, action_type)
    VALUES 
        (OLD.user_id, OLD.anime_id, OLD.state, NEW.state, OLD.rating, NEW.rating, OLD.progress, NEW.progress, 'UPDATE');
END //

CREATE TRIGGER watchlist_entry_delete_trigger
AFTER DELETE ON watchlist_entries
FOR EACH ROW
BEGIN
    INSERT INTO watchlist_history 
        (user_id, anime_id, old_state, new_state, old_rating, new_rating, old_progress, new_progress, action_type)
    VALUES 
        (OLD.user_id, OLD.anime_id, OLD.state, OLD.state, OLD.rating, NULL, OLD.progress, 0, 'DELETE');
END //

DELIMITER ;

CREATE VIEW user_watchlist_view AS
SELECT 
    we.user_id,
    we.anime_id,
    u.username AS user_name,
    a.title_romaji AS anime_name,
    we.state,
    we.rating,
    we.progress
FROM watchlist_entries we
JOIN users u ON we.user_id = u.id
JOIN anime a ON we.anime_id = a.id;

CREATE VIEW anime_with_genres_view AS
SELECT 
    a.id AS anime_id,
    a.title_romaji,
    a.title_english,
    a.status,
    GROUP_CONCAT(g.name SEPARATOR ', ') AS genres
FROM anime a
LEFT JOIN anime_genres ag ON a.id = ag.anime_id
LEFT JOIN genres g ON ag.genre_id = g.id
GROUP BY a.id, a.title_romaji, a.title_english, a.status;
"""

    def __init__(self):
        self.config = Config()
    
    def get_database_sql_path(self):
        src_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(src_dir)
        return os.path.join(project_root, 'databaze.sql')
    
    def database_sql_exists(self):
        return os.path.exists(self.get_database_sql_path())
    
    def generate_sql_script(self):
        db_config = self.config.get_database_config()
        
        return self.SQL_SCRIPT_TEMPLATE.format(
            database_name=db_config.get('database', 'animelist'),
            username=db_config.get('user', 'uzivatel'),
            password=db_config.get('password', 'heslo')
        )
    
    def create_database_sql_file(self):
        sql_script = self.generate_sql_script()
        sql_path = self.get_database_sql_path()
        
        try:
            with open(sql_path, 'w', encoding='utf-8') as f:
                f.write(sql_script)
            
            print(f"Created databaze.sql file at: {sql_path}")
            return True
            
        except Exception as e:
            print(f"Error creating databaze.sql file: {e}")
            return False
    
    def is_first_run(self):
        return not self.database_sql_exists()
    
    def setup_database_if_needed(self):
        if self.is_first_run():
            print("First run detected - creating databaze.sql...")
            success = self.create_database_sql_file()
            if success:
                print("databaze.sql successfully created with values from config.json")
                print("You can now run databaze.sql in MySQL to create the database and tables")
                print("After creating the database, run the application again for normal operation")
                return True
            else:
                print("Error creating databaze.sql")
                return False
        return False


if __name__ == "__main__":
    db_setup = DatabaseSetup()
    print(f"Is this the first run? {db_setup.is_first_run()}")
    if db_setup.is_first_run():
        db_setup.create_database_sql_file()