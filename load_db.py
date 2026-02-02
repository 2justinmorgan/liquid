from sqlite3 import connect
from json import load
from os import system


def create_table():
    """
    CREATE TABLE mins (
        symbol TEXT,
        type TEXT,
        candleType TEXT,
        open REAL,
        close REAL,
        high REAL,
        low REAL,
        volume REAL,
        time TEXT -- Stored as ISO 8601 string
    );
    """
    pass


def insert_to_db(json_file_name: str) -> None:
    f = open(json_file_name, 'r')
    mins = load(f)
    connection = connect("mins.db")
    cursor = connection.cursor()

    events = mins
    if not isinstance(events, list):
        print(f"-----------NOT {json_file_name}")
        return

    data_to_insert = [
        (c['symbol'], c['type'], c['candleType'], c['open'], c['close'], c['high'], c['low'], c['volume'], c['time'])
        for c in events
    ]

    # 4. Use executemany for high performance
    query = '''
        INSERT INTO mins (symbol, type, candleType, open, close, high, low, volume, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    cursor.executemany(query, data_to_insert)

    # 5. Commit and close
    connection.commit()
    print(f"Successfully inserted {cursor.rowcount} rows.")
    connection.close()
    f.close()


def load_all_files():
    from pathlib import Path

    # Use '.' for the current directory, or specify a path like 'my_folder'
    directory_path = Path('out')
    files_list = [p for p in directory_path.iterdir() if p.is_file()]

    for file_path in files_list:
        file_name = str(file_path).split('\\')[1]
        print(f"'out/{file_name}'")
        insert_to_db(f"out/{file_name}")
