import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re


def extraer_info_producto(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.text,"html.parser")

    diccionario_campos = {
        "score": lambda: soup.find("span", {"class": "stamped-badge-caption"})["data-rating"].replace(",", "."),
        "reviews": lambda: soup.find("span", {"class": "stamped-badge-caption"})["data-reviews"],
        "vertical": lambda: " ".join(soup.find("div", {"class": "container pango-breadcrumb"}).text.strip().split()[2:]),
        "description": lambda: soup.find("div", {"class": "cc-accordion"}).text.replace("\n", "-"),
        "politica_envios": lambda: [elemento.text.replace("\n", "-") for elemento in soup.findAll('div', {"class": "product-detail-accordion not-in-quickbuy"}) if elemento.find("summary").text == "Política de envíos"][0],
        "impacto": lambda: [elemento.text.replace("\n", "-") for elemento in soup.findAll('div', {"class": "product-detail-accordion not-in-quickbuy"}) if elemento.find("summary").text == "Impacto ambiental"][0],
        "desglose_costes": lambda: [elemento.text.replace("\n", "-") for elemento in soup.findAll('div', {"class": "product-detail-accordion not-in-quickbuy"}) if elemento.find("summary").text == "Desglose de costes"][0],
        "material2": lambda: soup.find('span', {"class": 'with-icon__beside'}).text,
        "cultivo": lambda: " # ".join([element.text for element in soup.find("div", {"class": "flexible-layout"}).find_all("div", {"class": "column"})[0].findChildren()]),
        "confeccion": lambda: " # ".join([element.text for element in soup.find("div", {"class": "flexible-layout"}).find_all("div", {"class": "column"})[1].findChildren()]),
        "logistica": lambda: " # ".join([element.text for element in soup.find("div", {"class": "flexible-layout"}).find_all("div", {"class": "column"})[2].findChildren()])
    }



    diccionario_rellenar = {
        "score": None,
        "reviews": None,
        "vertical": None,
        "description": None,
        "politica_envios": None,
        "impacto": None,
        "desglose_costes": None,
        "material2": None,
        "cultivo": None,
        "confeccion": None,
        "logistica": None
    }


    for key, function_dict in diccionario_campos.items():
        try:
            diccionario_rellenar[key] = function_dict()
        except:
            diccionario_rellenar[key] = np.nan

    return [*diccionario_rellenar.values()]


def sacar_productos_pagina(soup, diccionario_extract, diccionario):
    try:
        product_cards_list = soup.find("div",{"class":"product-list product-list--per-row-3 product-list--per-row-mob-2 product-list--per-row-mob-2 product-list--image-shape-shortest"}).findChildren("div",recursive=False)
    except:
        return diccionario
    for product_card in product_cards_list:
        for campo, valor_func in diccionario_extract.items():
            try:
                diccionario[campo].append(valor_func(product_card))
        
            except:
                diccionario[campo].append(np.nan)
    return diccionario