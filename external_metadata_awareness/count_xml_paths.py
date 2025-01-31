from collections import Counter
from lxml import etree
import time
from datetime import datetime
import argparse
import json


def count_unique_xpaths(xml_file, status_interval=10):
    """Count unique XPaths in an XML file using iterparse, reporting status every N seconds."""
    try:
        xpath_counter = Counter()
        context = etree.iterparse(xml_file, events=('end',))

        last_status_time = time.time()

        for event, elem in context:
            current_time = time.time()
            if current_time - last_status_time >= status_interval:
                timestamp = datetime.utcnow().isoformat()
                most_common = xpath_counter.most_common(1)[0] if xpath_counter else ('None', 0)
                print(f"[{timestamp}] Processed paths: {len(xpath_counter)}")
                print(f"Most frequent: {most_common[0]} ({most_common[1]} occurrences)")
                project_path = '/PackageSet/Package/Project'
                print(f"Project count: {xpath_counter.get(project_path, 0)}")
                last_status_time = current_time

            path_parts = []
            current = elem
            while current is not None:
                path_parts.append(current.tag)
                current = current.getparent()

            xpath = '/' + '/'.join(reversed(path_parts))
            xpath_counter[xpath] += 1

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

        return sorted(xpath_counter.items(), key=lambda x: (-x[1], x[0]))
    except etree.XMLSyntaxError as e:
        print(f"XML parsing error: {e}")
        return []
    except Exception as e:
        print(f"Error processing file: {e}")
        return []


def print_xpath_counts(sorted_paths):
    """Print XPath counts in a formatted table."""
    if not sorted_paths:
        print("No XPaths found or error processing file")
        return

    print("\nXPath Count Summary:")
    print("-" * 80)
    print(f"{'XPath':<60} {'Count':>10}")
    print("-" * 80)

    for path, count in sorted_paths:
        print(f"{path:<60} {count:>10}")

    print("-" * 80)
    print(f"Total unique XPaths: {len(sorted_paths)}")


def save_results(sorted_paths, output_file):
    """Save results as JSON."""
    results = {
        "total_unique_paths": len(sorted_paths),
        "paths": dict(sorted_paths)
    }
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count unique XPaths in XML file')
    parser.add_argument('xml_file', help='Path to XML file')
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help='Status reporting interval in seconds (default: 10)')
    parser.add_argument('-o', '--output', default='xpath_counts.json',
                        help='Output JSON file (default: xpath_counts.json)')
    args = parser.parse_args()

    xpath_counts = count_unique_xpaths(args.xml_file, args.interval)
    print_xpath_counts(xpath_counts)
    save_results(xpath_counts, args.output)
