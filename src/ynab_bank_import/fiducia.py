"""Convert FIDUCIA csv files"""

import csv
import decimal
import logging


log = logging.getLogger(__name__)


class Dialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def import_account(filename, ynab):
    ## Skipping first lines with unneeded information
    with open(filename, newline='', encoding='ISO-8859-15') as f:
        bank_file = f.readlines()

    for record in csv.DictReader(bank_file, dialect=Dialect):
        # Skipping last lines "Anfangssaldo" and "Endsaldo"
        if (record['Buchungstext'] == "Anfangssaldo" or record['Buchungstext'] == "Endsaldo"):
            continue

        t = ynab.new_transaction()
        t.Date = record['Buchungstag']
        t.Payee = record['Name Zahlungsbeteiligter']

        subject = record['Verwendungszweck']
        subject = subject.replace('\n', '').strip()

        t.Memo = subject
        amount = decimal.Decimal(
            record['Betrag'].replace('.', '').replace(',', '.'))

        # Last column indicates positive / negative amount
        if amount < 0:
            t.Outflow = abs(amount)
        else:
            t.Inflow = amount

        ynab.record_transaction(t)
