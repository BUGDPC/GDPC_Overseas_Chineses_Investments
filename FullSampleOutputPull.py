import sqlite3 as lite

connection = lite.connect("BRI_processed.db")
cursor = connection.cursor()
cursor.execute('SELECT * FROM output_sorted WHERE url_hash IN (SELECT url_hash FROM output_sorted ORDER BY RANDOM());')
with open('all.csv', 'w') as output:
    for row in cursor:
        url_hash, url, snippet, name, date, term = row
        date = date[0:7]
        output.write(date + "," + term + ", " + snippet.replace(',', ' ') + "," + name.replace(',', ' ') + ",'" + url +
                     "'\n")

if connection:
    connection.close()
