// Connect to MongoDB and list all indexes across databases
const dbs = db.adminCommand({listDatabases: 1}).databases;

for (const database of dbs) {
    const dbName = database.name;
    if (["admin", "local", "config"].includes(dbName)) {
        // Skip internal system databases if you want
        continue;
    }
    print(`\n=== Database: ${dbName} ===`);
    const currentDb = db.getSiblingDB(dbName);
    const collections = currentDb.getCollectionNames();

    for (const collName of collections) {
        print(`\n  --- Collection: ${collName} ---`);
        try {
            const indexes = currentDb.getCollection(collName).getIndexes();
            for (const index of indexes) {
                printjson(index);
            }
        } catch (error) {
            print(`    Error accessing indexes: ${error.message}`);
            print(`    This is likely due to permissions or special collection type`);
        }
    }
}