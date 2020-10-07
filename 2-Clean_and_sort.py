import json
import sqlite3 as lite
from tqdm import tqdm
import signal

from hashlib import md5


# TODO: Check Imports

def handler(signum, frame):
    print('Exiting Gracefully')
    if source_connection:
        source_connection.close()
    if output_connection:
        output_connection.close()


signal.signal(signal.SIGINT, handler)


class CustomValueError(ValueError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


# Set up database stuff:
source_connection = lite.connect("BRI_data.db")
output_connection = lite.connect("BRI_processed.db")
source_cursor = source_connection.cursor()
output_cursor = output_connection.cursor()
output_cursor.execute('DROP TABLE IF EXISTS output_sorted;')
output_cursor.execute('CREATE TABLE output_sorted (url_hash TEXT PRIMARY KEY, url TEXT, snippet TEXT, name TEXT, '
                      'month TEXT, term TEXT);')

row_total, = source_cursor.execute("SELECT COUNT(1) FROM terms_pulled;").fetchone()
pbar = tqdm(total=row_total)
source_cursor.execute("SELECT * FROM terms_pulled;")
for row in source_cursor:
    term, offset, date_range, json_str = row
    row_json = json.loads(json_str)
    pbar.update()
    try:
        for result in row_json['webPages']['value']:
            url = result['url']
            url_hash = md5(url.encode('utf-8')).hexdigest()
            snippet = result['snippet']
            name = result['name']
            output_cursor.execute("INSERT OR IGNORE INTO output_sorted VALUES ('" + url_hash + "', '" + url + "', '" +
                                  snippet + "', '" + name + "', '" + date_range + "', '" + term.strip("\n") + "');")
            output_connection.commit()
    except KeyError as e:
        pass

if output_connection:
    output_connection.close()
if source_connection:
    source_connection.close()