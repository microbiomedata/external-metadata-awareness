// Flatten BioProjects to minimal collection with key metadata fields
// Creates: bioprojects_flattened collection
// Uses the database from the current connection

print("Flattening bioprojects to bioprojects_flattened...");
print("Using database: " + db.getName());

// Drop target collection if it exists
db.bioprojects_flattened.drop();

// Execute aggregation pipeline
db.bioprojects.aggregate([
  {
    $project: {
      accession: "$ProjectID.ArchiveID.accession",
      archive: "$ProjectID.ArchiveID.archive",
      project_id: "$ProjectID.ArchiveID.id",
      name: "$ProjectDescr.Name",
      title: "$ProjectDescr.Title",
      description: "$ProjectDescr.Description",
      release_date: "$ProjectDescr.ProjectReleaseDate",
      organism_name: "$ProjectType.ProjectTypeSubmission.Target.Organism.OrganismName",
      organism_taxid: "$ProjectType.ProjectTypeSubmission.Target.Organism.taxID",
      organism_species: "$ProjectType.ProjectTypeSubmission.Target.Organism.species",
      organism_strain: "$ProjectType.ProjectTypeSubmission.Target.Organism.Strain",
      data_type: "$ProjectType.ProjectTypeSubmission.ProjectDataTypeSet.DataType",
      method_type: "$ProjectType.ProjectTypeSubmission.Method.method_type",
      sample_scope: "$ProjectType.ProjectTypeSubmission.Target.sample_scope",
      material: "$ProjectType.ProjectTypeSubmission.Target.material",
      capture: "$ProjectType.ProjectTypeSubmission.Target.capture"
    }
  },
  {
    $match: {
      accession: { $ne: null }
    }
  },
  {
    $out: "bioprojects_flattened"
  }
]);

// Report results
var count = db.bioprojects_flattened.countDocuments();
print("Created bioprojects_flattened with " + count + " documents");

// Show sample document
print("\nSample document:");
printjson(db.bioprojects_flattened.findOne());
