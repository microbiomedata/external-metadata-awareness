// Load global MIxS slot definitions into MongoDB  
// Fetches MIxS schema YAML, extracts slots (excluding MixsCompliantData domain), loads to MongoDB
// These are uninduced/global slot definitions without inheritance or slot_usage applied

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting global MIxS slot definitions loading`);

const { execSync } = require('child_process');
const fs = require('fs');

// MIxS schema URL
const mixsSchemaUrl = 'https://raw.githubusercontent.com/GenomicsStandardsConsortium/mixs/refs/heads/main/src/mixs/schema/mixs.yaml';
const tempFile = '/tmp/mixs_schema.yaml';
const tempJsonFile = '/tmp/global_mixs_slots.json';

try {
    // Download MIxS schema
    print(`[${new Date().toISOString()}] Downloading MIxS schema from GitHub...`);
    execSync(`curl -s -L "${mixsSchemaUrl}" -o "${tempFile}"`);
    print(`[${new Date().toISOString()}] Downloaded MIxS schema to ${tempFile}`);
    
    // Step 1: Extract .slots section to JSON
    print(`[${new Date().toISOString()}] Extracting .slots section to JSON...`);
    const extractSlotsCommand = `yq eval '.slots' "${tempFile}" -o=json > "${tempJsonFile}"`;
    execSync(extractSlotsCommand);
    
    // Step 2: Read and parse the slots JSON
    const slotsJson = fs.readFileSync(tempJsonFile, 'utf8');
    const slotsObject = JSON.parse(slotsJson);
    
    // Step 3: Convert object to array and filter out MixsCompliantData domain
    print(`[${new Date().toISOString()}] Converting to array and filtering out MixsCompliantData domain...`);
    const slots = Object.entries(slotsObject)
        .filter(([key, value]) => value.domain !== "MixsCompliantData")
        .map(([key, value]) => ({
            slot_name: key,
            ...value
        }));
    
    print(`[${new Date().toISOString()}] Extracted ${slots.length} global slot definitions (excluding MixsCompliantData domain)`);
    
    // Create beneficial indexes (error tolerant)
    print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
    try {
        db.global_mixs_slots.createIndex({slot_name: 1}, {background: true});
    } catch(e) {
        print(`Slot_name index exists: ${e.message}`);
    }
    try {
        db.global_mixs_slots.createIndex({domain: 1}, {background: true});
    } catch(e) {
        print(`Domain index exists: ${e.message}`);
    }
    try {
        db.global_mixs_slots.createIndex({range: 1}, {background: true});
    } catch(e) {
        print(`Range index exists: ${e.message}`);
    }
    
    // Drop and recreate collection
    print(`[${new Date().toISOString()}] Dropping existing global_mixs_slots collection`);
    db.global_mixs_slots.drop();
    
    // Insert slot definitions
    print(`[${new Date().toISOString()}] Inserting ${slots.length} global slot definitions into global_mixs_slots collection`);
    
    // Add metadata to each slot
    const slotsWithMetadata = slots.map(slot => ({
        ...slot,
        schema_source: "MIxS",
        schema_url: mixsSchemaUrl,
        loaded_at: new Date(),
        schema_version: "main",  // Could extract actual version if needed
        induction_applied: false  // These are global/uninduced definitions
    }));
    
    const result = db.global_mixs_slots.insertMany(slotsWithMetadata);
    print(`[${new Date().toISOString()}] Successfully inserted ${result.insertedIds.length} global slot definitions`);
    
    // Create additional indexes on output collection
    print(`[${new Date().toISOString()}] Creating additional indexes on global_mixs_slots collection`);
    try {
        db.global_mixs_slots.createIndex({unit: 1}, {background: true});
    } catch(e) {
        print(`Unit index exists: ${e.message}`);
    }
    try {
        db.global_mixs_slots.createIndex({"annotations.storage_units": 1}, {background: true});
    } catch(e) {
        print(`Storage_units annotation index exists: ${e.message}`);
    }
    try {
        db.global_mixs_slots.createIndex({minimum_value: 1, maximum_value: 1}, {background: true});
    } catch(e) {
        print(`Range compound index exists: ${e.message}`);
    }
    
    // Cleanup temporary files
    try {
        fs.unlinkSync(tempFile);
        fs.unlinkSync(tempJsonFile);
        print(`[${new Date().toISOString()}] Cleaned up temporary files`);
    } catch(e) {
        print(`Cleanup warning: ${e.message}`);
    }
    
    // Show summary statistics
    print(`[${new Date().toISOString()}] Collection summary:`);
    print(`  Total global slots: ${db.global_mixs_slots.countDocuments()}`);
    print(`  Slots with units: ${db.global_mixs_slots.countDocuments({unit: {$exists: true, $ne: null}})}`);
    print(`  Slots with ranges: ${db.global_mixs_slots.countDocuments({$or: [{minimum_value: {$exists: true}}, {maximum_value: {$exists: true}}]})}`);
    print(`  Slots with annotations: ${db.global_mixs_slots.countDocuments({annotations: {$exists: true}})}`);
    
    // Show sample slots for verification
    print(`[${new Date().toISOString()}] Sample global slot definitions:`);
    db.global_mixs_slots.find().limit(3).forEach(slot => {
        print(`  ${slot.slot_name}: ${slot.description || 'No description'}`);
        if (slot.unit) print(`    Unit: ${slot.unit}`);
        if (slot.range) print(`    Range: ${slot.range}`);
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