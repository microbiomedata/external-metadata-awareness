#!/usr/bin/env python3
"""
Script to plot the distribution of combined_oak_envo_coverage values
from the env_triad_component_labels collection for documents with
combined_oak_envo_coverage > 0.001.
"""

from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


def main():
    # MongoDB connection configuration.
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client.ncbi_metadata
    collection = db.env_triad_component_labels

    # Query for documents with combined_oak_envo_coverage > 0.001.
    cursor = collection.find(
        {"combined_oak_envo_coverage": {"$gt": 0.001}},
        {"combined_oak_envo_coverage": 1, "_id": 0}
    )
    # Extract the coverage values.
    values = [doc["combined_oak_envo_coverage"] for doc in cursor if "combined_oak_envo_coverage" in doc]

    if not values:
        print("No documents found with combined_oak_envo_coverage > 0.001")
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
    plt.title("Distribution of combined_oak_envo_coverage (values > 0.001)")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
