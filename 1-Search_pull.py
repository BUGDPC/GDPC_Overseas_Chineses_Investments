import urllib
import requests
import json
import sqlite3 as lite
import pickle

import signal
import time

from hashlib import md5


test_pull = False

def handler(signum, frame):
    print('Exiting Gracefully')
    if connection:
        connection.close()
signal.signal(signal.SIGINT, handler)

class CustomValueError(ValueError):
 def __init__(self, arg):
  self.strerror = arg
  self.args = {arg}


#Azure Subscription Key:
sub_key = "[YOUR KEY HERE]"
bing_url_base ='https://api.cognitive.microsoft.com/bing/v7.0/search'

# Example Date Ranges. Please Edit to suit your collection needs
dates_rages = ["2015-01-01..2015-01-31",
"2015-02-01..2015-02-28",
"2015-03-01..2015-03-31",
"2015-04-01..2015-04-30",
"2015-05-01..2015-05-31",
"2015-06-01..2015-06-30",
"2015-07-01..2015-07-31",
"2015-08-01..2015-08-31",
"2015-09-01..2015-09-30",
"2015-10-01..2015-10-31",
"2015-11-01..2015-11-30",
"2015-12-01..2015-12-31",
"2016-01-01..2016-01-31",
"2016-02-01..2016-02-28",
"2016-03-01..2016-03-31",
"2016-04-01..2016-04-30",
"2016-05-01..2016-05-31",
"2016-06-01..2016-06-30",
"2016-07-01..2016-07-31",
"2016-08-01..2016-08-31",
"2016-09-01..2016-09-30",
"2016-10-01..2016-10-31",
"2016-11-01..2016-11-30",
"2016-12-01..2016-12-31",
"2017-01-01..2017-01-31",
"2017-02-01..2017-02-28",
"2017-03-01..2017-03-31",
"2017-04-01..2017-04-30",
"2017-05-01..2017-05-31",
"2017-06-01..2017-06-30",
"2017-07-01..2017-07-31",
"2017-08-01..2017-08-31",
"2017-09-01..2017-09-30",
"2017-10-01..2017-10-31",
"2017-11-01..2017-11-30",
"2017-12-01..2017-12-31",
"2018-01-01..2018-01-31",
"2018-02-01..2018-02-28",
"2018-03-01..2018-03-31",
"2018-04-01..2018-04-30",
"2018-05-01..2018-05-31",
"2018-06-01..2018-06-30",
"2018-07-01..2018-07-31",
"2018-08-01..2018-08-31",
"2018-09-01..2018-09-30",
"2018-10-01..2018-10-31",
"2018-11-01..2018-11-30",
"2018-12-01..2018-12-31"]

#Set up database :
connection = lite.connect("BRI_data.db")
cursor = connection.cursor()
cursor2 = connection.cursor()

#load terms if needed:
f = open('terms.lst', 'r')
term_arr = f.readlines()

#Primary key is to make sure our inserts don't duplicate.
cursor2.execute('CREATE TABLE IF NOT EXISTS terms_lookup (term TEXT, term_hash TEXT PRIMARY KEY);')
for row in term_arr:
    term = row.split("\t")[0].strip()
    cursor2.execute("INSERT OR IGNORE INTO terms_lookup VALUES ('" + term + "', '" + md5(term.encode('utf-8')).hexdigest() + "');")

connection.commit()

terms = term_arr
#Examaple:
# terms = ['"China Development Bank" loan']
cursor.execute("CREATE TABLE IF NOT EXISTS terms_pulled(term TEXT, offset INT, datestr TEXT, json TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS urls_pulled(urlhash TEXT PRIMARY KEY, url TEXT, result BLOB);")

for term in terms:
    print("running term: " + term)
    #each term is run also by date
    for date_range in dates_rages:
        #For the offset increments
        offset = 0
        num_of_results = -1
        last = False
        try:
            while True:
                # Example Debugging:
                # print("offset: " + str(offset) + "; term: " + term + "; date range:" + date_range)
                # offset wont be this high for very specific terms.
                if offset > 1500:
                    raise CustomValueError("hit our offset limit!")
                    #The following unreachable code was originally for testing
                    print( "offset is getting large for term: " + term)
                    try:
                        yn = raw_input("Do you wish to continue? (y/n)")
                        if(yn != 'y'):
                            break
                    except NameError:
                        #if response not defined, let's pass. edge condition
                        pass

                encoded_term = urllib.parse.quote(term)
                bing_url = bing_url_base + "?q=" + encoded_term + "&count=100&offset=" + str(offset) + "&freshness=" + date_range
                bing_url_hash = md5(bing_url.encode('utf-8')).hexdigest()
                print(bing_url)

                #Helper for testing:
                class TestReponse:
                    def __init__(self):
                        pass
                    status_code = -1

                response = TestReponse()
                if not test_pull:
                    cursor.execute("select * from urls_pulled where urlhash='" + bing_url_hash + "';")
                    # This may be needed at a future time:
                    has_term = cursor.fetchone()
                    if has_term and len(has_term) > 0:
                        # if we have already pulled this term, don't pull again, but keep our fake response for control flow.
                        response = pickle.loads(has_term[2])
                    else:
                        response = requests.get(bing_url, headers={'Ocp-Apim-Subscription-Key': sub_key}, timeout=15)
                        #no matter the response, we are going to enter it into the db. This will be good for future erros stuff
                        insert_cmd = "INSERT OR IGNORE INTO urls_pulled ('urlhash', 'url', 'result') VALUES (?, ?, ?);"
                        data_tuple = (bing_url_hash, bing_url, pickle.dumps(response))
                        cursor.execute(insert_cmd, data_tuple)
                        connection.commit()
                else:
                    #just for testing:
                    print("url: " + bing_url)

                if response.status_code == 200:
                    #Debugging:
                    # print(json.dumps(response.json()).replace("'", ""))
                    if(num_of_results == -1):
                        try:
                            num_of_results = int(response.json()['webPages']['totalEstimatedMatches'])
                        except KeyError as e:
                            print("No Results for " + term + ", " + date_range)
                    print("num of results: " + str(num_of_results))
                    json_str = json.dumps(response.json()).replace("'", "")

                    insert_cmd = "INSERT INTO terms_pulled VALUES ('" + term + "', '" + str(offset) + "', '" + date_range + "', '" + json_str + "');"
                    cursor.execute(insert_cmd)
                    connection.commit()
                    if(last):
                        raise CustomValueError("End of the line; Offset maxed")
                    if offset < 100 and num_of_results < 100:
                        raise CustomValueError("End of the line; Offset maxed")
                    elif (offset + 100) >= num_of_results:
                        #need to increment a smaller amount
                        for i in range(100, -1, -1):
                            if (offset + i) >= num_of_results:
                                continue
                            else:
                                offset = offset + i + 1
                                last = True
                                print("Incrementing Offset. Now equals: " + str(offset))
                    else:
                        offset = offset + 100
                        print("Incrementing Offset. Now equals: " + str(offset))
                elif response.status_code == 401:
                    print(response)
                    print(response.content)
                    exit(0)
                elif response.status_code == -1:
                    #Testing
                    pass
                elif response.status_code == 403:
                    #Wait 10 seconds
                    time.sleep(10)
                    #then retry the pull in case API issue:
                    response = requests.get(bing_url, headers={'Ocp-Apim-Subscription-Key': sub_key})
                    if response.status_code == 200:
                        #re-add to database
                        update_cmd = "UPDATE urls_pulled SET result = ? WHERE urlhash='" + bing_url_hash + "' AND url='" + bing_url + "';"
                        # import pudb; pudb.set_trace()
                        data_tuple = (pickle.dumps(response),)
                        cursor.execute(update_cmd, data_tuple)
                        connection.commit()
                    else:
                        #some other error; let's not keep going
                        print(response)
                        print(response.content)
                        exit(1)
                else:
                    print(response)
                    print(response.content)
                    break
                    #if offset > 100:
                    #    break
                    # Finish here to loop through results. For now, did this manually, since we only have 2 pages of results
        except CustomValueError as e:
            print("Offset got too high!")

if connection:
    connection.close()
