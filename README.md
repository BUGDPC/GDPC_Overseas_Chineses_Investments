

# Data Scraper for Oversease Chinese Investments, A Research Database

* Citation to be added after publication.
<br/>

## Table of Contents
* [About the Project](#about-the-project)
* [Usage](#usage)
* [License & Warranty](#license)
* [Contact](#contact)


<br/>

## About The Project
The objective of the research study was to create a database of global Chinese investments. Specifically, to identify financing arrangements from Export-Import Bank of China and China
Development Bank to various projects around the world. We use news aggregation services
The full study, research, and publications can be found [here] (To be updated after publication). The code here is a small piece of the overall data collection, methodology, and verification steps that went into this research.

## Usage
The project code requires a number of packages and software to run. These include an existing sqlite3 installation and database, python3 installation, python packages (see scripts). In addition, this uses Azure marketplace API to make data requests, so an account
is required with a valid API key.


The basic usage is as follows.
1. Create list of Search Terms. The format of these is the same as typical web-search queries, such as including quotes for exact matches, etc. See [Search Term Operators](https://support.google.com/websearch/answer/2466433). Example:
```text
China “Eximbank” lending
```
These terms are included one per line in ``terms.lst``. For a full list of terms used, see extended documentation in the publication above.
2. Initialize sqlite database and add API key to 1-Search_pull.py
3. run via
```bash
python 1-Search_pull.py
````
4. At this point all data is collected in raw form. This data is a short 1-sentence snippet as well as a url. Unfortunately, this is not enough to validate the results at this point, as there are over 1M total results; untenable to process these manually.
5. Full text was scraped and added to the database using ``ScrapedURLsToCouchDB`` as well as ``fulltextscraper.py``.
6. Additional steps were performed as noted in the methodology paper (above). The following methods were used as helpers only.
  * ``ScrapedURLsToCouchDB.ipynb`` Jupyter Notebook for data cleaning and loading into database for manual review.
  * ``RandomSamplePull.py`` Pulls a random data sample from raw results. As noted in the
  methodology section, we performed several samplings during the course of our methodology
  approach in order to validate findings.
  * ``ProcessedDBToJSON.py`` data export to CSV/JSON format.
  * ``CouchDBConflictResolver.ipynb`` Checks for conflicts in the database.
  * ``index.js`` Additional Filtering and resolution of issues. (orig in Nodejs)
  * ``FullSampleOutputPull.py`` Full data output, randomized.
  * ``Insert Design Document.ipynb`` Design Testing Documents

## License
The project is Licensed under Mozilla Public License 2.0 open source license. Please
use paper citation when borrowing from data or code. This code is provided without Warranty. Please see LICENSE file for further information.

## Contact
For research questions, please contact paper authors directly. For Any code questions, please contact here.
