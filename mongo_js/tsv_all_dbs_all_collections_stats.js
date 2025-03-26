function getDatabaseReportTSV() {
    let report = [];

    // Header row for TSV
    report.push("Database\tCollection\tStorage Size (MB)\tDocuments\tAvg Document Size (kB)\tIndexes\tTotal Index Size (MB)\tIndex Names");

    let dbList = db.adminCommand({listDatabases: 1}).databases;

    dbList.forEach(database => {
        let dbName = database.name;
        let dbConn = db.getSiblingDB(dbName);
        let collections = dbConn.getCollectionInfos(); // Get collection details

        collections.forEach(coll => {
            if (coll.type !== "collection") {
                print(`Skipping view: ${dbName}.${coll.name}`); // Inform about skipped views
                return;
            }

            let stats = dbConn.runCommand({collStats: coll.name});

            let storageSize = (stats.storageSize / (1024 * 1024)).toFixed(2);
            let docCount = stats.count;
            let avgDocSize = stats.avgObjSize ? (stats.avgObjSize / 1024).toFixed(2) : "N/A";
            let indexCount = stats.nindexes;
            let totalIndexSize = (stats.totalIndexSize / (1024 * 1024)).toFixed(2);
            let indexNames = Object.keys(stats.indexSizes || {}).join(", ");

            report.push(`${dbName}\t${coll.name}\t${storageSize}\t${docCount}\t${avgDocSize}\t${indexCount}\t${totalIndexSize}\t${indexNames}`);
        });
    });

    return report.join("\n");
}

// Run the function and print the TSV output
let tsvOutput = getDatabaseReportTSV();
print(tsvOutput);
