# app.py
# Created by S. Hück on 02.09.2022

import logging
import ntpath
import os
from re import L
from datetime import date

import numpy as np
import pandas as pd

'''
### HOW TO USE ###
- 
- TODO: 
'''

# TODO:
# - 

def main():

    # Set up logging
    logging.basicConfig(  # filename='example.log',
        format='%(levelname)s: %(message)s',
        level=logging.INFO)

    
    input_root_dir = os.getcwd() + '/reports_in/'
    input_file_name = 'Fidor mantrafant Kontoumsätze 2019.csv'
    input_file_abs_path = input_root_dir + input_file_name
    logging.info(
        f'... reading {input_file_name} was successful.\n')

    df = pd.read_csv(input_file_abs_path,
                     encoding='ISO-8859-1',
                     sep=';',
                     decimal=',',
                     dtype={
                         'Beschreibung': 'str',
                         'Beschreibung2': 'str',
                         'Wert': 'str'
                         # 'Order Date': 'category',
                         
                     },
                     # converters={'total-amount': convert_decimal, 'amount': convert_decimal}, # not used with VAT reports

                     # datetime format is too custom, conversion done in separate pd.to_datetime
                     infer_datetime_format = True,
                     parse_dates=['Datum'], dayfirst=True
                     )

    
    df['Wert'] = df['Wert'].str.replace(',', '.').apply(pd.to_numeric, errors='coerce')
    
    substring_dict = {
        'PayPal (Europe)': 'PayPal', 
        'Fidor': 'Fidor',
        'Yongkang Powertec': 'Yongkang Powertec',
        'Claudia Matt PIMPINELLA' : 'Claudia Matt PIMPINELLA',
        'Amazon Europe Core S.A.R.L.' : 'Amazon Europe Core S.A.R.L.',
        'Amazon Payments Europe S.C.A.': 'Amazon Payments Europe S.C.A.',
        'Fidor' : 'Fidor',
        'Fremdwaehrungsgebuehr': 'Fidor Fremdwaehrungsgebuehr',
        'Upwork': 'Upwork',
        'STEUERVERWALTUNG NRW': 'STEUERVERWALTUNG NRW',
        'Avocado Store GmbH': 'Avocado Store GmbH',
        'Billbee GmbH': 'Billbee GmbH',
        'QIMA': 'QIMA',
        'DRIVENOW': 'DriveNow',
        'Shell': 'Shell',
        'GOOGLE*ADS': 'Google Ads',
        'Gymshark': 'Gymshark',
        'Aktivitaetsbonus': 'Fidor',
        'Kontofuehrung': 'Fidor',
        'Q PARK': 'Q PARK',
        'KAFFEESAURUS': 'Kaffeesaurus',
        'Kaffeesapiens': 'Kaffeesapiens',
        'FEEDBACKWHIZ': 'Feedbackwhiz',
        'R/D RAZZLE DAZZLE UG': 'RD Razzle Dazzle UG',
        'Peter Pane': 'Peter Pane',
        'Unicorn.Berlin': 'Unicorn Berlin',
        'DB Bahn': 'DB Bahn',
        'Vapiano': 'Vapiano',
        'Eurowings': 'Eurowings',
        'COA GASTRONOMIE GMBH': 'COA Gastronomie GmbH',
        'Tankstelle Peter': 'Tankstelle Peter',
        'Gloria Jeans Coffee': 'Gloria Jeans Coffee',
        'COFFEE FELLOWS': 'Coffee Fellows',
        'Jugendbildungsstatte der PSG e.V.': 'Jugendbildungsstatte der PSG e.V.',

        }
    for substring, new_key_string in substring_dict.items():
        df.loc[df['Beschreibung'].str.contains(substring, case=False), 'Empfänger/Absender'] = new_key_string
    
    print(df)
    
    ### Create output folder with today's date ###
    today = date.today().strftime('%Y-%m-%d')
    if not os.path.isdir('out/' + today):
        os.makedirs('out/' + today)
    logging.debug("created folder : ", today)

    ### Export newly formatted CSV ###
    #all_outgoing_sales_invoices_df[bb_reference_df.columns].to_csv('out/' + today + '/' + 'Alle Monate gesammelt' + '.csv',
    df.to_csv('out/' + today + '/' + input_file_name + ' 2bb' + '.csv',
                           decimal=',',    # Decimal separator is 'comma'
                           float_format='%.2f',  # Two decimal digits
                           sep=';',
                           index=False
                           )
    exit()

    ### create empty DataFrame reference for Buchhaltungsbutler import with column names and types ###
    ## INFO: Buchhaltungsbutler CSV Konfiguration Typ 2 mit pos.  und neg. Beträgen ##
    # Das "Konto" muss dem Basiskonto (Bank, Kasse, Debitor, Kreditor) entsprechen und das Aufwands-/Ertragskonto muss als Gegenkonto definiert sein.
    # Bei dieser Konfiguration ohne Soll-/Haben-Kennzeichen bedingt der Betrag, welches Konto im Soll und welches im Haben steht: Bei positivem Betrag steht das Basiskonto (Konto) im Soll und das Gegenkonto im Haben, bei negativem Betrag ist es umgekehrt.
    bb_reference_df = pd.DataFrame({'Datum (vollständig)': pd.Series(dtype='str'),
                   'Gegenpartei': pd.Series(dtype='str'),
                   'Rechnungsnummer': pd.Series(dtype='str'),
                   'Betrag in EUR': pd.Series(dtype='float'),
                   'Konto': pd.Series(dtype='str'),
                   'Gegenkonto': pd.Series(dtype='str'),
                   'Zahlungsreferenz': pd.Series(dtype='str'),
                   'Buchungstext': pd.Series(dtype='str')
                   })

    ### Create output folder with today's date ###
    today = date.today().strftime('%Y-%m-%d')
    if not os.path.isdir('out/' + today):
        os.makedirs('out/' + today)
    logging.debug("created folder : ", today)

    ### Export Overivew CSV with all reports included ###
    all_outgoing_sales_invoices_df[bb_reference_df.columns].to_csv('out/' + today + '/' + 'Alle Monate gesammelt' + '.csv',
                           decimal=',',    # Decimal separator is 'comma'
                           float_format='%.2f',  # Two decimal digits
                           sep=';',
                           index=False
                           )
    
    logging.info('Generating Outputs:')
    logging.info(f'Created new folder: {today}')
    logging.info(f'Generated "Alle Monate gesammelt.CSV" file in folder {today}')

    
    generate_monthly_reports(all_outgoing_sales_invoices_df, get_year_month_list(all_outgoing_sales_invoices_df), bb_reference_df, today)
    logging.info(f'Generated sales invoice CSV file for every month separately in folder {today}')
if __name__ == '__main__':
    main()
