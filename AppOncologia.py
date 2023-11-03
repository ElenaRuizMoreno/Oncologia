#==================================================================================================================================
#IMPORTAR BIBLIOTECAS
#==================================================================================================================================
import streamlit as st
import pandas as pd
import base64

#==================================================================================================================================
#CONFIGURACIÓN DE LA PÁGINA
#==================================================================================================================================

st.set_page_config(layout="wide", page_icon='Logo_pagina(2).png', page_title="Oncology")

st.image("Logo(3).png",use_container_width=True)

left, right = st.columns([1,1], gap="large")

#==================================================================================================================================
#COLUMNA IZQUIERDA
#==================================================================================================================================

with left:
    texto = '<p></p><i><p style="font-family:Arial; font-size: 25px;">Datos identificativos del paciente</p></i>'
    st.write(texto,unsafe_allow_html=True)

    nombre = st.text_input(label="NOMBRE", placeholder = "Introduzca su nombre: ")
    apellidos = st.text_input(label="APELLIDOS", placeholder = "Y sus apellidos: ")
    nhi = st.text_input(label="Nº HISTORIA CLÍNICA", placeholder = "Nº Historia Clínica: ")
    sexo = st.selectbox("SEXO",['-','Hombre','Mujer','Otro'])
    fecha_n = st.text_input(label="FECHA DE NACIMIENTO: ", placeholder = "(dd/mm/yyyy)")

#==================================================================================================================================
#COLUMNA DERECHA
#==================================================================================================================================

with right:
    texto = '<p></p><i><p style="font-family:Arial; font-size: 25px;">Datos patológicos</p></i>'
    st.write(texto,unsafe_allow_html = True)

    enfermedad = st.text_input(label="ENFERMEDAD ACTUAL", placeholder = "Escriba la principal patología del paciente")
    otras_e = st.text_input(label="OTRAS PATOLOGÍAS", placeholder = "Introduzca las patologías separadas por comas")

    texto = '<p></p><i><p style="font-family:Arial; font-size: 25px;">Datos tratamiento</p></i>'
    st.write(texto,unsafe_allow_html = True)
    tratamiento = st.text_input(label="TRATAMIENTO", placeholder = "Introduzca los fármacos separados por comas")
    farmacos = tratamiento.split(',')
    farmacos = [i.strip().lower() for i in farmacos]

#==================================================================================================================================
#PARTE INFERIOR
#==================================================================================================================================

#DEFINICIÓN DE FUNCIONES
#_________________________________________________________________________________________________________________________________

def buscarAlelosGen(gen):
    import json
    import requests
    listaAlelos=[]
    url="https://api.cpicpgx.org/v1/allele?genesymbol=eq."+gen
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    for i in range(len(datos)):
        alelo=datos[i]["name"]
        listaAlelos.append(alelo)
    setAlelos=set(listaAlelos)
    ListaFiltradaAlelos=(list(setAlelos))
    ListaFiltradaAlelos.sort()
    return ListaFiltradaAlelos

def ID_CPIC_Farmaco(nombreFarmaco):
    import json
    import requests
    url="https://api.cpicpgx.org/v1/drug?name=eq."+nombreFarmaco
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    if len(datos) != 0:
        ID_Farmaco=datos[0]['drugid']
        return ID_Farmaco
    else:
        return ''

def fenotipoSegunAlelos(gen,alelo1,alelo2):
    import json
    import requests
    listaAlelos=[]
    #url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2C19&diplotype=eq.*17/*17"
    url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq."+gen+"&diplotype=eq."+alelo1+"/"+alelo2
    response= requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    return datos

def urlGuia(farmaco,ID):
    import json
    import requests
    url = 'https://api.cpicpgx.org/v1/drug?name=eq.'+farmaco+'&select=drugid,name,guideline_for_drug(*)'
    response = requests.get(url)
    json_obtenido = response.json()
    datos = json_obtenido
    for i in datos:
        if i['guideline_for_drug']['id'] == ID:
            return i['guideline_for_drug']['url']
        
def recomendacionClinica(gen,alelo1,alelo2,farmaco):
    lista = []
    fenotipo = fenotipoSegunAlelos(gen,alelo1,alelo2)
    if len(fenotipo) != 0:
        lookupkey= fenotipo[0]['lookupkey']
        ID_Farmaco=ID_CPIC_Farmaco(farmaco)
        import json
        import requests
        url='https://api.cpicpgx.org/v1/recommendation?select=drug(name), guideline(name), * &drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{\"'+list(lookupkey.keys())[0]+'":"'+list(lookupkey.values())[0]+'"}'
        response = requests.get(url)
        json_obtenido = response.json()
        datos=json_obtenido
        if len(datos) != 0:
            lista.append(fenotipo[0]['generesult'])
            lista.append(datos[0]['drugrecommendation'].encode('latin-1','ignore').decode('latin-1'))
            lista.append(datos[0]['guideline']['name'])
            lista.append(urlGuia(farmaco,datos[0]['guidelineid']))
    return lista

def BuscarFarmacosRelacionadosGen(gen):
    import json
    import requests
    listaFarmacos=[]
    url="https://api.pharmgkb.org/v1/data/clinicalAnnotation?location.genes.symbol="+gen
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    if datos['status'] == 'success':
        for i in range(len(datos["data"])):
            farmaco=datos["data"][i]["relatedChemicals"][0]["name"]
            listaFarmacos.append(farmaco)
    setFarmacos=set(listaFarmacos)
    ListaFiltradaFarmacos=(list(setFarmacos))
    ListaFiltradaFarmacos.sort()
    return ListaFiltradaFarmacos

#CÓDIGO DE STREAMLIT
#_________________________________________________________________________________________________________________________________

texto = '<p></p><i><p style="font-family:Arial; font-size: 25px;">Datos genéticos</p></i>'
st.write(texto,unsafe_allow_html = True)

col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,1], gap="large")

with col1:
    gen1 = st.text_input(label="Gen 1", placeholder = "Introduzca el gen")
    lista1 = buscarAlelosGen(gen1)
    alelo1_1 = st.selectbox("Alelo 1",['-']+lista1, key = 11)
    alelo1_2 = st.selectbox("Alelo 2",['-']+lista1, key = 12)
    
with col2:
    gen2 = st.text_input(label="Gen 2", placeholder = "Introduzca el gen")
    lista2 = buscarAlelosGen(gen2)
    alelo2_1 = st.selectbox("Alelo 1",['-']+lista2, key = 21)
    alelo2_2 = st.selectbox("Alelo 2",['-']+lista2, key = 22)

with col3:
    gen3 = st.text_input(label="Gen 3", placeholder = "Introduzca el gen")
    lista3 = buscarAlelosGen(gen3)
    alelo3_1 = st.selectbox("Alelo 1",['-']+lista3, key = 31)
    alelo3_2 = st.selectbox("Alelo 2",['-']+lista3, key = 32)
    

    
genes = [gen1,gen2,gen3]
alelos1 = [alelo1_1,alelo2_1,alelo3_1]
alelos2 = [alelo1_2,alelo2_2,alelo3_2]

#==================================================================================================================================
#OBTENCIÓN DE RESULTADOS
#==================================================================================================================================

recomendaciones = dict()
for i in farmacos:
    recomendaciones[i] = dict()
    for x, y, z in zip(genes, alelos1, alelos2):
        if y != '-' and z != '-':
            recomendaciones[i][x] = recomendacionClinica(x,y,z,i)
            
relaciones = dict()
for x,y,z in zip(genes, alelos1, alelos2):
    if y != '-' and z != '-':
        relaciones[x] = BuscarFarmacosRelacionadosGen(x)


    
#==================================================================================================================================
#MOSTRAR RESULTADOS
#==================================================================================================================================   
texto = '<center><p style="font-family:Arial; font-size: 35px;">INFORMACIÓN EXTRAÍDA</p></center>'
st.write(texto,unsafe_allow_html = True)
#--------------------------------------------------------------------------------------------------------------------------
texto = '<i><p style="font-family:Arial; font-size: 22px;"><u>FENOTIPO Y RECOMENDACIÓN DE DOSIS</u></p></i>'
st.write(texto,unsafe_allow_html = True)

for i in recomendaciones:
    texto = '<p style="text-indent: 30px; font-family:Arial; font-size: 18px;">En relación con el fármaco <b>'+i+'</b>:</p>'
    st.write(texto,unsafe_allow_html = True)          
    for x in recomendaciones[i]:
        if len(recomendaciones[i][x]) == 0:
            texto = '<p style="text-indent: 50px; font-family:Arial; font-size: 15px;">No hay información sobre interacciones con <b>'+x+'</b> para esos alelos.</p>'
            st.write(texto,unsafe_allow_html = True)
        else:
            texto = '<p style="text-indent: 50px; font-family:Arial; font-size: 15px;">El fenotipo para <b>'+x+'</b> es '+recomendaciones[i][x][0]+'. Recomendación clínica: '+recomendaciones[i][x][1]+' Fuente de información: <a href="'+recomendaciones[i][x][3]+'" target= "_blank">'+recomendaciones[i][x][2]+'</a></p>'
            st.write(texto,unsafe_allow_html = True)
#--------------------------------------------------------------------------------------------------------------------------   
texto = '<i><p style="font-family:Arial; font-size: 22px;"><u>Interacciones con otros fármacos</u></p></i>'
st.write(texto,unsafe_allow_html = True)

for i in relaciones:
    texto = '<p style="text-indent: 30px; font-family:Arial; font-size: 15px;">Fármacos metabolizados por <b>'+i+'</b>: '+str(', '.join(relaciones[i]))+'.'+'</p>'
    st.write(texto,unsafe_allow_html = True)
