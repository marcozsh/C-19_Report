import os
import requests
import sqlite3
from sqlite3 import Error
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import time
from time import sleep



data_date = time.strftime("%d-%m-%y", time.localtime())

data_base = "covidDB"

def conn(db_file):

    conn = None
   
    try:
        conn = sqlite3.connect(db_file)

    except Error as e:
        print(e)

    return conn



def view_data(db_file, fecha_datos):

    BD = conn(db_file)

    a = [fecha_datos]

    try:
        
        cursor = BD.cursor()

        datos = cursor.execute("select nuevos, activos, total, fecha from casos where fecha = (?)", a) 

        datos = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        BD.close()

    return datos



if __name__ == '__main__':

    # print(type(date))
    table = PrettyTable(['Casos Nuevos', 'Casos Activos', 'Casos Totales', 'Fecha'])
   
    table.add_row(view_data(data_base,data_date))
    
    print(table)

