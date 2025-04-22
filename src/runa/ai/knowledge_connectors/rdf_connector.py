"""
RDF/OWL connector for Runa knowledge graph integration.

This module provides RDF/OWL-specific implementation of the knowledge graph
connector, allowing Runa code to interact with standard RDF triplestores.
"""

import os
from typing import Dict, List, Any, Optional, Union, Tuple
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from rdflib.namespace import NamespaceManager
from ..knowledge import KnowledgeEntity, KnowledgeTriple, KnowledgeGraphConnector


class RDFConnector(KnowledgeGraphConnector):
    """RDF/OWL-specific implementation of the knowledge graph connector."""
    
    def __init__(self, graph_uri: str = None):
        """
        Initialize the RDF connector.
        
        Args:
            graph_uri: URI of the RDF graph or file path to load from
        """
        super().__init__(graph_uri=graph_uri)
        self.graph = Graph()
        self.prefixes = {}
        self.initialize_namespaces()
    
    def initialize_namespaces(self):
        """Initialize standard namespaces."""
        # Standard namespaces
        self.prefixes = {
            'rdf': RDF,
            'rdfs': RDFS,
            'owl': OWL,
            'runa': Namespace("http://runa-lang.org/ontology#")
        }
        
        # Bind the namespaces to the graph
        for prefix, namespace in self.prefixes.items():
            self.graph.bind(prefix, namespace)
    
    def add_namespace(self, prefix: str, uri: str):
        """
        Add a custom namespace.
        
        Args:
            prefix: Namespace prefix
            uri: Namespace URI
        """
        namespace = Namespace(uri)
        self.prefixes[prefix] = namespace
        self.graph.bind(prefix, namespace)
    
    def connect(self, api_key: str = None) -> bool:
        """
        Connect to the RDF graph (or load from file).
        
        Args:
            api_key: Not used for RDF (maintained for interface compatibility)
            
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            if self.graph_uri:
                # Check if it's a file path or URI
                if os.path.exists(self.graph_uri):
                    # Load from file based on extension
                    format = None
                    if self.graph_uri.endswith(".ttl"):
                        format = "turtle"
                    elif self.graph_uri.endswith(".rdf") or self.graph_uri.endswith(".xml"):
                        format = "xml"
                    elif self.graph_uri.endswith(".n3"):
                        format = "n3"
                    elif self.graph_uri.endswith(".nt"):
                        format = "nt"
                    elif self.graph_uri.endswith(".jsonld"):
                        format = "json-ld"
                    
                    self.graph.parse(self.graph_uri, format=format)
                else:
                    # Treat as URI endpoint
                    self.graph.open(self.graph_uri)
            
            # Consider connection successful if we get here
            self.api_client = {"connected": True}
            return True
        except Exception as e:
            print(f"Error connecting to RDF graph: {e}")
            return False
    
    def close(self):
        """Close the RDF graph connection."""
        try:
            self.graph.close()
            self.api_client = None
        except:
            pass
    
    def uri_for_entity(self, entity_id: str) -> URIRef:
        """
        Convert an entity ID to a URIRef.
        
        Args:
            entity_id: Entity ID string (possibly with prefix).
            
        Returns:
            URIRef for the entity.
        """
        if ":" in entity_id:
            prefix, local_name = entity_id.split(":", 1)
            if prefix in self.prefixes:
                return self.prefixes[prefix][local_name]
        
        # Default: use Runa namespace
        return self.prefixes["runa"][entity_id]
    
    def entity_to_rdf(self, entity: KnowledgeEntity) -> None:
        """
        Add an entity to the RDF graph.
        
        Args:
            entity: The knowledge entity to add.
        """
        # Create URI for the entity
        entity_uri = self.uri_for_entity(entity.entity_id)
        
        # Add type triples
        type_uri = self.uri_for_entity(entity.entity_type)
        self.graph.add((entity_uri, RDF.type, type_uri))
        
        # Add other properties
        for key, value in entity.properties.items():
            pred_uri = self.prefixes["runa"][key]
            
            # Convert the value to the appropriate RDF form
            if isinstance(value, str):
                obj = Literal(value)
            elif isinstance(value, (int, float, bool)):
                obj = Literal(value)
            elif value is None:
                continue
            else:
                # For complex objects, convert to string
                obj = Literal(str(value))
            
            self.graph.add((entity_uri, pred_uri, obj))
    
    def triple_to_rdf(self, triple: KnowledgeTriple) -> None:
        """
        Add a triple to the RDF graph.
        
        Args:
            triple: The knowledge triple to add.
        """
        # Create URIs for subject, predicate, object
        subject_uri = self.uri_for_entity(triple.subject_id)
        predicate_uri = self.uri_for_entity(triple.predicate)
        object_uri = self.uri_for_entity(triple.object_id)
        
        # Add the main triple
        self.graph.add((subject_uri, predicate_uri, object_uri))
        
        # Add metadata as reified statements if needed
        if triple.confidence < 1.0 or triple.metadata:
            # Create a unique ID for this statement
            statement_id = f"{triple.subject_id}_{triple.predicate}_{triple.object_id}"
            statement_uri = self.prefixes["runa"][f"statement_{statement_id}"]
            
            # Reify the statement
            self.graph.add((statement_uri, RDF.type, RDF.Statement))
            self.graph.add((statement_uri, RDF.subject, subject_uri))
            self.graph.add((statement_uri, RDF.predicate, predicate_uri))
            self.graph.add((statement_uri, RDF.object, object_uri))
            
            # Add confidence as a property
            self.graph.add((statement_uri, self.prefixes["runa"]["confidence"], Literal(triple.confidence)))
            
            # Add other metadata
            for key, value in triple.metadata.items():
                pred_uri = self.prefixes["runa"][key]
                
                if isinstance(value, str):
                    obj = Literal(value)
                elif isinstance(value, (int, float, bool)):
                    obj = Literal(value)
                else:
                    obj = Literal(str(value))
                
                self.graph.add((statement_uri, pred_uri, obj))
    
    def query_knowledge_graph(
        self, 
        query: Union[str, Dict[str, Any]], 
        query_type: str = "sparql"
    ) -> List[Dict[str, Any]]:
        """
        Query the RDF knowledge graph.
        
        Args:
            query: SPARQL query string or structured query dict.
            query_type: Type of query ("sparql" or "structured").
            
        Returns:
            List of result objects.
        """
        try:
            # Direct SPARQL query
            if query_type == "sparql" and isinstance(query, str):
                results = self.graph.query(query)
                return [
                    {str(var): str(value) for var, value in zip(results.vars, row)}
                    for row in results
                ]
            
            # Structured query
            elif isinstance(query, dict):
                if "entity_id" in query:
                    # Entity lookup
                    entity_id = query["entity_id"]
                    entity_uri = self.uri_for_entity(entity_id)
                    
                    # Check if entity exists in the graph
                    exists = False
                    for s, p, o in self.graph.triples((entity_uri, None, None)):
                        exists = True
                        break
                    
                    return [{"id": entity_id, "found": exists}]
                
                elif "name_similar_to" in query:
                    # Simple regex-based name search
                    name = query["name_similar_to"]
                    entity_type = query.get("type", "")
                    
                    type_filter = f"""
                    ?entity rdf:type ?type .
                    FILTER(str(?type) = "{entity_type}")
                    """ if entity_type else ""
                    
                    sparql = f"""
                    SELECT ?entity ?name ?type
                    WHERE {{
                        ?entity runa:name ?name .
                        FILTER(REGEX(?name, "{name}", "i"))
                        {type_filter}
                        ?entity rdf:type ?type .
                    }}
                    LIMIT 5
                    """
                    
                    results = self.graph.query(sparql)
                    return [
                        {
                            "id": str(row.entity).split("#")[-1],
                            "name": str(row.name),
                            "type": str(row.type).split("#")[-1],
                            "match_score": 0.8
                        }
                        for row in results
                    ]
                
                elif "subject" in query:
                    # Find relationships for a subject
                    subject_id = query["subject"]
                    subject_uri = self.uri_for_entity(subject_id)
                    
                    results = []
                    for s, p, o in self.graph.triples((subject_uri, None, None)):
                        # Skip RDF metadata properties
                        if p in [RDF.type, RDFS.label, RDFS.comment]:
                            continue
                            
                        predicate = str(p).split("#")[-1]
                        object_id = str(o).split("#")[-1]
                        
                        # Look for confidence information
                        confidence = 1.0
                        
                        results.append({
                            "subject": subject_id,
                            "predicate": predicate,
                            "object": object_id,
                            "confidence": confidence
                        })
                    
                    return results
            
            # Default empty response
            return []
            
        except Exception as e:
            print(f"Error querying RDF graph: {e}")
            return []
    
    def store_entity(self, entity: KnowledgeEntity) -> bool:
        """
        Store a knowledge entity in the RDF graph.
        
        Args:
            entity: The entity to store.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.entity_to_rdf(entity)
            
            # Store in local entities cache as well
            self.entities[entity.entity_id] = entity
            
            return True
        except Exception as e:
            print(f"Error storing entity in RDF graph: {e}")
            return False
    
    def store_triple(self, triple: KnowledgeTriple) -> bool:
        """
        Store a knowledge triple in the RDF graph.
        
        Args:
            triple: The triple to store.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.triple_to_rdf(triple)
            
            # Store in local triples cache as well
            self.triples.append(triple)
            
            return True
        except Exception as e:
            print(f"Error storing triple in RDF graph: {e}")
            return False
    
    def import_knowledge(self, entities: List[KnowledgeEntity], triples: List[KnowledgeTriple]) -> bool:
        """
        Import knowledge entities and triples into the RDF graph.
        
        Args:
            entities: List of entities to import.
            triples: List of triples to import.
            
        Returns:
            True if import is successful, False otherwise.
        """
        try:
            # Import entities
            for entity in entities:
                self.entity_to_rdf(entity)
                self.entities[entity.entity_id] = entity
            
            # Import triples
            for triple in triples:
                self.triple_to_rdf(triple)
                self.triples.append(triple)
            
            return True
        except Exception as e:
            print(f"Error importing knowledge to RDF graph: {e}")
            return False
    
    def export_knowledge(self) -> Tuple[List[KnowledgeEntity], List[KnowledgeTriple]]:
        """
        Export all knowledge from the RDF graph.
        
        Returns:
            Tuple of (entities, triples) from the graph.
        """
        entities = []
        triples = []
        
        try:
            # Find all entities (subjects with a type)
            sparql = """
            SELECT DISTINCT ?entity ?type
            WHERE {
                ?entity rdf:type ?type .
            }
            """
            
            entity_results = self.graph.query(sparql)
            
            for row in entity_results:
                entity_uri = row.entity
                type_uri = row.type
                
                # Skip RDF/OWL built-in types
                if str(type_uri).startswith(str(RDF)) or str(type_uri).startswith(str(RDFS)) or str(type_uri).startswith(str(OWL)):
                    continue
                
                # Extract entity ID from URI
                entity_id = str(entity_uri).split("#")[-1]
                entity_type = str(type_uri).split("#")[-1]
                
                # Collect properties
                properties = {}
                for s, p, o in self.graph.triples((entity_uri, None, None)):
                    if p == RDF.type:
                        continue
                    
                    # Extract property name from URI
                    prop_name = str(p).split("#")[-1]
                    
                    # Convert literal to appropriate Python type
                    if isinstance(o, Literal):
                        value = o.toPython()
                    else:
                        value = str(o).split("#")[-1]
                    
                    properties[prop_name] = value
                
                # Create entity
                entity = KnowledgeEntity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    properties=properties,
                    source="rdf"
                )
                
                entities.append(entity)
                self.entities[entity_id] = entity
            
            # Find all non-metadata triples
            for s, p, o in self.graph:
                if p == RDF.type:
                    continue
                
                # Skip if subject or object are literal
                if isinstance(s, Literal) or isinstance(o, Literal):
                    continue
                
                # Skip RDF/RDFS/OWL built-in properties
                if str(p).startswith(str(RDF)) or str(p).startswith(str(RDFS)) or str(p).startswith(str(OWL)):
                    continue
                
                # Extract IDs from URIs
                subject_id = str(s).split("#")[-1]
                predicate = str(p).split("#")[-1]
                object_id = str(o).split("#")[-1]
                
                # Create triple
                triple = KnowledgeTriple(
                    subject_id=subject_id,
                    predicate=predicate,
                    object_id=object_id,
                    confidence=1.0,  # Default confidence
                    metadata={}
                )
                
                triples.append(triple)
                self.triples.append(triple)
            
            return entities, triples
        except Exception as e:
            print(f"Error exporting knowledge from RDF graph: {e}")
            return [], []
    
    def save_to_file(self, filename: str, format: str = "turtle") -> bool:
        """
        Save the RDF graph to a file.
        
        Args:
            filename: Path to the output file.
            format: RDF serialization format ("turtle", "xml", "n3", "nt", "json-ld").
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.graph.serialize(destination=filename, format=format)
            return True
        except Exception as e:
            print(f"Error saving RDF graph to file: {e}")
            return False
    
    def load_from_file(self, filename: str, format: str = None) -> bool:
        """
        Load RDF data from a file.
        
        Args:
            filename: Path to the input file.
            format: RDF serialization format (if None, will be inferred from file extension).
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Determine format from file extension if not specified
            if format is None:
                if filename.endswith(".ttl"):
                    format = "turtle"
                elif filename.endswith(".rdf") or filename.endswith(".xml"):
                    format = "xml"
                elif filename.endswith(".n3"):
                    format = "n3"
                elif filename.endswith(".nt"):
                    format = "nt"
                elif filename.endswith(".jsonld"):
                    format = "json-ld"
            
            self.graph.parse(filename, format=format)
            return True
        except Exception as e:
            print(f"Error loading RDF graph from file: {e}")
            return False 