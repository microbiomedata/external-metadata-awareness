#!/usr/bin/env python3
"""
Combine multiple requests-cache SQLite files into a single consolidated cache file.
This script preserves the original cache files and creates a new one containing all entries.
"""

import sqlite3
import os
from pathlib import Path

# Define the source cache files and target combined cache
SOURCE_FILES = [
    'requests_cache.sqlite',
    'new_env_triad_values_splitter_cache.sqlite',
    'my_cache.sqlite',
    'notebooks/studies_exploration/ncbi_annotation_mining/requests_cache.sqlite'
]
COMBINED_CACHE = 'external-metadata-awareness-requests-cache.sqlite'


def create_empty_cache_db(output_path):
    """Create an empty cache database with the correct schema."""
    if Path(output_path).exists():
        print(f"Warning: {output_path} already exists. It will be overwritten.")
        os.remove(output_path)
    
    conn = sqlite3.connect(output_path)
    
    # Create responses table
    conn.execute("""
    CREATE TABLE responses (
        key TEXT PRIMARY KEY,
        value BLOB, 
        expires INTEGER
    )
    """)
    conn.execute("CREATE INDEX expires_idx ON responses(expires)")
    
    # Create redirects table
    conn.execute("""
    CREATE TABLE redirects (
        key TEXT PRIMARY KEY,
        value BLOB, 
        expires INTEGER
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Created empty cache database at {output_path}")


def merge_caches(source_files, target_file):
    """Merge multiple cache files into a single target file."""
    # Create the target cache file
    create_empty_cache_db(target_file)
    
    # Connect to the target database
    target_conn = sqlite3.connect(target_file)
    target_cur = target_conn.cursor()
    
    # Process each source file
    for source_file in source_files:
        if not Path(source_file).exists():
            print(f"Warning: Source file {source_file} does not exist. Skipping.")
            continue
        
        print(f"Processing {source_file}...")
        try:
            source_conn = sqlite3.connect(source_file)
            source_cur = source_conn.cursor()
            
            # Process each table
            for table in ['responses', 'redirects']:
                # Get column names
                source_cur.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in source_cur.fetchall()]
                
                # Count records before importing
                target_cur.execute(f"SELECT COUNT(*) FROM {table}")
                before_count = target_cur.fetchone()[0]
                
                # Import data with INSERT OR IGNORE to handle duplicates
                source_cur.execute(f"SELECT * FROM {table}")
                rows = source_cur.fetchall()
                
                if rows:
                    placeholders = ','.join(['?'] * len(rows[0]))
                    target_cur.executemany(
                        f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})", 
                        rows
                    )
                
                # Count records after importing
                target_conn.commit()
                target_cur.execute(f"SELECT COUNT(*) FROM {table}")
                after_count = target_cur.fetchone()[0]
                
                print(f"  - Added {after_count - before_count} entries to {table} table from {source_file}")
            
            source_conn.close()
            
        except Exception as e:
            print(f"Error processing {source_file}: {str(e)}")
    
    # Commit changes and close target connection
    target_conn.commit()
    
    # Get final stats
    target_cur.execute("SELECT COUNT(*) FROM responses")
    responses_count = target_cur.fetchone()[0]
    target_cur.execute("SELECT COUNT(*) FROM redirects")
    redirects_count = target_cur.fetchone()[0]
    
    target_conn.close()
    
    print("\nMerge completed:")
    print(f"Total responses in combined cache: {responses_count}")
    print(f"Total redirects in combined cache: {redirects_count}")


if __name__ == "__main__":
    print("Starting cache merge operation...")
    merge_caches(SOURCE_FILES, COMBINED_CACHE)
    print(f"\nSuccessfully created combined cache at: {COMBINED_CACHE}")
    print("NOTE: This is a new file that doesn't affect the existing cache files.")
    print("To use it, you'll need to update your application code to point to this file.")