#!/usr/bin/env python3
"""
A simple mongosh wrapper that handles MongoDB authentication from .env files.

This script takes a MongoDB URI, a JavaScript file path, and optionally an .env file path.
It constructs a mongosh command with the proper credentials and executes it.
"""

import os
import sys
import subprocess
import click
from pymongo import uri_parser

from external_metadata_awareness.mongodb_connection import get_mongo_client


@click.command()
@click.option('--mongo-uri', required=True, help='MongoDB connection URI (must start with mongodb:// and include database name)')
@click.option('--js-file', required=True, help='Path to JavaScript file to execute')
@click.option('--env-file', help='Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)')
@click.option('--verbose', is_flag=True, help='Show verbose output')
def main(mongo_uri, js_file, env_file, verbose):
    """
    Execute a MongoDB JavaScript file using mongosh with proper authentication.
    
    This tool loads credentials from .env file if provided, constructs a 
    mongosh command with the credentials embedded in the URI, and executes it.
    """
    try:
        # Verify JS file exists
        if not os.path.exists(js_file):
            click.echo(f"Error: JavaScript file not found: {js_file}", err=True)
            sys.exit(1)
            
        if verbose:
            click.echo(f"Processing JavaScript file: {js_file}")
        
        # Get the final URI with credentials if env file is provided
        final_uri = mongo_uri
        if env_file:
            # Use get_mongo_client in dry run mode to get the URI with credentials
            result = get_mongo_client(
                mongo_uri=mongo_uri,
                env_file=env_file,
                debug=verbose,
                dry_run=True
            )
            final_uri = result.get('uri', mongo_uri)
            
        # Check if mongosh is available
        try:
            mongosh_version = subprocess.check_output(["mongosh", "--version"], text=True).strip()
            if verbose:
                click.echo(f"Found mongosh: {mongosh_version}")
        except (subprocess.SubprocessError, FileNotFoundError):
            click.echo("Error: mongosh not found. Please install mongosh to use this script.", err=True)
            sys.exit(1)
        
        # Construct the mongosh command
        mongosh_cmd = ["mongosh", final_uri, "--file", js_file]
        if verbose:
            # Don't print the full URI with credentials in verbose mode for security
            credentials_status = 'credentials' if '@' in final_uri else 'no credentials'
            click.echo(f"Executing: mongosh [URI with {credentials_status}] --file {js_file}")
        
        # Execute mongosh
        result = subprocess.run(mongosh_cmd, capture_output=True, text=True)
        
        # Display output
        if result.stdout:
            click.echo(result.stdout)
        
        # Check for errors
        if result.returncode != 0:
            if result.stderr:
                click.echo(f"Error: {result.stderr}", err=True)
            click.echo(f"mongosh exited with code {result.returncode}", err=True)
            sys.exit(result.returncode)
        else:
            click.echo("JavaScript executed successfully via mongosh")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()