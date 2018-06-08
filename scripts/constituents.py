from bs4 import BeautifulSoup
import csv
from os import mkdir
from yattag import Doc
from os.path import exists, join
import urllib


datadir = join('..', 'data')
if not exists(datadir):
    mkdir(datadir)

if not exists('tmp'):
    mkdir('tmp')

source = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
cache = join('tmp', 'List_of_S%26P_500_companies.html')

def retrieve():
    urllib.urlretrieve(source, cache)

def extract():
    source_page = open(cache).read()
    soup = BeautifulSoup(source_page, 'html.parser')
    table = soup.find("table", { "class" : "wikitable sortable" })

    # Fail now if we haven't found the right table
    header = table.findAll('th')
    if header[0].string != "Ticker symbol" or header[1].string != "Security":
        raise Exception("Can't parse wikipedia's table!")

    # Retreive the values in the table
    records = []
    rows = table.findAll('tr')
    for row in rows:
        fields = row.findAll('td')
        if fields:
            symbol = fields[0].string
            exchange = 'XNAS' if fields[0].a.get('href').find('nasdaq') != -1 else 'XNYS'
            main_page = 'http://www.morningstar.com/stocks/' + exchange + '/' + symbol + '/quote.html'
            profile_page = main_page + '#sal-components-company-profile'
            price_vs_fair_value = main_page + '#sal-components-price-fairvalue'
            financials = main_page + '#sal-components-financials'
            valuation = main_page + '#sal-components-valuation'
            performance = main_page + '#sal-components-oper-perf'

            # fix as now they have links to the companies on WP
            name = ' '.join(fields[1].stripped_strings)
            sector = fields[3].string
            sub_sector = fields[4].string
            records.append([symbol, name, exchange, sector, sub_sector, profile_page, price_vs_fair_value, financials, valuation, performance])

    header = ['Symbol', 'Name', 'Exchange', 'Sector', 'Sub Sector', 'Profile Page', 'Price vs Fair Value', 'Financials', 'Valuation', 'Performance']
    writer = csv.writer(open('../data/constituents.csv', 'w'), lineterminator='\n')
    writer.writerow(header)
    # Sorting ensure easy tracking of modifications
    records.sort(key=lambda s: s[1].lower())
    writer.writerows(records)

    with open("template.html") as fp:
        soup = BeautifulSoup(fp, "html.parser")

    doc, tag, text, line = Doc().ttl()
    with tag('tbody'):
        for record in records:
            with tag('tr'):
                with tag('td'):
                    text(record[0])
                with tag('td'):
                    text(record[1])
                with tag('td'):
                    text(record[2])
                with tag('td'):
                    text(record[3])
                with tag('td'):
                    text(record[4])
                with tag('td'):
                    line('a', 'link', href=record[5])
                with tag('td'):
                    line('a', 'link', href=record[6])
                with tag('td'):
                    line('a', 'link', href=record[7])
                with tag('td'):
                    line('a', 'link', href=record[8])
                with tag('td'):
                    line('a', 'link', href=record[9])


    final = soup.prettify().replace("##placeholder##", doc.getvalue())

    with open('../data/index.html', 'w') as file_:
        file_.write(final)

def process():
    retrieve()
    extract()

if __name__ == '__main__':
    process()
