// NCBI SRA

db.sra_metadata.aggregate([
  {
    $project: {
      _id: 1,
      biosample_accession: "$biosample",
      bioproject_accession: "$bioproject"
    }
  },
  {
    $out: "sra_biosamples_bioprojects"
  }
]);
