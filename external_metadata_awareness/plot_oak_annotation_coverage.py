#!/usr/bin/env python3
"""
Script to plot the distribution of combined_oak_envo_coverage values
from the env_triad_component_labels collection for documents above a
configurable coverage threshold.
"""

import click
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", show_default=True,
              help="MongoDB connection URI.")
@click.option("--db-name", default="ncbi_metadata", show_default=True,
              help="Database holding the env_triad_component_labels collection.")
@click.option("--threshold", default=0.001, show_default=True, type=float,
              help="Minimum combined_oak_envo_coverage to include.")
def main(mongo_uri, db_name, threshold):
    """Plot the distribution of combined_oak_envo_coverage above a threshold."""
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db.env_triad_component_labels

    # Query for documents above the coverage threshold.
    cursor = collection.find(
        {"combined_oak_envo_coverage": {"$gt": threshold}},
        {"combined_oak_envo_coverage": 1, "_id": 0}
    )
    # Extract the coverage values.
    values = [doc["combined_oak_envo_coverage"] for doc in cursor if "combined_oak_envo_coverage" in doc]

    if not values:
        print(f"No documents found with combined_oak_envo_coverage > {threshold}")
        return

    # Create a histogram.
    plt.figure(figsize=(10, 6))
    plt.hist(values, bins=50, density=True, alpha=0.6, color="skyblue", edgecolor="black", label="Histogram")

    # Create a density plot using Gaussian KDE.
    density = gaussian_kde(values)
    xs = np.linspace(min(values), max(values), 200)
    plt.plot(xs, density(xs), "r-", label="Density")

    plt.xlabel("Combined ENVO Coverage")
    plt.ylabel("Density")
    plt.title(f"Distribution of combined_oak_envo_coverage (values > {threshold})")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
