import click
from collections import Counter
from lxml import etree
import time
from datetime import datetime
import json


def count_unique_xpaths(xml_file, status_interval, always_count_path, stop_after):
    """Count unique XPaths in an XML file using iterparse, reporting status every N seconds."""
    try:
        xpath_counter = Counter()
        context = etree.iterparse(xml_file, events=('end',))

        last_status_time = time.time()

        for event, elem in context:
            current_time = time.time()
            if current_time - last_status_time >= status_interval:
                timestamp = datetime.utcnow().isoformat()
                click.echo(
                    f"[{timestamp}] Processed paths: {len(xpath_counter)}; {always_count_path} count: {xpath_counter.get(always_count_path, 0)}")
                last_status_time = current_time

            path_parts = []
            current = elem
            while current is not None:
                path_parts.append(current.tag)
                current = current.getparent()

            base_xpath = '/' + '/'.join(reversed(path_parts))
            xpath_counter[base_xpath] += 1

            # Include attributes
            for attr in elem.attrib:
                attr_xpath = f"{base_xpath}@{attr}"
                xpath_counter[attr_xpath] += 1

            # Include text content if present
            if elem.text and elem.text.strip():
                text_xpath = f"{base_xpath}#text"
                xpath_counter[text_xpath] += 1

            if stop_after and xpath_counter[always_count_path] >= stop_after:
                click.echo(f"Stopping after {stop_after} occurrences of {always_count_path}")
                break

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

        return sorted(xpath_counter.items(), key=lambda x: (-x[1], x[0]))
    except etree.XMLSyntaxError as e:
        click.echo(f"XML parsing error: {e}", err=True)
        return []
    except Exception as e:
        click.echo(f"Error processing file: {e}", err=True)
        return []


def print_xpath_counts(sorted_paths):
    """Print XPath counts in a formatted table."""
    if not sorted_paths:
        click.echo("No XPaths found or error processing file", err=True)
        return

    click.echo("\nXPath Count Summary:")
    click.echo("-" * 80)
    click.echo(f"{'XPath':<60} {'Count':>10}")
    click.echo("-" * 80)

    for path, count in sorted_paths:
        click.echo(f"{path:<60} {count:>10}")

    click.echo("-" * 80)
    click.echo(f"Total unique XPaths: {len(sorted_paths)}")


def save_results(sorted_paths, output_file):
    """Save results as JSON."""
    results = {
        "total_unique_paths": len(sorted_paths),
        "paths": dict(sorted_paths)
    }
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


@click.command()
@click.option('--xml-file', required=True, type=click.Path(exists=True), help='Path to XML file')
@click.option('--interval', '-i', default=10, type=int, help='Status reporting interval in seconds (default: 10)')
@click.option('--output', '-o', default='xpath_counts.json', help='Output JSON file (default: xpath_counts.json)')
@click.option('--always-count-path', '-p', default='/PackageSet/Package/Project',
              help='XPath that will always be counted (default: /PackageSet/Package/Project)')
@click.option('--stop-after', '-s', default=None, type=int,
              help='Stop processing after N occurrences of always-count-path')
def main(xml_file, interval, output, always_count_path, stop_after):
    """Count unique XPaths in an XML file and save the results."""
    xpath_counts = count_unique_xpaths(xml_file, interval, always_count_path, stop_after)
    print_xpath_counts(xpath_counts)
    save_results(xpath_counts, output)


if __name__ == "__main__":
    main()
