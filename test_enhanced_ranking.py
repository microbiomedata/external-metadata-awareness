#!/usr/bin/env python3
"""
Test the enhanced measurement ranking framework on a subset of fields.
"""

import json
import sys
import os

# Add the package to the path
sys.path.insert(0, '/Users/MAM/Documents/gitrepos/external-metadata-awareness')

from external_metadata_awareness.prioritize_measurement_targets import EnhancedMeasurementRanker

def test_subset():
    """Test enhanced ranking on a small subset of known fields."""
    
    # Initialize ranker
    ranker = EnhancedMeasurementRanker('mongodb://localhost:27017/', 'ncbi_metadata')
    ranker.load_framework_config('local/enhanced_measurement_ranking_framework.json')
    
    # Test on a small subset of interesting fields
    test_fields = [
        'host_age', 'depth', 'estimated_size',  # Known good measurements
        'air_temp_regm', 'ph_meth', 'root_cond',  # Known false positives
        'lat_lon', 'env_broad_scale', 'sample_name'  # Known non-measurements
    ]
    
    print(f"Testing enhanced ranking on {len(test_fields)} representative fields...")
    
    # Phase 1: Apply exclusion patterns
    excluded_fields = {}
    for field_name in test_fields:
        exclusions = []
        if field_name.endswith('_regm'):
            exclusions.append('regimen_fields')
        if field_name.endswith('_meth'):
            exclusions.append('method_fields')
        if exclusions:
            excluded_fields[field_name] = exclusions
    
    print(f"Excluded {len(excluded_fields)} fields: {list(excluded_fields.keys())}")
    
    # Phase 2: Calculate variation metrics for non-excluded fields
    non_excluded_fields = [f for f in test_fields if f not in excluded_fields]
    print(f"Analyzing {len(non_excluded_fields)} non-excluded fields...")
    
    field_metrics = ranker.calculate_variation_metrics(non_excluded_fields, sample_size=100)
    
    # Phase 3: Validate top fields with quantulum3
    validation_results = ranker.validate_with_quantulum3(field_metrics, top_n=10)
    
    # Phase 4: Apply composite scoring
    results = []
    
    for field_name in test_fields:
        if field_name in excluded_fields:
            results.append({
                'field_name': field_name,
                'composite_score': 0.0,
                'status': 'excluded',
                'exclusion_reasons': excluded_fields[field_name],
                'evidence': 'pattern_exclusion'
            })
        else:
            metrics = field_metrics.get(field_name, {})
            validation = validation_results.get(field_name, {})
            
            variation_ratio = metrics.get('variation_ratio', 0.0)
            numeric_content_ratio = metrics.get('numeric_content_ratio', 0.0)
            quantulum3_success_rate = validation.get('quantulum3_success_rate', 0.0)
            
            composite_score = (
                variation_ratio * 0.4 +
                numeric_content_ratio * 0.3 +
                quantulum3_success_rate * 0.2 +
                0.0 * 0.1  # semantic similarity (skipped for test)
            )
            
            confidence_level = "low_confidence"
            if variation_ratio >= 0.8 and numeric_content_ratio >= 0.7:
                confidence_level = "high_confidence"
            elif variation_ratio >= 0.3 and numeric_content_ratio >= 0.4:
                confidence_level = "medium_confidence"
            
            results.append({
                'field_name': field_name,
                'composite_score': composite_score,
                'status': 'analyzed',
                'confidence_level': confidence_level,
                'variation_ratio': variation_ratio,
                'numeric_content_ratio': numeric_content_ratio,
                'quantulum3_success_rate': quantulum3_success_rate,
                'sample_values': metrics.get('sample_values', [])[:3]
            })
    
    # Sort by composite score
    results.sort(key=lambda x: x['composite_score'], reverse=True)
    
    print("\n=== ENHANCED MEASUREMENT RANKING RESULTS ===")
    for i, result in enumerate(results, 1):
        print(f"{i:2d}. {result['field_name']:<20} score: {result['composite_score']:.3f}")
        if result['status'] == 'excluded':
            print(f"    Status: EXCLUDED ({', '.join(result['exclusion_reasons'])})")
        else:
            print(f"    Confidence: {result['confidence_level']}")
            print(f"    Variation: {result['variation_ratio']:.3f}, Numeric: {result['numeric_content_ratio']:.3f}, Parsing: {result['quantulum3_success_rate']:.3f}")
            if result['sample_values']:
                print(f"    Samples: {result['sample_values']}")
        print()
    
    # Save test results
    with open('local/enhanced_ranking_test_results.json', 'w') as f:
        json.dump({
            'test_description': 'Enhanced measurement ranking on representative subset',
            'total_fields_tested': len(test_fields),
            'excluded_fields_count': len(excluded_fields),
            'results': results
        }, f, indent=2)
    
    print("✓ Test results saved to local/enhanced_ranking_test_results.json")
    
    # Summary
    high_confidence = sum(1 for r in results if r.get('confidence_level') == 'high_confidence')
    medium_confidence = sum(1 for r in results if r.get('confidence_level') == 'medium_confidence')
    excluded = sum(1 for r in results if r['status'] == 'excluded')
    
    print(f"\nSUMMARY: {high_confidence} high confidence, {medium_confidence} medium confidence, {excluded} excluded")

if __name__ == '__main__':
    test_subset()