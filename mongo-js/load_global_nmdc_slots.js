// Load global NMDC slot definitions into MongoDB  
// Extracts slots from NMDC schema, loads to MongoDB without induction
// These are uninduced/global slot definitions without inheritance or slot_usage applied

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting global NMDC slot definitions loading`);

const { execSync } = require('child_process');
const fs = require('fs');

const localSchemaFile = 'local/nmdc_materialized_patterns.yaml';
const tempJsonFile = '/tmp/global_nmdc_slots.json';

try {
    // Check if local schema file exists
    if (!fs.existsSync(localSchemaFile)) {
        print(`[${new Date().toISOString()}] Local NMDC schema not found, downloading...`);
        const nmdcSchemaUrl = 'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml';
        
        // Ensure local directory exists
        if (!fs.existsSync('local')) {
            fs.mkdirSync('local');
        }
        
        execSync(`curl -s -L "${nmdcSchemaUrl}" -o "${localSchemaFile}"`);
        print(`[${new Date().toISOString()}] Downloaded NMDC schema to ${localSchemaFile}`);
    } else {
        print(`[${new Date().toISOString()}] Using existing NMDC schema: ${localSchemaFile}`);
    }
    
    // Extract global slots section to JSON
    print(`[${new Date().toISOString()}] Extracting global slots section to JSON...`);
    const extractSlotsCommand = `yq eval '.slots' "${localSchemaFile}" -o=json > "${tempJsonFile}"`;
    execSync(extractSlotsCommand);
    
    // Read and parse the slots JSON
    const slotsJson = fs.readFileSync(tempJsonFile, 'utf8');
    const slotsObject = JSON.parse(slotsJson);
    
    // Convert object to array (no filtering - all global slots)
    print(`[${new Date().toISOString()}] Converting to array format...`);
    const slots = Object.entries(slotsObject)
        .map(([key, value]) => ({
            slot_name: key,
            ...value
        }));
    
    print(`[${new Date().toISOString()}] Extracted ${slots.length} global NMDC slot definitions`);
    
    // Create beneficial indexes (error tolerant)
    print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
    try {
        db.global_nmdc_slots.createIndex({slot_name: 1}, {background: true});
    } catch(e) {
        print(`Slot_name index exists: ${e.message}`);
    }
    try {
        db.global_nmdc_slots.createIndex({domain: 1}, {background: true});
    } catch(e) {
        print(`Domain index exists: ${e.message}`);
    }
    try {
        db.global_nmdc_slots.createIndex({range: 1}, {background: true});
    } catch(e) {
        print(`Range index exists: ${e.message}`);
    }
    
    // Drop and recreate collection
    print(`[${new Date().toISOString()}] Dropping existing global_nmdc_slots collection`);
    db.global_nmdc_slots.drop();
    
    // Insert slot definitions
    print(`[${new Date().toISOString()}] Inserting ${slots.length} global slot definitions into global_nmdc_slots collection`);
    
    // Add metadata to each slot
    const slotsWithMetadata = slots.map(slot => ({
        ...slot,
        schema_source: "NMDC",
        schema_file: localSchemaFile,
        loaded_at: new Date(),
        schema_version: "main",  // Could extract actual version if needed
        induction_applied: false  // These are global/uninduced definitions
    }));
    
    const result = db.global_nmdc_slots.insertMany(slotsWithMetadata);
    print(`[${new Date().toISOString()}] Successfully inserted ${result.insertedIds.length} global slot definitions`);
    
    // Create additional indexes on output collection
    print(`[${new Date().toISOString()}] Creating additional indexes on global_nmdc_slots collection`);
    try {
        db.global_nmdc_slots.createIndex({unit: 1}, {background: true});
    } catch(e) {
        print(`Unit index exists: ${e.message}`);
    }
    try {
        db.global_nmdc_slots.createIndex({slot_uri: 1}, {background: true});
    } catch(e) {
        print(`Slot_uri index exists: ${e.message}`);
    }
    try {
        db.global_nmdc_slots.createIndex({"annotations.storage_units": 1}, {background: true});
    } catch(e) {
        print(`Storage_units annotation index exists: ${e.message}`);
    }
    try {
        db.global_nmdc_slots.createIndex({minimum_value: 1, maximum_value: 1}, {background: true});
    } catch(e) {
        print(`Range compound index exists: ${e.message}`);
    }
    
    // Cleanup temporary file
    try {
        fs.unlinkSync(tempJsonFile);
        print(`[${new Date().toISOString()}] Cleaned up temporary files`);
    } catch(e) {
        print(`Cleanup warning: ${e.message}`);
    }
    
    // Show summary statistics
    print(`[${new Date().toISOString()}] Collection summary:`);
    print(`  Total global slots: ${db.global_nmdc_slots.countDocuments()}`);
    print(`  Slots with units: ${db.global_nmdc_slots.countDocuments({unit: {$exists: true, $ne: null}})}`);
    print(`  Slots with ranges: ${db.global_nmdc_slots.countDocuments({range: {$exists: true, $ne: null}})}`);
    print(`  Slots with slot_uri: ${db.global_nmdc_slots.countDocuments({slot_uri: {$exists: true, $ne: null}})}`);
    print(`  Slots with annotations: ${db.global_nmdc_slots.countDocuments({annotations: {$exists: true}})}`);
    print(`  Slots with min/max values: ${db.global_nmdc_slots.countDocuments({$or: [{minimum_value: {$exists: true}}, {maximum_value: {$exists: true}}]})}`);
    
    // Show sample slots for verification
    print(`[${new Date().toISOString()}] Sample global slot definitions:`);
    db.global_nmdc_slots.find().limit(3).forEach(slot => {
        print(`  ${slot.slot_name}: ${slot.description || 'No description'}`);
        if (slot.unit) print(`    Unit: ${slot.unit}`);
        if (slot.range) print(`    Range: ${slot.range}`);
        if (slot.slot_uri) print(`    Slot URI: ${slot.slot_uri}`);
        if (slot.minimum_value !== undefined || slot.maximum_value !== undefined) {
            print(`    Value range: ${slot.minimum_value || 'N/A'} to ${slot.maximum_value || 'N/A'}`);
        }
    });

} catch (error) {
    print(`[${new Date().toISOString()}] Error: ${error.message}`);
    throw error;
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);