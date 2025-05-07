// Aggregates biosamples by package_content and outputs to a new collection
db.biosamples_flattened.aggregate([
  { $match: { package_content: { $exists: true } } },
  {
    $group: {
      _id: "$package_content",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } },
  { $out: "biosamples_packages" }
], { allowDiskUse: true });

// Create an index on count for faster queries
db.biosample_packages.createIndex({ count: -1 });

// Print minimal stats
const totalPackages = db.biosample_packages.countDocuments();
print(`Created collection with ${totalPackages} unique biosample packages.`);