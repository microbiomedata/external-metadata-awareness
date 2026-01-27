// Generate detailed report of NMDC range slot_usage modifications
// Shows: slot name, global range, class with modification, resulting range

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting NMDC range slot_usage detailed report`);

const { execSync } = require('child_process');
const fs = require('fs');

const localSchemaFile = 'local/nmdc_materialized_patterns.yaml';
const tempSlotsFile = '/tmp/nmdc_global_slots.json';
const tempClassesFile = '/tmp/nmdc_classes.json';

try {
    // Check if local schema file exists
    if (!fs.existsSync(localSchemaFile)) {
        throw new Error(`NMDC schema file not found: ${localSchemaFile}. Run analyze-nmdc-slot-usage first.`);
    }
    
    print(`[${new Date().toISOString()}] Using local NMDC schema: ${localSchemaFile}`);
    
    // Extract global slots section
    print(`[${new Date().toISOString()}] Extracting global slots definitions...`);
    const extractSlotsCommand = `yq eval '.slots' "${localSchemaFile}" -o=json > "${tempSlotsFile}"`;
    execSync(extractSlotsCommand);
    
    // Extract classes section  
    print(`[${new Date().toISOString()}] Extracting classes definitions...`);
    const extractClassesCommand = `yq eval '.classes' "${localSchemaFile}" -o=json > "${tempClassesFile}"`;
    execSync(extractClassesCommand);
    
    // Read and parse both sections
    const globalSlotsJson = fs.readFileSync(tempSlotsFile, 'utf8');
    const globalSlots = JSON.parse(globalSlotsJson);
    
    const classesJson = fs.readFileSync(tempClassesFile, 'utf8');
    const classes = JSON.parse(classesJson);
    
    print(`[${new Date().toISOString()}] Analyzing range modifications...`);
    
    // Build comprehensive report
    const rangeModifications = [];
    
    Object.entries(classes).forEach(([className, classDef]) => {
        if (classDef.slot_usage) {
            Object.entries(classDef.slot_usage).forEach(([slotName, slotUsage]) => {
                if (slotUsage.range) {
                    // Look up global slot definition
                    const globalSlot = globalSlots[slotName];
                    const globalRange = globalSlot ? globalSlot.range : null;
                    
                    rangeModifications.push({
                        slot_name: slotName,
                        global_range: globalRange,
                        global_slot_uri: globalSlot ? globalSlot.slot_uri : null,
                        class_name: className,
                        slot_usage_range: slotUsage.range,
                        slot_usage_slot_uri: slotUsage.slot_uri || null,
                        is_override: globalRange !== null,
                        is_same_range: globalRange === slotUsage.range,
                        global_description: globalSlot ? globalSlot.description : null,
                        slot_usage_description: slotUsage.description || null,
                        other_slot_usage_properties: {
                            unit: slotUsage.unit || null,
                            minimum_value: slotUsage.minimum_value || null,
                            maximum_value: slotUsage.maximum_value || null,
                            required: slotUsage.required || null,
                            multivalued: slotUsage.multivalued || null
                        }
                    });
                }
            });
        }
    });
    
    // Drop and recreate report collection
    print(`[${new Date().toISOString()}] Storing detailed report in nmdc_range_slot_usage_report collection`);
    db.nmdc_range_slot_usage_report.drop();
    
    // Insert detailed report
    if (rangeModifications.length > 0) {
        const reportsWithMetadata = rangeModifications.map(report => ({
            ...report,
            schema_source: "NMDC",
            schema_file: localSchemaFile
        }));

        db.nmdc_range_slot_usage_report.insertMany(reportsWithMetadata);
    }
    
    // Create indexes for efficient querying
    try {
        db.nmdc_range_slot_usage_report.createIndex({slot_name: 1}, {background: true});
    } catch(e) {
        print(`Slot_name index exists: ${e.message}`);
    }
    try {
        db.nmdc_range_slot_usage_report.createIndex({class_name: 1}, {background: true});
    } catch(e) {
        print(`Class_name index exists: ${e.message}`);
    }
    try {
        db.nmdc_range_slot_usage_report.createIndex({is_override: 1}, {background: true});
    } catch(e) {
        print(`Is_override index exists: ${e.message}`);
    }
    try {
        db.nmdc_range_slot_usage_report.createIndex({is_same_range: 1}, {background: true});
    } catch(e) {
        print(`Is_same_range index exists: ${e.message}`);
    }
    
    // Generate summary statistics
    const totalModifications = rangeModifications.length;
    const overrides = rangeModifications.filter(r => r.is_override).length;
    const newRangeAssertions = rangeModifications.filter(r => !r.is_override).length;
    const sameRangeReassertions = rangeModifications.filter(r => r.is_same_range).length;
    const actualOverrides = rangeModifications.filter(r => r.is_override && !r.is_same_range).length;
    
    print(`\\n[${new Date().toISOString()}] DETAILED RANGE SLOT_USAGE REPORT:`);
    print(`=================================================================`);
    print(`Total range modifications: ${totalModifications}`);
    print(`Overrides of existing global ranges: ${overrides}`);
    print(`New range assertions (no global range): ${newRangeAssertions}`);
    print(`Same range re-assertions: ${sameRangeReassertions}`);
    print(`Actual range changes: ${actualOverrides}`);
    print(`=================================================================`);
    
    // Show all modifications in detail
    print(`\\n[${new Date().toISOString()}] COMPLETE RANGE MODIFICATIONS LIST:`);
    print(`Format: SLOT_NAME | Global Range → Class.slot_usage Range | [Status]`);
    print(`-----------------------------------------------------------------`);
    
    // Sort by slot name for easier reading
    rangeModifications.sort((a, b) => a.slot_name.localeCompare(b.slot_name));
    
    rangeModifications.forEach(mod => {
        const globalRangeDisplay = mod.global_range || 'NO_GLOBAL_RANGE';
        const status = mod.is_override ? 
            (mod.is_same_range ? '[REASSERT]' : '[OVERRIDE]') : 
            '[NEW]';
        
        print(`${mod.slot_name.padEnd(25)} | ${globalRangeDisplay.padEnd(20)} → ${mod.class_name}.${mod.slot_usage_range.padEnd(20)} | ${status}`);
    });
    
    // Show actual overrides (where range changes)
    const actualOverridesList = rangeModifications.filter(r => r.is_override && !r.is_same_range);
    if (actualOverridesList.length > 0) {
        print(`\\n[${new Date().toISOString()}] ACTUAL RANGE OVERRIDES (Global → Class-specific):`);
        print(`================================================================`);
        actualOverridesList.forEach(mod => {
            print(`${mod.slot_name}:`);
            print(`  Global range: ${mod.global_range}`);
            print(`  ${mod.class_name} range: ${mod.slot_usage_range}`);
            if (mod.global_description) {
                print(`  Global description: ${mod.global_description.substring(0, 80)}...`);
            }
            if (mod.slot_usage_description) {
                print(`  Class description: ${mod.slot_usage_description.substring(0, 80)}...`);
            }
            print(``);
        });
    }
    
    // Show new range assertions (slots without global ranges)
    const newAssertionsList = rangeModifications.filter(r => !r.is_override);
    if (newAssertionsList.length > 0) {
        print(`\\n[${new Date().toISOString()}] NEW RANGE ASSERTIONS (Class-only ranges):`);
        print(`=========================================================`);
        newAssertionsList.forEach(mod => {
            print(`${mod.slot_name} in ${mod.class_name}: ${mod.slot_usage_range}`);
        });
    }
    
    // Show slots by class
    print(`\\n[${new Date().toISOString()}] RANGE MODIFICATIONS BY CLASS:`);
    print(`============================================`);
    const byClass = {};
    rangeModifications.forEach(mod => {
        if (!byClass[mod.class_name]) byClass[mod.class_name] = [];
        byClass[mod.class_name].push(mod);
    });
    
    Object.entries(byClass)
        .sort(([a], [b]) => a.localeCompare(b))
        .forEach(([className, mods]) => {
            print(`${className} (${mods.length} range modifications):`);
            mods.forEach(mod => {
                const status = mod.is_override ? (mod.is_same_range ? 'reassert' : 'override') : 'new';
                print(`  ${mod.slot_name}: ${mod.slot_usage_range} [${status}]`);
            });
            print(``);
        });
    
    // Cleanup temporary files
    try {
        fs.unlinkSync(tempSlotsFile);
        fs.unlinkSync(tempClassesFile);
        print(`[${new Date().toISOString()}] Cleaned up temporary files`);
    } catch(e) {
        print(`Cleanup warning: ${e.message}`);
    }
    
    // Write TSV report file  
    const tsvFile = 'local/nmdc_range_slot_usage_report.tsv';
    print(`[${new Date().toISOString()}] Writing TSV report to ${tsvFile}...`);
    
    // Ensure local directory exists
    if (!fs.existsSync('local')) {
        fs.mkdirSync('local');
    }
    
    // Create TSV content
    const tsvHeader = 'slot_name\tglobal_range\tglobal_slot_uri\tclass_name\tslot_usage_range\tslot_usage_slot_uri\tstatus\tglobal_description\tslot_usage_description\n';
    let tsvContent = tsvHeader;
    
    rangeModifications.forEach(mod => {
        const status = mod.is_override ? 
            (mod.is_same_range ? 'REASSERT' : 'OVERRIDE') : 
            'NEW';
        
        const globalRange = mod.global_range || 'NO_GLOBAL_RANGE';
        const globalSlotUri = mod.global_slot_uri || '';
        const slotUsageSlotUri = mod.slot_usage_slot_uri || '';
        const globalDesc = (mod.global_description || '').replace(/\t/g, ' ').replace(/\n/g, ' ');
        const slotUsageDesc = (mod.slot_usage_description || '').replace(/\t/g, ' ').replace(/\n/g, ' ');
        
        tsvContent += `${mod.slot_name}\t${globalRange}\t${globalSlotUri}\t${mod.class_name}\t${mod.slot_usage_range}\t${slotUsageSlotUri}\t${status}\t${globalDesc}\t${slotUsageDesc}\n`;
    });
    
    fs.writeFileSync(tsvFile, tsvContent);
    print(`[${new Date().toISOString()}] TSV report written: ${tsvFile} (${rangeModifications.length} rows)`);
    
    print(`[${new Date().toISOString()}] Detailed report stored in nmdc_range_slot_usage_report collection`);

} catch (error) {
    print(`[${new Date().toISOString()}] Error: ${error.message}`);
    throw error;
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);