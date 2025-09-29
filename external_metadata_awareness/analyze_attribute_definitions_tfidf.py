#!/usr/bin/env python3
"""
Interactive semantic analysis of attribute definitions using TF-IDF embeddings.
Allows arbitrary queries to find measurement-like attributes without PyTorch dependencies.
"""

import click
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import json
import pickle
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import os


class AttributeSemanticAnalyzer:
    """Interactive semantic analyzer for metadata attributes."""
    
    def __init__(self, mongo_uri: str):
        self.mongo_uri = mongo_uri
        self.vectorizer = None
        self.attribute_vectors = None
        self.df = None
        self.fitted = False
    
    def extract_attribute_data(self) -> pd.DataFrame:
        """Extract all attribute text data from MongoDB collections."""
        client = pymongo.MongoClient(self.mongo_uri)
        db = client.get_database()
        
        # Get unified attribute data
        unified_attrs = list(db.unified_measurement_attribute_rankings.find({}))
        
        if not unified_attrs:
            raise ValueError("No unified attribute rankings found. Run rank-unified-measurement-attributes first.")
        
        rows = []
        for attr in unified_attrs:
            # Combine all text fields for semantic analysis
            text_parts = []
            
            # Name (most important - add multiple times for weight)
            name = attr.get('name', '')
            text_parts.extend([name] * 3)  # Triple weight for name
            
            # Descriptions from all sources
            descriptions = attr.get('descriptions', [])
            if descriptions:
                # Join descriptions, removing source prefixes
                clean_descriptions = [desc.split(':', 1)[-1].strip() if ':' in desc else desc 
                                    for desc in descriptions]
                text_parts.extend(clean_descriptions[:2])  # Limit to avoid redundancy
            
            # Format information (important for measurement detection)
            formats = attr.get('formats', [])
            if formats:
                clean_formats = [fmt.split(':', 1)[-1].strip() if ':' in fmt else fmt 
                               for fmt in formats]
                text_parts.extend(clean_formats)
            
            # Range information
            ranges = attr.get('ranges', [])
            if ranges:
                clean_ranges = [rng.split(':', 1)[-1].strip() if ':' in rng else rng 
                              for rng in ranges]
                text_parts.extend(clean_ranges)
            
            
            # Synonyms from NCBI
            if attr.get('synonyms'):
                synonyms = attr['synonyms'].split(';') if isinstance(attr['synonyms'], str) else []
                text_parts.extend([syn.strip() for syn in synonyms if syn.strip()])
            
            # Combine all text
            combined_text = ' '.join(filter(None, text_parts))
            
            rows.append({
                'name': attr['name'],
                'sources': '+'.join(attr.get('sources', [])),
                'text': combined_text,
                'current_score': attr.get('measurement_score', 0),
                'total_samples': attr.get('total_samples', 0),
                'unit_assertion_pct': attr.get('unit_assertion_percentage', 0),
                'mixed_content_pct': attr.get('mixed_content_percentage', 0),
                'source_count': len(attr.get('sources', [])),
                'formats': '|'.join(attr.get('formats', [])),
                'ranges': '|'.join(attr.get('ranges', []))
            })
        
        client.close()
        return pd.DataFrame(rows)
    
    def fit_embeddings(self) -> None:
        """Create TF-IDF embeddings for all attributes."""
        print("Extracting attribute data from MongoDB...")
        self.df = self.extract_attribute_data()
        print(f"Extracted {len(self.df)} attributes")
        
        print("Creating TF-IDF embeddings...")
        # Create TF-IDF vectorizer optimized for metadata analysis
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),  # Include trigrams for complex terms
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9_\.]*\b',  # Include underscores and dots
            min_df=1,  # Include rare terms (important for specific scientific terms)
            max_df=0.95  # Remove very common terms
        )
        
        # Fit on all attribute texts
        self.attribute_vectors = self.vectorizer.fit_transform(self.df['text'])
        self.fitted = True
        print(f"Created embeddings with {self.attribute_vectors.shape[1]} features")
    
    def find_similar(self, query: str, top_n: int = 20) -> pd.DataFrame:
        """Find attributes most similar to the given query."""
        if not self.fitted:
            raise ValueError("Must call fit_embeddings() first")
        
        # Transform query to vector space
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.attribute_vectors).flatten()
        
        # Add similarities to dataframe copy
        result_df = self.df.copy()
        result_df['similarity'] = similarities
        
        # Sort by similarity and return top results
        return result_df.sort_values('similarity', ascending=False).head(top_n)
    
    
    def analyze_measurement_potential(self) -> pd.DataFrame:
        """Analyze measurement potential using semantic features."""
        if not self.fitted:
            raise ValueError("Must call fit_embeddings() first")
        
        # Define measurement-related search queries
        measurement_queries = {
            'has_units': 'unit units measure measurement value quantity',
            'is_numeric': 'number numeric float integer count amount',
            'is_physical': 'temperature pressure density mass volume length area',
            'is_chemical': 'concentration ph conductivity salinity chemical',
            'is_temporal': 'time age duration date period interval',
            'is_biological': 'organism count cell bacteria abundance biomass'
        }
        
        result_df = self.df.copy()
        
        # Calculate similarity to each measurement category
        for category, query in measurement_queries.items():
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.attribute_vectors).flatten()
            result_df[f'{category}_sim'] = similarities
        
        # Calculate composite semantic measurement score
        weights = {
            'has_units': 0.3,
            'is_numeric': 0.2,
            'is_physical': 0.15,
            'is_chemical': 0.15,
            'is_temporal': 0.1,
            'is_biological': 0.1
        }
        
        result_df['semantic_score'] = sum(
            result_df[f'{cat}_sim'] * weight 
            for cat, weight in weights.items()
        )
        
        # Create enhanced hybrid score
        result_df['enhanced_score'] = (
            result_df['semantic_score'] * 40 +      # Semantic evidence (0-40 points)
            result_df['unit_assertion_pct'] * 30 +  # Unit assertions (0-30 points)  
            result_df['mixed_content_pct'] * 20 +   # Mixed content (0-20 points)
            result_df['source_count'] * 5 +         # Multi-source bonus (0-15 points)
            np.log10(result_df['total_samples'] + 1) * 2  # Volume bonus (0-~10 points)
        )
        
        return result_df.sort_values('enhanced_score', ascending=False)
    
    def save_model(self, filepath: str) -> None:
        """Save the fitted model for later use."""
        if not self.fitted:
            raise ValueError("Must call fit_embeddings() first")
        
        model_data = {
            'vectorizer': self.vectorizer,
            'attribute_vectors': self.attribute_vectors,
            'df': self.df,
            'fitted': self.fitted
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a previously saved model."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.attribute_vectors = model_data['attribute_vectors']
        self.df = model_data['df']
        self.fitted = model_data['fitted']
        print(f"Model loaded from {filepath}")


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata',
              help='MongoDB connection URI')
@click.option('--mode', type=click.Choice(['fit', 'query', 'analyze']), 
              default='analyze', help='Analysis mode')
@click.option('--query', '-q', help='Search query for similarity search')
@click.option('--top-n', default=20, help='Number of top results to show')
@click.option('--save-model', default='local/attribute_definitions_tfidf_model.pkl', help='Save model to file')
@click.option('--load-model', help='Load model from file')
@click.option('--output-file', default='local/attribute_definitions_tfidf_analysis.json', help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(mongo_uri: str, mode: str, query: Optional[str], top_n: int,
         save_model: str, load_model: Optional[str], output_file: str, verbose: bool):
    """TF-IDF semantic analysis of attribute definitions from NCBI/MIxS/NMDC schemas."""
    
    print(f"🔍 Semantic Metadata Attribute Analyzer")
    print(f"Mode: {mode}")
    
    # Initialize analyzer
    analyzer = AttributeSemanticAnalyzer(mongo_uri)
    
    # Load existing model or fit new one
    if load_model and os.path.exists(load_model):
        print(f"Loading existing model from {load_model}...")
        analyzer.load_model(load_model)
    else:
        print("Fitting new embeddings model...")
        analyzer.fit_embeddings()
        if save_model:
            analyzer.save_model(save_model)
    
    # Execute requested analysis
    if mode == 'query':
        if not query:
            query = click.prompt("Enter your search query")
        
        print(f"\n🔍 Finding attributes similar to: '{query}'")
        results = analyzer.find_similar(query, top_n)
        
        print(f"\nTop {top_n} similar attributes:")
        for i, (_, row) in enumerate(results.iterrows()):
            print(f"{i+1:2d}. {row['similarity']:.3f}: {row['name']:25} ({row['sources']:15}) "
                  f"[score: {row['current_score']:.1f}, samples: {row['total_samples']:,}]")
    
    elif mode == 'analyze':
        print(f"\n📊 Analyzing measurement potential of all attributes...")
        enhanced_df = analyzer.analyze_measurement_potential()
        
        print(f"\nTOP 15 MEASUREMENT CANDIDATES (Enhanced Scoring):")
        for i, (_, row) in enumerate(enhanced_df.head(15).iterrows()):
            print(f"{i+1:2d}. {row['enhanced_score']:5.1f}: {row['name']:25} ({row['sources']:15})")
            if verbose:
                print(f"     Semantic: {row['semantic_score']:.3f}, "
                      f"Units: {row['unit_assertion_pct']*100:.1f}%, "
                      f"Mixed: {row['mixed_content_pct']*100:.1f}%")
        
        # Save detailed results
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_attributes': len(enhanced_df),
            'methodology': 'TF-IDF semantic similarity + empirical evidence',
            'top_measurement_candidates': enhanced_df.head(50)[
                ['name', 'sources', 'enhanced_score', 'semantic_score', 
                 'current_score', 'total_samples']
            ].to_dict('records')
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
    
    print(f"\n✅ Analysis complete!")
    print(f"\nNext steps:")
    print(f"  - Use --mode query to search for specific terms")
    print(f"  - Focus on top-ranked attributes for value parsing")


if __name__ == '__main__':
    main()