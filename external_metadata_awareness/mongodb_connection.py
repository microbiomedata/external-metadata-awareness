import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import pymongo


def parse_mongo_uri(uri: str) -> dict:
    """
    Parse a MongoDB URI into its component parts.
    
    Args:
        uri: A MongoDB connection URI (mongodb://host:port/)
        
    Returns:
        A dictionary containing the parsed components (host, port, etc.)
    """
    result = {"host": "localhost", "port": 27017}
    
    if not uri or not uri.startswith("mongodb://"):
        return result
    
    # Remove the mongodb:// prefix
    uri = uri.replace("mongodb://", "")
    
    # Split auth part from host:port part
    if '@' in uri:
        auth, host_port = uri.split('@', 1)
        if ':' in auth:
            result["username"], result["password"] = auth.split(':', 1)
    else:
        host_port = uri
    
    # Parse host and port
    if host_port.endswith('/'):
        host_port = host_port[:-1]
        
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        result["host"] = host
        try:
            result["port"] = int(port)
        except ValueError:
            pass  # Keep default port if parsing fails
    else:
        result["host"] = host_port
    
    return result


def get_mongo_client(
    mongo_uri: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: str = "localhost",
    port: int = 27017,
    direct_connection: bool = True,
    auth_mechanism: str = "SCRAM-SHA-256",
    auth_source: str = "admin",
    env_file: Optional[str] = None
) -> pymongo.MongoClient:
    """
    Establishes a connection to a MongoDB server with flexible configuration options.
    
    Args:
        mongo_uri: MongoDB connection URI string (overrides individual parameters if provided)
        username: Username for authentication (optional)
        password: Password for authentication (optional)
        host: Hostname of the MongoDB server (defaults to localhost)
        port: Port of the MongoDB server (defaults to 27017)
        direct_connection: Use a direct connection (defaults to True)
        auth_mechanism: Authentication mechanism (defaults to SCRAM-SHA-256)
        auth_source: Authentication source database (defaults to admin)
        env_file: Path to .env file to load credentials from (looks for NMDC_MONGO_USER and NMDC_MONGO_PASSWORD)
        
    Returns:
        A pymongo.MongoClient instance
    """
    # First try to load from .env file if provided
    if env_file and Path(env_file).exists():
        load_dotenv(env_file)
        env_username = os.getenv("NMDC_MONGO_USER")
        env_password = os.getenv("NMDC_MONGO_PASSWORD")
        if env_username and env_password:
            username = env_username
            password = env_password
    
    # If mongo_uri is provided, use it (with parsed values)
    if mongo_uri:
        parsed = parse_mongo_uri(mongo_uri)
        host = parsed.get("host", host)
        port = parsed.get("port", port)
        
        # Only use parsed auth if username/password not explicitly provided
        if not username and not password:
            username = parsed.get("username")
            password = parsed.get("password")
    
    # Build the connection
    if username and password:
        full_uri = f"mongodb://{username}:{password}@{host}:{port}/"
        client = pymongo.MongoClient(
            full_uri,
            directConnection=direct_connection,
            authMechanism=auth_mechanism,
            authSource=auth_source
        )
    else:
        client = pymongo.MongoClient(
            host,
            port,
            directConnection=direct_connection
        )
    
    return client