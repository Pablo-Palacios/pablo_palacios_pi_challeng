import json
from pydantic import BaseModel
from typing import Optional
from faker import Faker
import cohere
from dotenv import load_dotenv
import os
from .config import get_data_user,add_data_user,User,query_vector,guardar_chat_ask,guardar_chat_personal
from fastapi import HTTPException
import requests
from .views import get_top_10_coins, especifict_coint_valor


load_dotenv() 

api_key = os.getenv("COHERE_KEY")
#api_key = "O3WlMhRr2RPAo816yI5InQK0rBfNIIHm5xpHf9ro"

co = cohere.ClientV2(api_key)

#print(api_key)
faker = Faker()


class NewDocument(BaseModel):
    id: Optional[int] = faker.random_number(digits=3)
    title: str
    content: Optional[str] = None



class Embeddigns(BaseModel):
    document_id: int

class Chatbot(BaseModel):
    question: str


document_pdf_list: dict[int, NewDocument] = {}

document_list: dict[int, NewDocument] = {}

document: dict[int, NewDocument] = {}



def convertir_embeddigns(consulta):
    response = co.embed(
                        texts=[consulta],
                        model="embed-multilingual-v2.0",
                        input_type="search_document",
                        embedding_types=["float"]
                    )
    return response.embeddings.float_



def chat_ask(contexto,consulta):
    
    model_ = "command-r-plus"
    prompt = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual. 
                   Te proporcionare un contexto para tengas un mejor panorama: {contexto}.
                   Tu tarea es asociar la pregunta del usuario y el contexto generado, elaborando una respuesta
                   de una oracion que responda la pregunta del usuario. Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                  {"role":"user", "content":f"{consulta}"}]
    )

    return prompt.message.content[0].text

# TENER EN CUENTA QUE EL CONTEXTO DEBE ESTAR EN EL ROLE USER Y EL SYSTEM NO SE DEBE MODIFICAR

def chat_search(contexto,consulta):
    
    model_ = "command-r-plus"
    prompt = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual. 
                   Te proporcionare un contexto para tengas un mejor panorama: {contexto}.
                   Tu tarea es asociar la pregunta del usuario, el contexto generado y buscar en la lista {document_list} el titulo y su id.
                   La respuesta debe ser el titulo, el document_id del documento y la primera frase en el content_snippet con el formato de diccionario como esta en la lista con sus keys y su contenido.
                   Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                  {"role":"user", "content":f"{consulta}"}]
    )

    return prompt.message.content[0].text


def chat_cripto(consulta):
    aviable_fuctions = {
        "top_10":get_top_10_coins,
        "valor_especifico":especifict_coint_valor}
    
    tools = [
        {
            "type":"function",
            "function":{
                "name":"top_10",
                "description":"""Funcion que devuelve el nombre y el volumen total las 10 monedas que tienen más actividad comercia en las ultimas 24 horas, 
                basado en la confianza o interés en el mercado en negociar puediendo ofrecer mejores oportunidades de trading debido a su alta liquidez.""",
                "parameters": { 
                    "type": "object",
                    "properties": {},  
                    "required": [] 
                }
            }
        },

        {
            "type":"function",
            "function":{
                "name":"valor_especifico",
                "description":"Retorna el valor actual de la coint crypto segun la moneda de intercambio",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "criptomoneda":{
                            "type":"string",
                            "description":"Nombre o abreviacion que representa la moneda crypto"
                        },
                         "moneda":{
                            "type":"string",
                            "description":"Nombre o abreviacion que representa la moneda de intercambio"
                        }
                    },
                    "required":["criptomoneda","moneda"]
                }
            }
        }
    ]
    
    model_ = "command-r-plus"
    question_embeddings = convertir_embeddigns(consulta)
    query = query_vector(question_embeddings)
    prompt = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual experto en criptomonedas, maestro en economia y finanzas. 
                   Tu tarea es asociar la pregunta del usuario, el contexto generado. Si la cosulta se entiende que es una consulta sobre las mejores monedas en el mercado o la cotizacion de alguna moneda en especifico, utiliza las funciones. Acordate de pedir la moneda de intercambio de ser necesario para la funcion
                   Debes proporcionar una respuesta coherente, que explique las caracteristicas tecnicamente. Agrega un listado de item de ser necesario.
                   Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                  {"role":"user", "content":f"{consulta} y {query}"}],
        max_tokens=1000,
        temperature=0.8,
        tools=tools
    ) 
    if not prompt.message.tool_calls:
        model_1 = prompt.message.content[0].text

        prompt_2 = co.chat(
            model=model_,
            messages=[{"role":"system","content":f""" Apasionado por la informática y la tecnología, Trader e inversionista estratégico . 
                    Vas a recibir el resumen emitido por el asistente virtual. Tu tarea sera revisar el resumen y extraer los datos mas principales e importantes, 
                    teniendo en cuenta la pregunta que implementa el usuario. Puedes utilizar items de ser necesarios. Si la consulta no es tecnica, puedes generar una conclusion en la respuesta como forma de consejo en base al analisis que concluyas.
                    Debes entender que al publico que pregunta no suele tener conocimientos sobre la materia. Debes propocionar todo analisis que hagas. Ten en cuenta si el usuario pide cuestiones especificas o algun parametro en la respuesta que desea, debes cumplirla al pie.
                    Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                    {"role":"user", "content":f"consulta usuario: {consulta} - contexto vectoral: {query} - modelo: {model_1}"}],
            max_tokens=800,
            temperature=0.4
        )
        response = prompt_2.message.content[0].text
        return response


    for t in prompt.message.tool_calls:
        function_name = t.function.name
        function_args = json.loads(t.function.arguments)
        #print(function_args)
        tool_response = aviable_fuctions[function_name](**function_args)
        promp_tool = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual experto en criptomonedas, maestro en economia y finanzas. 
                   Tu tarea es tomar las respuesta de las funciones y generar una minima explicacion detallada de no mas de 20 palabras.'"""},
                  {"role":"user", "content":f"{consulta} - {tool_response}"}])
        return promp_tool.message.content[0].text

   
    guardar_chat_ask(role="user",content=f"{consulta}")
    guardar_chat_ask(role="assistant", content=f"{response}")

    return response


def chat_asistente_data(consulta):
    model_ = "command-r-plus"

    aviable_fuctions = {
        "add_user":add_data_user,
        "get_information":get_data_user
    }

    tools = [
        {
            "type":"function",
            "function":{
                "name":"add_user",
                "description":"""Agregar los datos ingresados de una persona a la base de datos, agregando los datos nombre,
                                edad,ingreso fijo, ahorro. Mostrar el mensaje que retorna""",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "nombre":{
                            "type":"string",
                            "description":"Nombre del usuario"
                        },
                        "edad":{
                            "type":"integer",
                            "description":"numero de edad del usuario"
                        },
                        
                        "ingreso_fijo":{
                            "type":"integer",
                            "description":"Numero de sueldo o ingreso fijo que tiene el usuario en su poder"
                        },
                        "ahorro":{
                            "type":"integer",
                            "description":"Numero de la capacidad de ahorro que posee el usuario"
                        }
                        
                    },
                    "required":["nombre","edad","ingreso_fijo","ahorro"]
                }
            }
        },

        {
            "type":"function",
            "function":{
                "name":"get_information",
                "description":"Retorna los datos del usuario basandose en el nombre que este registrado en la base de datos.",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "nombre":{
                            "type":"string",
                            "description":"Nombre del usuario que esta asociado a la base de datos"
                        }
                    },
                    "required":["nombre"]
                }
            }
        }
    ]

    

    prompt_ = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente programador que sirve para registrar usuarios y traer informacion de una base de datos.
                   Tambien puedes interactuar de forma educada con el usuario si es necesario. Utiliza las funciones para interactuar con la base de datos.
                   Debes verificar que no se salte ningun dato y en caso de ser asi, debes remarcarle que dato falta y volver a pedirlo que los agregue."""},
                  {"role":"user", "content":f"{consulta}"}
                  ],
        tools=tools
        )
    if not prompt_.message.tool_calls:

        prompt_1 = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres el chatbot y debes mantener una conversacion sencilla. 
                   Debes indicarle al usuario que agregue sus datos personales para armar su registro en la base y poder ayudarlo en sus movimientos financieros en el futuro: nombre,edad, su ingreso fijo(importante),capacidad de ahorro (importante), eres activo en alguna inversion financiera. 
                   Si la consulta es sobre extraccion de datos, dile que necesitas el nombre del usuario para buscarlo en la base de datos."""},
                  {"role":"user", "content":f"{consulta}"}])
        
        response = prompt_1.message.content[0].text
        guardar_chat_personal(role="user", content=f"{consulta}")
        guardar_chat_personal(role="assistant", content=f"{response}")

        return response

    for t in prompt_.message.tool_calls:
        function_name = t.function.name
        function_args = json.loads(t.function.arguments)
        #print(function_args)
        missing_fields = [key for key, value in function_args.items() if value is None]
        if missing_fields:
            
            return {f"Faltan los siguientes campos obligatorios: {', '.join(missing_fields)}"}
        
        tool_response = aviable_fuctions[function_name](**function_args)

    

    response_final = co.chat(
                model=model_,
                messages=[{"role":"system", "content":"""Eres un profesor de programacion, que es capaz de recibir cualquier tipo de dato o variable para manipularlos segun el prompt del usuario. 
                        Debes ser capaz de responder o mostrar la informacion generada. Tu respuesta debe ser un mensaje sencillo. 
                        Recibiras la respuesta del modelo para que sigas la orientacion de su idea"""},
                        {"role":"user","content":f"Datos encontrados: {tool_response}"}])
            

    response = response_final.message.content[0].text
    guardar_chat_personal(role="user", content=f"{consulta}")
    guardar_chat_personal(role="assistant", content=f"{response}")

    return response


def chat_asistente_personal(consulta):
    model_ = "command-r-plus"

    aviable_fuctions = {
        "get_information":get_data_user
    }
        
    tools = [
        {
            "type":"function",
            "function":{
                "name":"get_information",
                "description":"Retorna los datos del usuario basandose en el nombre que este registrado en la base de datos.",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "nombre":{
                            "type":"string",
                            "description":"Nombre del usuario que esta asociado a la base de datos"
                        }
                    },
                    "required":["nombre"]
                }
            }
        },
        {
            "type":"function",
            "function":{
                "name":"top_10",
                "description":"""Funcion que devuelve el nombre y el volumen total las 10 monedas que tienen más actividad comercia en las ultimas 24 horas, 
                basado en la confianza o interés en el mercado en negociar puediendo ofrecer mejores oportunidades de trading debido a su alta liquidez.""",
                "parameters": { 
                    "type": "object",
                    "properties": {},  
                    "required": [] 
                }
            }
        }

    ]

    

    response_final = co.chat(
                model=model_,
                messages=[{"role":"system", "content":"""Eres un asistente virtual, tu deber es propocionar los datos del usuario basandote en su nombre. 
                           Si en el historial de la conversacion ya se manifesto el nombre y los datos del usuariom, deberas pasarle el dato de la funcion para que el modelo maneje mejor su analisis."""},
                        {"role":"user","content":f"{consulta}"}], tools=tools)
    
    if not response_final.message.tool_calls:
        return {f"Debes proporcionar el nombre del usuario para por extraer sus datos"}
    
    for t in response_final.message.tool_calls:
        function_name = t.function.name
        function_args = json.loads(t.function.arguments)
        tool_response = aviable_fuctions[function_name](**function_args)


    consulta_emb = convertir_embeddigns(consulta)
    query = query_vector(consulta_emb)

    prompt_ = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""
                    Actúa como un asesor financiero y estratega de inversiones de alto nivel, especializado en análisis de mercados financieros, gestión de riesgos y planificación estratégica. Tu objetivo es proporcionar análisis claros, concisos y accionables basados en datos del mercado, tendencias macroeconómicas y estrategias de trading avanzadas. Debes tener obligatoriamente en consideracion los datos del usuario  y la cotizaciones en el mercado actual que encontraras en las funciones: {tool_response} 

                    Tu enfoque debe incluir:

                    Identificación de oportunidades de inversión basadas en análisis técnico y fundamental.
                    Evaluación de riesgos asociados y posibles mitigaciones.
                    Generación de estrategias personalizadas para diversificación de portafolios y optimización de ganancias.
                    Respuestas precisas y contextualizadas para mercados específicos, incluyendo acciones, divisas, criptomonedas y commodities.
                    Gestión y recuerdo de datos proporcionados por el usuario, como su nombre y contexto financiero, para dar continuidad a la conversación y ofrecer recomendaciones alineadas con su perfil financiero.
                    Si en el historial de la conversación se ha indicado el nombre del usuario y otros datos relevantes, recuerda esta información para personalizar las recomendaciones y administrar sus finanzas de manera efectiva en futuros movimientos mientras avanza la conversación.
                    Comunicación profesional y enfocada en los objetivos del inversionista.
                    Recuerda proporcionar detalles concretos, ejemplos aplicables y explicaciones educativas que refuercen la toma de decisiones estratégicas. Además, si identificas lagunas de información, solicita los datos necesarios de forma clara y respetuosa. Si se solicita, sugiere herramientas, recursos o indicadores útiles para mejorar el análisis o la ejecución de las estrategias.
                    """},
                    {"role":"user", "content":f"{consulta} - bibliografia: {query}"}
                  ],
        max_tokens=900,
        temperature=0.5
        )
    
    prompt_2= co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente analista de inversiones. Tu tarea es poder formular un seguimiento de consejos acordes a la informacion acreditada para empezar a invertir. 
                   La idea es que en la respuesta, puedas establecer dos opciones para invertir de forma simple y profesional. Puedes recomendar billeteras virtuales, monedas, formas de invertir. Acuerdate tener en cuenta el historial del usuario. Que tus respuestas esten bien formuladas y sean sencillas. Debes completar tu respuesta, no puede quedar abierta."""},
                    {"role":"user", "content":f"{consulta} - analisis: {prompt_.message.content[0].text}"}
                  ],
        max_tokens=400,
        temperature=0.3
        )

    
    response = prompt_2.message.content[0].text
    guardar_chat_personal(role="user", content=f"{consulta}")
    guardar_chat_personal(role="assistant", content=f"{response}")

    return response
    



# def get_info_mercado():
#     endpoint = "/api/v3/exchangeInfo"
#     response = requests.get(api_cohere + endpoint)
#     if response.status_code == 200:
#         body = response.json()
        
#         symbols = body["symbols"]
#         active_symbols = []
#         for symbol in symbols:
#             if symbol["status"] == 'TRADING':
#                 active_symbols.append(symbol)
        
#         top_10_coins = active_symbols[:1]

#         for coin in top_10_coins:
#             print(coin)
#             print(coin["symbol"])


#print(get_info_mercado())

