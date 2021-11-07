import csv
from datetime import tzinfo, timedelta, datetime
import sys
import argparse

def convert_to_ledger_csv(input_files: list, output_file: str, pub_key: str):
    with open(output_file, 'w', newline='') as csvfileout:
        output_field_names = ['Operation Date', 'Currency Ticker', 'Operation Type', 'Operation Amount', 'Operation Fees', 
                    'Operation Hash', 'Account Name', 'Account xpub', 'Countervalue Ticker', 'Countervalue at Operation Date', 'Countervalue at CSV Export']
        writer = csv.DictWriter(csvfileout, fieldnames=output_field_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for file in input_files:
            with open(file, newline='') as csvfilein:
                reader = csv.DictReader(csvfilein)

                for index, row in enumerate(reader):

                    if 'Value' in row:
                        operation_amount =  row['Value']
                        tx_fees = 0
                        currency_ticker = row['TokenSymbol']
                    elif 'Value_OUT(MATIC)' in row:
                        operation_amount = row['Value_OUT(MATIC)'] if row['From'] == pub_key  else row['Value_IN(MATIC)']
                        tx_fees = row['TxnFee(MATIC)']
                        currency_ticker = 'MATIC'
                    else:
                        operation_amount = row['Value_OUT(AVAX)'] if row['From'] == pub_key  else row['Value_IN(AVAX)']
                        tx_fees = row['TxnFee(AVAX)']
                        currency_ticker = 'AVAX'

                    if operation_amount == "0":
                        operation_type = "FEES"
                    elif row['From'] == pub_key:
                        operation_type = "OUT"
                    else:
                        operation_type = "IN"
                
                    writer.writerow({
                        'Operation Date': datetime.fromisoformat(row['DateTime']).isoformat(timespec='milliseconds')+'Z',
                        'Operation Fees': tx_fees,
                        'Operation Hash': row['Txhash'],
                        'Account xpub': pub_key,
                        'Currency Ticker': currency_ticker.replace('.e', ''),
                        'Countervalue Ticker': 'USD',
                        'Operation Type': operation_type,
                        'Operation Amount': operation_amount.replace(',', '')
                        })

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-pub', dest='pub_key', type=str, help='Clé publique', required=True)
    parser.add_argument('-i', nargs='+', dest='input_files', help='Chemins des fichiers de transactions Polygonscan CSV', required=True)
    parser.add_argument('-o', dest='output_file', type=str, help='Chemin du fichier de transactions CSV au format Ledger', required=True)

    args = parser.parse_args()

    convert_to_ledger_csv(args.input_files, args.output_file, args.pub_key)