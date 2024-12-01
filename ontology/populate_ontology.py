import os
import requests
from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
import re
load_dotenv()
ONTOLOGY_FILE_PATH = 'empty_animals_ontology.rdf'
NEW_ONTOLOGY_FILE_PATH = 'populated_ontology.rdf'
ANIMALS_API_KEY = os.getenv('ANIMALS_API_KEY')

animals_graph = Graph()
animals_graph.parse(ONTOLOGY_FILE_PATH, format='xml')

animals_ontology = Namespace('http://www.semanticweb.org/tehno-trube/ontologies/2024/11/animals_ontology.owl#')


def get_json_from_name(name):
    api_url = 'https://api.api-ninjas.com/v1/animals?name={}'.format(name)
    response = requests.get(api_url, headers={'X-Api-Key': ANIMALS_API_KEY})
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)


def populate_ontology(json):
    cheetah_uri = URIRef(animals_ontology[json['name'].replace(" ", "_")])
    animals_graph.add((cheetah_uri, RDF.type, animals_ontology.Animal))

    taxonomy = json['taxonomy']
    taxonomy_uri = URIRef(animals_ontology[json['name'].replace(" ", "_") + "_taxonomy"])
    animals_graph.add((taxonomy_uri, RDF.type, animals_ontology.Taxonomy))
    
    for key, value in taxonomy.items():
        prop_uri = URIRef(animals_ontology[key])
        animals_graph.add((taxonomy_uri, prop_uri, Literal(value)))

    animals_graph.add((cheetah_uri, animals_ontology.hasTaxonomy, taxonomy_uri))

    locations = json['locations']
    for location in locations:
        location_uri = URIRef(animals_ontology[location])
        animals_graph.add((location_uri, RDF.type, animals_ontology.Location))
        animals_graph.add((cheetah_uri, animals_ontology.livesIn, location_uri))

    characteristics = json['characteristics']
    characteristic_uri = URIRef(animals_ontology[json['name'].replace(" ", "_") + "_characteristics"])
    animals_graph.add((characteristic_uri, RDF.type, animals_ontology.Characteristic))
    

    for key, value in characteristics.items():
        # delete special characters from key using regex
        key = re.sub(r'[^\w\s]', '', key)
        prop_uri = URIRef(animals_ontology[key])

        animals_graph.add((characteristic_uri, prop_uri, Literal(value)))

    animals_graph.add((cheetah_uri, animals_ontology.hasCharacteristic, characteristic_uri))

#names is list of 20 basic animals
names = ['cheetah', 'lion', 'tiger', 'elephant', 'giraffe', 'zebra', 'rhinoceros', 'hippopotamus', 'crocodile', 'alligator', 'penguin', 'koala', 'kangaroo', 'panda', 'koala', 'kangaroo', 'panda', 'monkey', 'gorilla', 'chimpanzee']
for name in names:
    try:
        json = get_json_from_name(name)
        print(json[0])
        populate_ontology(json[0])
    except:
        print("Error while populating ontology for", name)
animals_graph.serialize(NEW_ONTOLOGY_FILE_PATH, format="xml")
