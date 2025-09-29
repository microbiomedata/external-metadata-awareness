#!/usr/bin/env python3
"""
Enhanced measurement field ranking with multi-evidence substantiation.

This script implements the framework defined in enhanced_measurement_ranking_framework.json
to systematically rank all attributes by measurement-likeness using both deterministic
and language analysis evidence.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import click
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import quantulum3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EvidenceBreakdown:
    """Structure for tracking evidence used in scoring."""
    variation_ratio: Optional[float] = None
    numeric_content_ratio: Optional[float] = None
    quantulum3_success_rate: Optional[float] = None
    semantic_similarity: Optional[float] = None
    exclusion_patterns: List[str] = None
    confidence_level: str = "unknown"
    determination_method: str = "not_analyzed"
    
    def __post_init__(self):
        if self.exclusion_patterns is None:
            self.exclusion_patterns = []

@dataclass 
class RankingEntry:
    """Complete ranking entry with evidence substantiation."""
    field_name: str
    composite_score: float
    evidence_breakdown: EvidenceBreakdown
    sample_values_examined: List[str]
    validation_status: str
    exclusion_reasons: List[str] = None
    
    def __post_init__(self):
        if self.exclusion_reasons is None:
            self.exclusion_reasons = []

class EnhancedMeasurementRanker:
    """Implements the enhanced measurement ranking framework."""
    
    def __init__(self, mongo_uri: str, database_name: str):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.measurement_keywords = [
            "temp", "size", "depth", "age", "volume", "weight", "mass", 
            "length", "area", "height", "pressure", "concentration", 
            "temperature", "measurement", "value", "amount", "level",
            "rate", "speed", "duration", "distance", "density", "ph"
        ]
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.semantic_vectors = None
        self.attributes_df = None
        
    def load_framework_config(self, framework_path: str):
        """Load the enhanced ranking framework configuration."""
        with open(framework_path, 'r') as f:
            self.framework = json.load(f)
        logger.info(f"Loaded framework version {self.framework['framework_version']}")
        
    def load_attributes(self):
        """Load consolidated attribute data from MongoDB."""
        logger.info("Loading unified attribute rankings...")
        cursor = self.db.unified_measurement_attribute_rankings.find({}, {
            'name': 1, 'sources': 1, 'measurement_score': 1, 'total_samples': 1, 
            'descriptions': 1, 'unit_assertion_percentage': 1, 'mixed_content_percentage': 1
        })
        
        attributes = list(cursor)
        if not attributes:
            raise ValueError("No attributes found in unified_measurement_attribute_rankings collection")
            
        self.attributes_df = pd.DataFrame(attributes)
        logger.info(f"Loaded {len(self.attributes_df)} attributes")
        
        # Prepare semantic analysis using descriptions field
        descriptions = []
        for _, row in self.attributes_df.iterrows():
            desc_list = row.get('descriptions', [])
            if desc_list:
                # Join all descriptions for this attribute
                descriptions.append(' '.join(desc_list))
            else:
                descriptions.append('')
        
        if descriptions:
            self.semantic_vectors = self.vectorizer.fit_transform(descriptions)
            logger.info("Prepared semantic vectors for similarity analysis")
            
    def apply_exclusion_patterns(self) -> Dict[str, List[str]]:
        """Phase 1: Apply exclusion patterns to identify obvious non-measurements."""
        logger.info("Applying exclusion patterns...")
        
        exclusion_patterns = self.framework['evidence_categories']['DETERMINISTIC_EVIDENCE']['pattern_based_classification']['exclusion_patterns']
        
        excluded = {}
        for _, row in self.attributes_df.iterrows():
            field_name = row.get('name')
            if not field_name:
                continue
                
            exclusions = []
            
            # Check regimen fields
            if field_name.endswith('_regm'):
                exclusions.append('regimen_fields')
                
            # Check method fields  
            if field_name.endswith('_meth'):
                exclusions.append('method_fields')
                
            # Check protocol fields
            if field_name.endswith('_protocol'):
                exclusions.append('protocol_fields')
                
            if exclusions:
                excluded[field_name] = exclusions
                
        logger.info(f"Excluded {len(excluded)} fields based on patterns")
        return excluded
        
    def calculate_variation_metrics(self, field_names: List[str], sample_size: int = 1000) -> Dict[str, Dict]:
        """Phase 2: Calculate variation and numeric ratios for fields."""
        logger.info(f"Calculating variation metrics for {len(field_names)} fields...")
        
        metrics = {}
        for field_name in field_names:
            try:
                # Sample values from biosamples_flattened
                pipeline = [
                    {'$match': {field_name: {'$exists': True, '$ne': None}}},
                    {'$sample': {'size': sample_size}},
                    {'$project': {field_name: 1}}
                ]
                
                cursor = self.db.biosamples_flattened.aggregate(pipeline)
                values = [str(doc.get(field_name, '')) for doc in cursor if doc.get(field_name)]
                
                if not values:
                    metrics[field_name] = {
                        'variation_ratio': 0.0,
                        'numeric_content_ratio': 0.0,
                        'sample_size': 0,
                        'sample_values': []
                    }
                    continue
                    
                # Calculate variation ratio
                unique_values = set(values)
                variation_ratio = len(unique_values) / len(values) if values else 0.0
                
                # Calculate numeric content ratio
                numeric_count = 0
                for value in values:
                    if self._is_numeric_like(value):
                        numeric_count += 1
                        
                numeric_content_ratio = numeric_count / len(values) if values else 0.0
                
                metrics[field_name] = {
                    'variation_ratio': variation_ratio,
                    'numeric_content_ratio': numeric_content_ratio,
                    'sample_size': len(values),
                    'sample_values': list(unique_values)[:10]  # First 10 for inspection
                }
                
            except Exception as e:
                logger.warning(f"Error processing {field_name}: {e}")
                metrics[field_name] = {
                    'variation_ratio': 0.0,
                    'numeric_content_ratio': 0.0,
                    'sample_size': 0,
                    'sample_values': [],
                    'error': str(e)
                }
                
        return metrics
        
    def _is_numeric_like(self, value: str) -> bool:
        """Check if a value appears to contain numeric content."""
        # Remove common non-numeric characters and check if remainder is largely numeric
        cleaned = re.sub(r'[^\w\s\.]', '', str(value))
        if not cleaned:
            return False
            
        # Count numeric characters
        numeric_chars = sum(1 for c in cleaned if c.isdigit() or c == '.')
        total_chars = len(cleaned.replace(' ', ''))
        
        return (numeric_chars / total_chars) > 0.3 if total_chars > 0 else False
        
    def validate_with_quantulum3(self, field_metrics: Dict[str, Dict], top_n: int = 50) -> Dict[str, Dict]:
        """Phase 3: Validate high-scoring fields with quantulum3 sampling."""
        logger.info(f"Validating top {top_n} fields with quantulum3...")
        
        # Sort by composite heuristic (variation_ratio * 0.6 + numeric_content_ratio * 0.4)
        sorted_fields = sorted(
            field_metrics.items(),
            key=lambda x: x[1]['variation_ratio'] * 0.6 + x[1]['numeric_content_ratio'] * 0.4,
            reverse=True
        )[:top_n]
        
        validation_results = {}
        for field_name, metrics in sorted_fields:
            sample_values = metrics.get('sample_values', [])[:20]  # Test up to 20 values
            
            if not sample_values:
                validation_results[field_name] = {
                    'quantulum3_success_rate': 0.0,
                    'parsing_examples': [],
                    'validation_status': 'no_samples'
                }
                continue
                
            successful_parses = 0
            parsing_examples = []
            
            for value in sample_values:
                try:
                    quantities = quantulum3.parse(str(value))
                    if quantities:
                        successful_parses += 1
                        parsing_examples.append({
                            'input': str(value),
                            'parsed': [(q.value, q.unit.name) for q in quantities]
                        })
                        
                except Exception as e:
                    logger.debug(f"Quantulum3 error on {value}: {e}")
                    
            success_rate = successful_parses / len(sample_values) if sample_values else 0.0
            
            validation_results[field_name] = {
                'quantulum3_success_rate': success_rate,
                'parsing_examples': parsing_examples[:5],  # Top 5 examples
                'validation_status': 'completed'
            }
            
        return validation_results
        
    def calculate_semantic_similarity(self, field_name: str) -> float:
        """Calculate semantic similarity to measurement keywords."""
        if self.semantic_vectors is None:
            return 0.0
            
        try:
            field_idx = self.attributes_df[self.attributes_df['name'] == field_name].index[0]
            field_vector = self.semantic_vectors[field_idx]
            
            # Create measurement keywords vector
            keywords_text = ' '.join(self.measurement_keywords)
            keywords_vector = self.vectorizer.transform([keywords_text])
            
            similarity = cosine_similarity(field_vector, keywords_vector)[0][0]
            return float(similarity)
            
        except (IndexError, KeyError):
            return 0.0
            
    def apply_composite_scoring(self, excluded_fields: Dict, field_metrics: Dict, 
                              validation_results: Dict) -> List[RankingEntry]:
        """Phase 4: Apply composite scoring formula with evidence substantiation."""
        logger.info("Applying composite scoring formula...")
        
        rankings = []
        formula = self.framework['composite_scoring_formula']
        
        for _, row in self.attributes_df.iterrows():
            field_name = row.get('name')
            if not field_name:
                continue
                
            # Check for exclusions
            if field_name in excluded_fields:
                evidence = EvidenceBreakdown(
                    exclusion_patterns=excluded_fields[field_name],
                    confidence_level="excluded",
                    determination_method="pattern_exclusion"
                )
                
                ranking = RankingEntry(
                    field_name=field_name,
                    composite_score=0.0,
                    evidence_breakdown=evidence,
                    sample_values_examined=[],
                    validation_status="excluded_by_pattern",
                    exclusion_reasons=excluded_fields[field_name]
                )
                rankings.append(ranking)
                continue
                
            # Get metrics
            metrics = field_metrics.get(field_name, {})
            validation = validation_results.get(field_name, {})
            semantic_sim = self.calculate_semantic_similarity(field_name)
            
            # Calculate composite score using framework formula
            variation_ratio = metrics.get('variation_ratio', 0.0)
            numeric_content_ratio = metrics.get('numeric_content_ratio', 0.0)
            quantulum3_success_rate = validation.get('quantulum3_success_rate', 0.0)
            
            composite_score = (
                variation_ratio * 0.4 +
                numeric_content_ratio * 0.3 +
                quantulum3_success_rate * 0.2 +
                semantic_sim * 0.1
            )
            
            # Determine confidence level
            confidence_level = "low_confidence"
            if variation_ratio >= 0.8 and numeric_content_ratio >= 0.7:
                confidence_level = "high_confidence"
            elif variation_ratio >= 0.3 and numeric_content_ratio >= 0.4:
                confidence_level = "medium_confidence"
                
            evidence = EvidenceBreakdown(
                variation_ratio=variation_ratio,
                numeric_content_ratio=numeric_content_ratio,
                quantulum3_success_rate=quantulum3_success_rate,
                semantic_similarity=semantic_sim,
                confidence_level=confidence_level,
                determination_method="multi_evidence_analysis"
            )
            
            ranking = RankingEntry(
                field_name=field_name,
                composite_score=composite_score,
                evidence_breakdown=evidence,
                sample_values_examined=metrics.get('sample_values', [])[:5],
                validation_status=validation.get('validation_status', 'not_validated')
            )
            rankings.append(ranking)
            
        return rankings
        
    def generate_final_rankings(self, rankings: List[RankingEntry], output_path: str):
        """Phase 5: Generate ranked list with evidence provenance."""
        logger.info("Generating final rankings...")
        
        # Sort by composite score
        rankings.sort(key=lambda x: x.composite_score, reverse=True)
        
        # Convert to serializable format
        output_data = {
            'framework_version': self.framework['framework_version'],
            'generation_date': self.framework['generation_date'],
            'methodology': self.framework['methodology'],
            'total_attributes_analyzed': len(rankings),
            'rankings': []
        }
        
        for ranking in rankings:
            ranking_dict = asdict(ranking)
            ranking_dict['evidence_breakdown'] = asdict(ranking.evidence_breakdown)
            output_data['rankings'].append(ranking_dict)
            
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Saved {len(rankings)} rankings to {output_path}")
        
        # Print summary
        high_confidence = sum(1 for r in rankings if r.evidence_breakdown.confidence_level == "high_confidence")
        medium_confidence = sum(1 for r in rankings if r.evidence_breakdown.confidence_level == "medium_confidence")
        excluded = sum(1 for r in rankings if r.validation_status == "excluded_by_pattern")
        
        logger.info(f"Summary: {high_confidence} high confidence, {medium_confidence} medium confidence, {excluded} excluded")
        
        return rankings

@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/', help='MongoDB connection URI')
@click.option('--database', default='ncbi_metadata', help='MongoDB database name')
@click.option('--framework-config', default='local/enhanced_measurement_ranking_framework.json', 
              help='Path to framework configuration file')
@click.option('--output', default='local/enhanced_measurement_rankings.json', 
              help='Output path for rankings')
@click.option('--sample-size', default=1000, type=int, help='Sample size for variation analysis')
@click.option('--validate-top-n', default=100, type=int, help='Number of top fields to validate with quantulum3')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(mongo_uri: str, database: str, framework_config: str, output: str, 
         sample_size: int, validate_top_n: int, verbose: bool):
    """Generate enhanced measurement field rankings with multi-evidence substantiation."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        # Initialize ranker
        ranker = EnhancedMeasurementRanker(mongo_uri, database)
        ranker.load_framework_config(framework_config)
        ranker.load_attributes()
        
        # Phase 1: Apply exclusion patterns
        excluded_fields = ranker.apply_exclusion_patterns()
        
        # Phase 2: Calculate variation metrics for non-excluded fields
        non_excluded_fields = [
            row.get('name') for _, row in ranker.attributes_df.iterrows() 
            if row.get('name') and row.get('name') not in excluded_fields
        ]
        field_metrics = ranker.calculate_variation_metrics(non_excluded_fields, sample_size)
        
        # Phase 3: Validate with quantulum3
        validation_results = ranker.validate_with_quantulum3(field_metrics, validate_top_n)
        
        # Phase 4 & 5: Apply scoring and generate rankings
        rankings = ranker.apply_composite_scoring(excluded_fields, field_metrics, validation_results)
        final_rankings = ranker.generate_final_rankings(rankings, output)
        
        # Show top 10 and bottom 10
        print("\n=== TOP 10 MEASUREMENT CANDIDATES ===")
        for i, ranking in enumerate(final_rankings[:10], 1):
            print(f"{i:2d}. {ranking.field_name} (score: {ranking.composite_score:.3f}, confidence: {ranking.evidence_breakdown.confidence_level})")
            
        print("\n=== BOTTOM 10 (LOWEST SCORES) ===")
        for i, ranking in enumerate(final_rankings[-10:], len(final_rankings)-9):
            print(f"{i:2d}. {ranking.field_name} (score: {ranking.composite_score:.3f}, confidence: {ranking.evidence_breakdown.confidence_level})")
            
    except Exception as e:
        logger.error(f"Error in enhanced measurement ranking: {e}")
        raise

if __name__ == '__main__':
    main()