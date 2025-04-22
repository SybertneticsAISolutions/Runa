"""
Neo4j connector for Runa knowledge graph integration.

This module provides Neo4j-specific implementation of the knowledge graph
connector, allowing Runa code to interact with Neo4j graph databases.
"""

import json
from typing import Dict, List, Any, Optional, Union, Tuple
from neo4j import GraphDatabase, Driver, Session
from ..knowledge import KnowledgeEntity, KnowledgeTriple, KnowledgeGraphConnector


class Neo4jConnector(KnowledgeGraphConnector):
    """Neo4j-specific implementation of the knowledge graph connector."""
    
    def __init__(self, uri: str = None, database: str = "neo4j"):
        """
        Initialize the Neo4j connector.
        
        Args:
            uri: URI of the Neo4j database (e.g., "bolt://localhost:7687")
            database: Name of the Neo4j database to use
        """
        super().__init__(graph_uri=uri)
        self.database = database
        self.driver: Optional[Driver] = None
    
    def connect(self, api_key: str = None, username: str = "neo4j", password: str = None) -> bool:
        """
        Connect to the Neo4j database.
        
        Args:
            api_key: Not used for Neo4j (maintained for interface compatibility)
            username: Neo4j username
            password: Neo4j password
            
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            auth = (username, password) if password else None
            self.driver = GraphDatabase.driver(self.graph_uri, auth=auth)
            
            # Test the connection
            with self.driver.session(database=self.database) as session:
                result = session.run("MATCH (n) RETURN count(n) AS count LIMIT 1")
                record = result.single()
                if record:
                    # Connection successful
                    self.api_client = {"connected": True, "driver": self.driver}
                    return True
            
            return False
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            return False
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            self.api_client = None
    
    def _get_session(self) -> Optional[Session]:
        """Get a Neo4j session if connected."""
        if not self.driver:
            print("Not connected to Neo4j database")
            return None
        
        return self.driver.session(database=self.database)
    
    def entity_to_cypher(self, entity: KnowledgeEntity) -> str:
        """
        Convert an entity to a Cypher query for creation.
        
        Args:
            entity: The knowledge entity to convert.
            
        Returns:
            Cypher query string.
        """
        # Escape properties for Cypher
        properties = {
            k: v if not isinstance(v, str) else v.replace("'", "\\'")
            for k, v in entity.properties.items()
        }
        
        # Add entity_id and entity_type properties
        properties["entity_id"] = entity.entity_id
        properties["type"] = entity.entity_type
        
        # Convert properties to Cypher format
        props_str = ", ".join([f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {json.dumps(v)}" 
                               for k, v in properties.items()])
        
        # Create a query with labels based on entity type
        query = f"MERGE (e:{entity.entity_type} {{entity_id: '{entity.entity_id}'}}) "
        query += f"ON CREATE SET e = {{{props_str}}} "
        query += f"ON MATCH SET e = {{{props_str}}} RETURN e"
        
        return query
    
    def triple_to_cypher(self, triple: KnowledgeTriple) -> str:
        """
        Convert a knowledge triple to a Cypher query for creation.
        
        Args:
            triple: The knowledge triple to convert.
            
        Returns:
            Cypher query string.
        """
        # Escape strings for Cypher
        subject_id = triple.subject_id.replace("'", "\\'")
        predicate = triple.predicate.replace("'", "\\'")
        object_id = triple.object_id.replace("'", "\\'")
        
        # Prepare relationship properties
        props = {"confidence": triple.confidence}
        props.update(triple.metadata)
        
        # Convert properties to Cypher format
        props_str = ", ".join([f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {json.dumps(v)}" 
                              for k, v in props.items()])
        
        # Create query that creates relationship between existing nodes
        query = f"MATCH (a {{entity_id: '{subject_id}'}}), (b {{entity_id: '{object_id}'}}) "
        query += f"MERGE (a)-[r:{predicate} {{{props_str}}}]->(b) "
        query += "RETURN r"
        
        return query
    
    def query_knowledge_graph(
        self, 
        query: Union[str, Dict[str, Any]], 
        query_type: str = "cypher"
    ) -> List[Dict[str, Any]]:
        """
        Query the Neo4j knowledge graph.
        
        Args:
            query: Cypher query string or structured query dict.
            query_type: Type of query (always "cypher" for Neo4j).
            
        Returns:
            List of result objects.
        """
        session = self._get_session()
        if not session:
            return []
        
        try:
            # Handle different query types
            if query_type == "cypher" and isinstance(query, str):
                # Direct Cypher query
                result = session.run(query)
                return [record.data() for record in result]
            
            elif isinstance(query, dict):
                # Structured query - convert to Cypher
                if "entity_id" in query:
                    # Entity lookup
                    entity_id = query["entity_id"]
                    cypher_query = f"MATCH (n {{entity_id: '{entity_id}'}}) RETURN n"
                    result = session.run(cypher_query)
                    return [{"id": entity_id, "found": bool(result.peek())}]
                
                elif "name_similar_to" in query:
                    # Semantic search (simplified implementation)
                    name = query["name_similar_to"]
                    entity_type = query.get("type", "")
                    
                    type_filter = f"AND n:{entity_type}" if entity_type else ""
                    cypher_query = f"""
                    MATCH (n) 
                    WHERE n.name =~ '(?i).*{name}.*' {type_filter}
                    RETURN n.entity_id AS id, n.name AS name, 
                           labels(n)[0] AS type, 0.8 AS match_score
                    LIMIT 5
                    """
                    
                    result = session.run(cypher_query)
                    return [record.data() for record in result]
                
                elif "subject" in query:
                    # Relationship search
                    subject_id = query["subject"]
                    cypher_query = f"""
                    MATCH (a {{entity_id: '{subject_id}'}})-[r]->(b)
                    RETURN a.entity_id AS subject, type(r) AS predicate, 
                           b.entity_id AS object, r.confidence AS confidence
                    """
                    
                    result = session.run(cypher_query)
                    return [record.data() for record in result]
            
            # Default empty response
            return []
            
        except Exception as e:
            print(f"Error querying Neo4j: {e}")
            return []
        finally:
            session.close()
    
    def store_entity(self, entity: KnowledgeEntity) -> bool:
        """
        Store a knowledge entity in Neo4j.
        
        Args:
            entity: The entity to store.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._get_session()
        if not session:
            return False
        
        try:
            query = self.entity_to_cypher(entity)
            result = session.run(query)
            
            # Store in local entities cache as well
            self.entities[entity.entity_id] = entity
            
            return bool(result.single())
        except Exception as e:
            print(f"Error storing entity in Neo4j: {e}")
            return False
        finally:
            session.close()
    
    def store_triple(self, triple: KnowledgeTriple) -> bool:
        """
        Store a knowledge triple in Neo4j.
        
        Args:
            triple: The triple to store.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._get_session()
        if not session:
            return False
        
        try:
            query = self.triple_to_cypher(triple)
            result = session.run(query)
            
            # Store in local triples cache as well
            self.triples.append(triple)
            
            return bool(result.single())
        except Exception as e:
            print(f"Error storing triple in Neo4j: {e}")
            return False
        finally:
            session.close()
    
    def import_knowledge(self, entities: List[KnowledgeEntity], triples: List[KnowledgeTriple]) -> bool:
        """
        Import knowledge entities and triples into Neo4j.
        
        Args:
            entities: List of entities to import.
            triples: List of triples to import.
            
        Returns:
            True if import is successful, False otherwise.
        """
        session = self._get_session()
        if not session:
            return False
        
        success = True
        
        try:
            # First import all entities
            for entity in entities:
                query = self.entity_to_cypher(entity)
                session.run(query)
                self.entities[entity.entity_id] = entity
            
            # Then import all relationships
            for triple in triples:
                query = self.triple_to_cypher(triple)
                session.run(query)
                self.triples.append(triple)
                
            return success
        except Exception as e:
            print(f"Error importing knowledge to Neo4j: {e}")
            return False
        finally:
            session.close()
    
    def export_knowledge(self) -> Tuple[List[KnowledgeEntity], List[KnowledgeTriple]]:
        """
        Export all knowledge from Neo4j.
        
        Returns:
            Tuple of (entities, triples) from the database.
        """
        session = self._get_session()
        if not session:
            return [], []
            
        entities = []
        triples = []
        
        try:
            # Export entities
            entity_query = "MATCH (n) RETURN n"
            entity_result = session.run(entity_query)
            
            for record in entity_result:
                node = record["n"]
                
                # Extract properties
                properties = dict(node)
                entity_id = properties.pop("entity_id", "unknown")
                entity_type = properties.pop("type", "concept")
                
                entity = KnowledgeEntity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    properties=properties,
                    source="neo4j"
                )
                
                entities.append(entity)
                self.entities[entity_id] = entity
            
            # Export relationships
            rel_query = "MATCH (a)-[r]->(b) RETURN a.entity_id AS subject, type(r) AS predicate, b.entity_id AS object, properties(r) AS props"
            rel_result = session.run(rel_query)
            
            for record in rel_result:
                subject_id = record["subject"]
                predicate = record["predicate"]
                object_id = record["object"]
                props = record["props"]
                
                confidence = props.pop("confidence", 1.0)
                
                triple = KnowledgeTriple(
                    subject_id=subject_id,
                    predicate=predicate,
                    object_id=object_id,
                    confidence=confidence,
                    metadata=props
                )
                
                triples.append(triple)
                self.triples.append(triple)
                
            return entities, triples
        except Exception as e:
            print(f"Error exporting knowledge from Neo4j: {e}")
            return [], []
        finally:
            session.close() 