#!/usr/bin/python3

import os
import requests
import sqlite3
from sqlite3 import Error
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import time
from time import sleep

data_base = "covidDB"

def conn(db_file):

    conn = None
   
    try:
        conn = sqlite3.connect(db_file)

    except Error as e:
        print(e)

    return conn

def insert_into_casos(db_file, datos):
   
    BD = conn(db_file)

    try:
        cursor = BD.cursor()
        cursor.execute("insert into casos values (?,?,?,?,?)", datos)
        BD.commit()

    except Error as e:
        print(e)

    finally:
        BD.close()

def delete_duplicates(db_file, fecha_datos):

    BD = conn(db_file)
    fecha_tabla = [fecha_datos]
    fecha = ""

    try:
        cursor = BD.cursor()

        fecha = cursor.execute("select fecha from casos where fecha = (?)", fecha_tabla)
        
        fecha = cursor.fetchone()       
   
    except Error as e:
        print(e)
    
    finally:
        BD.close()

    return fecha


def data_date():

    url = 'https://www.emol.com/especiales/2020/internacional/coronavirus/casos-chile.asp'

    page = requests.get(url, verify=False)

    soup = BeautifulSoup(page.content, 'html.parser')

    fecha_de_los_datos = soup.find("div", {"class":"header_nota_tabla"})

    fecha_datos = (fecha_de_los_datos.text[33:-1] +', '+ time.strftime("%Y", time.localtime()))


    return fecha_datos

def all_rows(db_file):

    BD = conn(db_file)

    filas = []

    try:
        cursor = BD.cursor()

        filas = cursor.execute("select * from casos")

        filas = cursor.fetchall()

    except Error as e:
        print(e)

    finally:
        BD.close()


    return len(filas)

def cifras_covid(fecha_datos):

    ID = all_rows(data_base) + 1

    url = 'https://www.emol.com/especiales/2020/internacional/coronavirus/casos-chile.asp'

    page = requests.get(url, verify=False)

    soup = BeautifulSoup(page.content, 'html.parser')

    casos = soup.find("table", {"id": "tabla-detalle-x-region"})

    cifras = casos.text[880:905]

    cifras.split(' ')
    datos = list(cifras.rstrip().lstrip())

    casos_nuevos = datos[0] + datos[1]+ datos[2]+ datos[3]+ datos[4]
    casos_activos = datos[6] + datos[7] + datos[8]+ datos[9]+ datos[10]+ datos[11]
    casos_totales = (datos[13] + datos[14]+ datos[15] 
                    + datos[16]+ datos[17]+ datos[18] + datos[19]+ datos[20]+ datos[21])

    resumen = [ID, casos_nuevos,casos_activos,casos_totales,fecha_datos] 
     

    return resumen


def new_data():

    success = False

    fecha_hoy = data_date()

    consulta_duplicados = delete_duplicates(data_base,fecha_hoy)

    if consulta_duplicados == None:
        
        insert_into_casos(data_base, cifras_covid(data_date()))
        success = True
    
    elif fecha_hoy == consulta_duplicados[0]:

        print("\n los datos de hoy ya fueron agregados a la base de datos \n")

    else:
        
        insert_into_casos(data_base, cifras_covid(data_date()))



    return success

def view_data(db_file, fecha_datos):

    BD = conn(db_file)

    fecha_tabla = [fecha_datos]

    try:
        
        cursor = BD.cursor()

        datos = cursor.execute("select nuevos, activos, total, fecha from casos where fecha = (?)", fecha_tabla) 

        datos = cursor.fetchone()

        success = True


    except Error as e:
        print(e)

    finally:
        BD.close()

    return datos

def all_data(db_file, ID):
    
    BD = conn(db_file)

    id_data = [ID]

    try:
        
        cursor = BD.cursor()

        datos = cursor.execute("select nuevos, activos, total, fecha from casos where ID = (?)", id_data)

        datos = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        BD.close()

    return datos

if __name__ == '__main__':

    while True:

        table = PrettyTable(['Casos Nuevos', 'Casos Activos', 'Casos Totales', 'Fecha'])
        choice = 0
        while True:

            print("\n Balance Covid Chile \n")
            print("Opciones: \n 1: Insertar nuevos datos \n 2: Consultar cifras hoy \n 3: Consultar cifras por fecha \n 4: Consultar todos los datos \n 5: Salir")
            try:

                choice = int(input("\n Opción: "))
                break;

            except:

                print("Valor ingresado invalido. Reintente.")
         
        if choice == 1:

            if new_data():
                print("datos ingresados")

        elif choice == 2:

            table.add_row(view_data(data_base,data_date()))

            print(table)

        elif choice == 3:

            date = None

            while True:
                try:
                    print("\n ej: 20 de noviembre, 2021")

                    date = input("\n Ingrese la fecha a consultar: ")

                    table.add_row(view_data(data_base, date))

                    print(table)
                    break;

                except:
                    print("\n Fecha no registrada en la base de datos")


        elif choice == 4:

            rows = all_rows(data_base)
            
            for i in range(1 ,rows + 1):
                table.add_row(all_data(data_base, i))

            print(table)

        elif choice == 5:
            print("\n Saliendo.....")
            sleep(1)
            break;
