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
    animal_uri = URIRef(animals_ontology[json['name'].replace(" ", "_")])
    animals_graph.add((animal_uri, RDF.type, animals_ontology.Animal))

    taxonomy = json['taxonomy']


    #Kingdom
    kingdom_uri = URIRef(animals_ontology[taxonomy['kingdom'].replace(" ", "_")])
    animals_graph.add((kingdom_uri, RDF.type, animals_ontology.Kingdom))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, kingdom_uri))

    #Phylum
    phylum_uri = URIRef(animals_ontology[taxonomy['phylum'].replace(" ", "_")])
    animals_graph.add((phylum_uri, RDF.type, animals_ontology.Phylum))
    animals_graph.add((phylum_uri, animals_ontology.belongsTo, kingdom_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, phylum_uri))

    #Class
    class_uri = URIRef(animals_ontology[taxonomy['class'].replace(" ", "_")])
    animals_graph.add((class_uri, RDF.type, animals_ontology.Class))
    animals_graph.add((class_uri, animals_ontology.belongsTo, phylum_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, class_uri))

    #Order
    order_uri = URIRef(animals_ontology[taxonomy['order'].replace(" ", "_")])
    animals_graph.add((order_uri, RDF.type, animals_ontology.Order))
    animals_graph.add((order_uri, animals_ontology.belongsTo, class_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, order_uri))

    #Family
    family_uri = URIRef(animals_ontology[taxonomy['family'].replace(" ", "_")])
    animals_graph.add((family_uri, RDF.type, animals_ontology.Family))
    animals_graph.add((family_uri, animals_ontology.belongsTo, order_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, family_uri))

    #Genus
    genus_uri = URIRef(animals_ontology[taxonomy['genus'].replace(" ", "_")])
    animals_graph.add((genus_uri, RDF.type, animals_ontology.Family))
    animals_graph.add((genus_uri, animals_ontology.belongsTo, family_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, genus_uri))

    #Scientific_name
    scientific_name_uri = URIRef(animals_ontology[taxonomy['scientific_name'].replace(" ", "_")])
    animals_graph.add((scientific_name_uri, RDF.type, animals_ontology.Scientific_name))
    animals_graph.add((scientific_name_uri, animals_ontology.belongsTo, genus_uri))
    animals_graph.add((animal_uri, animals_ontology.hasTaxonomy, scientific_name_uri))


    locations = json['locations']
    for location in locations:
        location_uri = URIRef(animals_ontology[location])
        animals_graph.add((location_uri, RDF.type, animals_ontology.Location))
        animals_graph.add((animal_uri, animals_ontology.livesIn, location_uri))

    characteristics = json['characteristics']
    characteristic_uri = URIRef(animals_ontology[json['name'].replace(" ", "_") + "_characteristics"])
    animals_graph.add((characteristic_uri, RDF.type, animals_ontology.Characteristics))


    for key, value in characteristics.items():
        # delete special characters from key using regex
        key = re.sub(r'[^\w\s]', '', key)
        prop_uri = URIRef(animals_ontology[key])

        animals_graph.add((characteristic_uri, prop_uri, Literal(value)))

    animals_graph.add((animal_uri, animals_ontology.hasCharacteristics, characteristic_uri))

#names is list of 20 basic animals
names = ['cheetah', 'lion', 'tiger', 'elephant',
         #'giraffe', 'zebra', 'rhinoceros', 'hippopotamus', 'crocodile', 'alligator', 'penguin', 'koala', 'kangaroo', 'panda', 'koala', 'kangaroo', 'panda', 'monkey', 'gorilla', 'chimpanzee'
         ]
for name in names:
    try:
        json = get_json_from_name(name)
        print(json[0])
        populate_ontology(json[0])
    except Exception as e:
        print(e)
        print("Error while populating ontology for", name)
animals_graph.serialize(NEW_ONTOLOGY_FILE_PATH, format="xml")
