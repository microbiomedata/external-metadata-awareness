#!/usr/bin/env python3
"""
Test quantulum3 parsing on our sampled field values to validate measurement vs non-measurement classification.
"""

from quantulum3 import parser
import json

def test_quantulum_parsing():
    """Test quantulum3 on our checkpoint samples."""
    
    # Load our checkpoint data
    with open('local/measurement_field_assessment_checkpoint1.json', 'r') as f:
        checkpoint = json.load(f)
    
    results = {}
    
    # Test each field category
    for category, fields in checkpoint['field_assessments'].items():
        results[category] = {}
        
        for field_name, field_data in fields.items():
            sample_values = field_data['sample_values']
            parsed_results = []
            
            print(f"\n=== Testing {field_name} ({category}) ===")
            
            for value in sample_values[:5]:  # Test first 5 values
                if value and value not in ['not collected', 'not determined', 'not provided']:
                    try:
                        quantities = parser.parse(str(value))
                        if quantities:
                            parsed = [(q.value, str(q.unit)) for q in quantities]
                            parsed_results.append({
                                'original': value,
                                'parsed': parsed,
                                'success': True
                            })
                            print(f"  ✅ '{value}' → {parsed}")
                        else:
                            parsed_results.append({
                                'original': value,
                                'parsed': None,
                                'success': False
                            })
                            print(f"  ❌ '{value}' → no quantities detected")
                    except Exception as e:
                        parsed_results.append({
                            'original': value,
                            'error': str(e),
                            'success': False
                        })
                        print(f"  ⚠️  '{value}' → error: {e}")
            
            # Calculate success rate
            successful_parses = sum(1 for r in parsed_results if r.get('success', False))
            success_rate = successful_parses / len(parsed_results) if parsed_results else 0
            
            results[category][field_name] = {
                'parsed_results': parsed_results,
                'success_rate': success_rate,
                'assessment_confirmed': None  # We'll fill this in
            }
            
            print(f"  Success rate: {success_rate:.1%} ({successful_parses}/{len(parsed_results)})")
    
    # Save results
    with open('local/quantulum_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

if __name__ == '__main__':
    results = test_quantulum_parsing()
    
    print("\n" + "="*60)
    print("QUANTULUM3 VALIDATION SUMMARY")
    print("="*60)
    
    for category, fields in results.items():
        print(f"\n{category}:")
        for field_name, data in fields.items():
            success_rate = data['success_rate']
            print(f"  {field_name}: {success_rate:.1%} success rate")