# app.py
# Created by S. Hück on 02.09.2022

import logging
import ntpath
import os
from re import L
from datetime import date
from tkinter import E

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
    #input_file_name = 'Fidor mantrafant Kontoumsätze 2018.csv'
    #input_file_name = 'Fidor mantrafant Kontoumsätze 2019.csv'
    #input_file_name = 'Fidor mantrafant Kontoumsätze 2020.csv'
    input_file_name = 'Fidor mantrafant Kontoumsätze 01-10 2021.csv'

    input_file_abs_path = input_root_dir + input_file_name
    print()
    logging.info(f'Reading {input_file_name} was successful.')

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

    
    df['Wert'] = df['Wert'].str.replace('.','',regex=False).str.replace(',', '.',regex=False).apply(pd.to_numeric, errors='coerce')
    
    substring_dict = pd.read_csv(os.getcwd() + '/references/' + 'fidor_beschreibung_reference.csv', sep=';', header=None, index_col=0).squeeze().to_dict()
    
    for substring, new_key_string in substring_dict.items():
        if type(substring) == str:  # empty rows in reference CSV are interpreted as 'nan'. Disregard those.
            df.loc[df['Beschreibung'].str.contains(substring, case=False, regex=False), 'Absender/Empfänger aus Beschreibung'] = new_key_string
    
    # Get string after Empfaenger/Absender until before next comma
    df['extract_from_Beschreibung2'] = df['Beschreibung2'].replace({r'(\w+er\s\s)(.+)(, IBAN.+)' : r'\2'}, regex=True)
    #df['IBAN'] = df['Beschreibung2'].replace({r'(.+)(IBAN\s\s)([\d\w]+)(.+)' : r'\3'}, regex=True)
    df['IBAN'] = df['Beschreibung2'].str.extract(r'IBAN\s+([\d\w]+)')
    df['BIC'] = df['Beschreibung2'].str.extract(r'BIC\s+([\d\w]+)')
    #df['Beschreibung2'].replace({r'(\w+),\s+(\w+)' : r'\2 \1', 'Max':'Fritz'}, regex=True)
    
    # create Absender/Empfänger column by combining Beschreibung + Beschreibung2 information
    df['Absender/Empfänger'] = df['Absender/Empfänger aus Beschreibung']
    df.loc[pd.isnull(df.loc[:, 'Absender/Empfänger aus Beschreibung']), 'Absender/Empfänger'] = df.loc[:, 'extract_from_Beschreibung2']

    df['Datum'] = df['Datum'].dt.strftime('%d.%m.%Y')
    df.rename(columns={ "Beschreibung": "Verwendungszweck",
                        "Beschreibung2": "Buchungstext",
                        "Datum": "Buchungsdatum",
                        "Wert": "Betrag"
                        }, inplace=True)


    ### Create output folder with today's date ###
    today = date.today().strftime('%Y-%m-%d')
    if not os.path.isdir('out/' + today):
        os.makedirs('out/' + today)
    logging.debug("created folder : ", today)

    ### Export newly formatted CSV ###
    #all_outgoing_sales_invoices_df[bb_reference_df.columns].to_csv('out/' + today + '/' + 'Alle Monate gesammelt' + '.csv',
    selected_columns = ['Buchungsdatum', 'Absender/Empfänger', 'Verwendungszweck', 'Buchungstext', 'IBAN', 'BIC', 'Betrag']
    df[selected_columns].to_csv('out/' + today + '/' + input_file_name[:-4] + ' 2bb' + '.csv',
                           decimal=',',    # Decimal separator is 'comma'
                           float_format='%.2f',  # Two decimal digits
                           sep=';',
                           index=False
                           )
    
    logging.info(f'Generated output file {input_file_name[:-4]} 2bb.csv in folder: {today}')

if __name__ == '__main__':
    main()
