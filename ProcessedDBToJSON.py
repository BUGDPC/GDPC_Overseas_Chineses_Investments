import sqlite3 as lite

connection = lite.connect("BRI_processed.db")
cursor = connection.cursor()
cursor.execute('SELECT * FROM output_sorted;')

with open('db_dump_all_records.csv', 'w') as output:
    for row in cursor:
        url_hash, url, snippet, name, date, term = row
        date = date[0:7]
        output.write(date + "," + term + ", " + snippet.replace(',', ' ') + "," + name.replace(',', ' ') + ",'" + url +
                     "'\n")

if connection:
    connection.close()
