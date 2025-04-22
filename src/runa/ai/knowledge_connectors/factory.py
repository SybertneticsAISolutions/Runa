"""
Knowledge graph connector factory for Runa.

This module provides a factory function to create the appropriate
knowledge graph connector based on the connection parameters.
"""

from typing import Dict, Any, Optional
from ..knowledge import KnowledgeGraphConnector
from .neo4j_connector import Neo4jConnector
from .rdf_connector import RDFConnector


def create_connector(
    connector_type: str,
    uri: Optional[str] = None,
    **kwargs
) -> KnowledgeGraphConnector:
    """
    Create a knowledge graph connector of the specified type.
    
    Args:
        connector_type: The type of connector to create ("neo4j", "rdf", etc.)
        uri: The URI of the knowledge graph
        **kwargs: Additional connector-specific parameters
        
    Returns:
        A knowledge graph connector instance.
        
    Raises:
        ValueError: If the connector type is not supported.
    """
    connector_type = connector_type.lower()
    
    if connector_type == "neo4j":
        database = kwargs.get("database", "neo4j")
        return Neo4jConnector(uri=uri, database=database)
    
    elif connector_type == "rdf" or connector_type == "owl":
        return RDFConnector(graph_uri=uri)
    
    else:
        raise ValueError(f"Unsupported connector type: {connector_type}")


def get_connector_for_uri(uri: str) -> KnowledgeGraphConnector:
    """
    Create a knowledge graph connector based on the URI format.
    
    Args:
        uri: The URI of the knowledge graph
        
    Returns:
        A knowledge graph connector instance.
    """
    if uri.startswith("bolt://") or uri.startswith("neo4j://"):
        return Neo4jConnector(uri=uri)
    
    elif (uri.endswith(".ttl") or uri.endswith(".rdf") or uri.endswith(".owl") or
          uri.endswith(".n3") or uri.endswith(".nt") or uri.endswith(".jsonld") or
          uri.startswith("http://") and any(ext in uri for ext in ["/sparql", "/rdf"])):
        return RDFConnector(graph_uri=uri)
    
    else:
        # Default to RDF for unknown formats
        return RDFConnector(graph_uri=uri) 