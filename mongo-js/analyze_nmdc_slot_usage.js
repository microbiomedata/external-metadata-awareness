// Analyze NMDC schema slot_usage statements with range assertions
// Downloads NMDC schema, saves locally, and analyzes slot_usage patterns

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting NMDC schema slot_usage analysis`);

const { execSync } = require('child_process');
const fs = require('fs');

// NMDC schema URL
const nmdcSchemaUrl = 'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml';
const localSchemaFile = 'local/nmdc_materialized_patterns.yaml';
const tempJsonFile = '/tmp/nmdc_analysis.json';

try {
    // Ensure local directory exists
    if (!fs.existsSync('local')) {
        fs.mkdirSync('local');
    }
    
    // Download NMDC schema and save locally
    print(`[${new Date().toISOString()}] Downloading NMDC schema from GitHub...`);
    execSync(`curl -s -L "${nmdcSchemaUrl}" -o "${localSchemaFile}"`);
    
    const fileSize = fs.statSync(localSchemaFile).size;
    print(`[${new Date().toISOString()}] Downloaded NMDC schema to ${localSchemaFile} (${Math.round(fileSize/1024/1024)}MB)`);
    
    // Extract classes section to analyze slot_usage
    print(`[${new Date().toISOString()}] Extracting classes section for slot_usage analysis...`);
    const extractClassesCommand = `yq eval '.classes' "${localSchemaFile}" -o=json > "${tempJsonFile}"`;
    execSync(extractClassesCommand);
    
    // Read and parse the classes JSON
    const classesJson = fs.readFileSync(tempJsonFile, 'utf8');
    const classesObject = JSON.parse(classesJson);
    
    // Analyze slot_usage statements
    print(`[${new Date().toISOString()}] Analyzing slot_usage statements...`);
    
    let totalClasses = 0;
    let classesWithSlotUsage = 0;
    let totalSlotUsageStatements = 0;
    let slotUsageWithRangeAssertions = 0;
    let slotUsageWithUnitAssertions = 0;
    let slotUsageWithMinMaxAssertions = 0;
    
    const classAnalysis = [];
    const rangeAssertionSlots = [];
    
    Object.entries(classesObject).forEach(([className, classDef]) => {
        totalClasses++;
        
        if (classDef.slot_usage) {
            classesWithSlotUsage++;
            const slotUsageEntries = Object.entries(classDef.slot_usage);
            totalSlotUsageStatements += slotUsageEntries.length;
            
            let classRangeAssertions = 0;
            let classUnitAssertions = 0;
            let classMinMaxAssertions = 0;
            
            slotUsageEntries.forEach(([slotName, slotUsage]) => {
                // Check for range assertions
                if (slotUsage.range) {
                    slotUsageWithRangeAssertions++;
                    classRangeAssertions++;
                    rangeAssertionSlots.push({
                        class_name: className,
                        slot_name: slotName,
                        range: slotUsage.range,
                        unit: slotUsage.unit || null,
                        minimum_value: slotUsage.minimum_value || null,
                        maximum_value: slotUsage.maximum_value || null,
                        description: slotUsage.description || null
                    });
                }
                
                // Check for unit assertions
                if (slotUsage.unit) {
                    slotUsageWithUnitAssertions++;
                    classUnitAssertions++;
                }
                
                // Check for min/max value assertions
                if (slotUsage.minimum_value !== undefined || slotUsage.maximum_value !== undefined) {
                    slotUsageWithMinMaxAssertions++;
                    classMinMaxAssertions++;
                }
            });
            
            classAnalysis.push({
                class_name: className,
                total_slot_usage: slotUsageEntries.length,
                range_assertions: classRangeAssertions,
                unit_assertions: classUnitAssertions,
                minmax_assertions: classMinMaxAssertions
            });
        }
    });
    
    // Drop and recreate analysis collection
    print(`[${new Date().toISOString()}] Storing analysis results in nmdc_slot_usage_analysis collection`);
    db.nmdc_slot_usage_analysis.drop();
    
    // Insert analysis results
    db.nmdc_slot_usage_analysis.insertOne({
        analysis_type: "nmdc_schema_overview",
        schema_url: nmdcSchemaUrl,
        analyzed_at: new Date(),
        summary: {
            total_classes: totalClasses,
            classes_with_slot_usage: classesWithSlotUsage,
            total_slot_usage_statements: totalSlotUsageStatements,
            slot_usage_with_range_assertions: slotUsageWithRangeAssertions,
            slot_usage_with_unit_assertions: slotUsageWithUnitAssertions,
            slot_usage_with_minmax_assertions: slotUsageWithMinMaxAssertions
        }
    });
    
    // Insert per-class analysis
    if (classAnalysis.length > 0) {
        db.nmdc_slot_usage_analysis.insertMany(
            classAnalysis.map(analysis => ({
                analysis_type: "class_slot_usage",
                analyzed_at: new Date(),
                ...analysis
            }))
        );
    }
    
    // Insert range assertion details
    if (rangeAssertionSlots.length > 0) {
        db.nmdc_slot_usage_analysis.insertMany(
            rangeAssertionSlots.map(slot => ({
                analysis_type: "range_assertion_slot",
                analyzed_at: new Date(),
                ...slot
            }))
        );
    }
    
    // Create indexes
    try {
        db.nmdc_slot_usage_analysis.createIndex({analysis_type: 1}, {background: true});
    } catch(e) {
        print(`Analysis_type index exists: ${e.message}`);
    }
    try {
        db.nmdc_slot_usage_analysis.createIndex({class_name: 1}, {background: true});
    } catch(e) {
        print(`Class_name index exists: ${e.message}`);
    }
    try {
        db.nmdc_slot_usage_analysis.createIndex({slot_name: 1}, {background: true});
    } catch(e) {
        print(`Slot_name index exists: ${e.message}`);
    }
    
    // Print summary
    print(`[${new Date().toISOString()}] NMDC Schema Analysis Summary:`);
    print(`  Total classes: ${totalClasses}`);
    print(`  Classes with slot_usage: ${classesWithSlotUsage}`);
    print(`  Total slot_usage statements: ${totalSlotUsageStatements}`);
    print(`  Slot_usage with range assertions: ${slotUsageWithRangeAssertions}`);
    print(`  Slot_usage with unit assertions: ${slotUsageWithUnitAssertions}`);
    print(`  Slot_usage with min/max assertions: ${slotUsageWithMinMaxAssertions}`);
    
    // Show classes sorted by slot_usage complexity
    print(`\\n[${new Date().toISOString()}] Top classes by slot_usage complexity:`);
    const topClasses = classAnalysis
        .sort((a, b) => (b.range_assertions + b.unit_assertions + b.minmax_assertions) - 
                       (a.range_assertions + a.unit_assertions + a.minmax_assertions))
        .slice(0, 10);
    
    topClasses.forEach(cls => {
        print(`  ${cls.class_name}: ${cls.total_slot_usage} slot_usage (${cls.range_assertions} range, ${cls.unit_assertions} unit, ${cls.minmax_assertions} min/max)`);
    });
    
    // Show Biosample class details if it exists
    const biosampleClass = classAnalysis.find(cls => cls.class_name === 'Biosample');
    if (biosampleClass) {
        print(`\\n[${new Date().toISOString()}] Biosample class slot_usage:`);
        print(`  Total slot_usage: ${biosampleClass.total_slot_usage}`);
        print(`  Range assertions: ${biosampleClass.range_assertions}`);
        print(`  Unit assertions: ${biosampleClass.unit_assertions}`);
        print(`  Min/max assertions: ${biosampleClass.minmax_assertions}`);
    }
    
    // Show some example range assertion slots
    if (rangeAssertionSlots.length > 0) {
        print(`\\n[${new Date().toISOString()}] Example slots with range assertions:`);
        rangeAssertionSlots.slice(0, 5).forEach(slot => {
            print(`  ${slot.class_name}.${slot.slot_name}: range=${slot.range}`);
            if (slot.unit) print(`    Unit: ${slot.unit}`);
            if (slot.minimum_value !== null || slot.maximum_value !== null) {
                print(`    Range: ${slot.minimum_value || 'N/A'} to ${slot.maximum_value || 'N/A'}`);
            }
        });
    }
    
    // Cleanup temporary file
    try {
        fs.unlinkSync(tempJsonFile);
        print(`[${new Date().toISOString()}] Cleaned up temporary files`);
    } catch(e) {
        print(`Cleanup warning: ${e.message}`);
    }
    
    print(`[${new Date().toISOString()}] Analysis results stored in nmdc_slot_usage_analysis collection`);
    print(`[${new Date().toISOString()}] NMDC schema saved locally as: ${localSchemaFile}`);

} catch (error) {
    print(`[${new Date().toISOString()}] Error: ${error.message}`);
    throw error;
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);