// Flatten NCBI packages collection directly in MongoDB
// Input: packages (nested NCBI package documents)
// Output: ncbi_packages_flattened (flat documents)

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting NCBI packages collection flattening`);

// Create beneficial indexes (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
try {
    db.packages.createIndex({Name: 1}, {background: true});
} catch(e) {
    print(`Packages Name index exists: ${e.message}`);
}

// Drop output collection
db.ncbi_packages_flattened.drop();

// Flatten packages using aggregation
print(`[${new Date().toISOString()}] Flattening packages collection...`);
db.packages.aggregate([
    {
        $project: {
            _id: 0,
            // Basic package info
            name: "$Name.content",
            display_name: "$DisplayName.content",
            short_name: "$ShortName.content",
            env_package: "$EnvPackage.content",
            env_package_display: "$EnvPackageDisplay.content",
            description: "$Description.content",
            example: "$Example.content",
            not_appropriate_for: "$NotAppropriateFor.content",
            
            // XML attributes (if any exist)
            group: "$group",
            antibiogram: "$antibiogram"
        }
    },
    {
        $out: "ncbi_packages_flattened"
    }
], { allowDiskUse: true });

const resultCount = db.ncbi_packages_flattened.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} flattened package records`);

// Create indexes on output collection
print(`[${new Date().toISOString()}] Creating indexes on flattened collection`);
try {
    db.ncbi_packages_flattened.createIndex({name: 1}, {background: true});
} catch(e) {
    print(`Flattened name index exists: ${e.message}`);
}
try {
    db.ncbi_packages_flattened.createIndex({env_package: 1}, {background: true});
} catch(e) {
    print(`Env_package index exists: ${e.message}`);
}
try {
    db.ncbi_packages_flattened.createIndex({display_name: 1}, {background: true});
} catch(e) {
    print(`Display_name index exists: ${e.message}`);
}

// Show sample results
print(`[${new Date().toISOString()}] Sample flattened packages:`);
db.ncbi_packages_flattened.find().limit(3).forEach(pkg => {
    print(`  ${pkg.name}: ${pkg.display_name} (env: ${pkg.env_package || 'none'})`);
});

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);