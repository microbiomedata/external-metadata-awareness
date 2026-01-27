// NCBI

db.biosamples.aggregate([
    {
        $project: {
            _id: 0,
            access: 1,
            accession: 1,
            id: 1,
            last_update: 1,
            publication_date: 1,
            submission_date: 1,
            package_content: {$ifNull: ["$Package.content", null]},
            status_status: {$ifNull: ["$Status.status", null]},
            status_when: {$ifNull: ["$Status.when", null]},
            is_reference: {$ifNull: ["$is_reference", null]},
            curation_date: {$ifNull: ["$Curation.curation_date", null]},
            curation_status: {$ifNull: ["$Curation.curation_status", null]},
            owner_abbreviation: {$ifNull: ["$Owner.Name.abbreviation", null]},
            owner_name: {$ifNull: ["$Owner.Name.content", null]},
            owner_url: {$ifNull: ["$Owner.Name.url", null]},
            description_title: {$ifNull: ["$Description.Title.content", null]},
            organism_name: {$ifNull: ["$Description.Organism.OrganismName.content", null]},
            taxonomy_id: {$ifNull: ["$Description.Organism.taxonomy_id", null]},
            taxonomy_name: {$ifNull: ["$Description.Organism.taxonomy_name", null]},
            description_comment: {
                $reduce: {
                    input: {
                        $cond: {
                            if: {$isArray: "$Description.Comment.Paragraph"},
                            then: {
                                $map: {
                                    input: "$Description.Comment.Paragraph",
                                    as: "p",
                                    in: "$$p.content"
                                }
                            },
                            else: {
                                $cond: {
                                    if: {$gt: ["$Description.Comment.Paragraph", null]},
                                    then: ["$Description.Comment.Paragraph.content"],
                                    else: []
                                }
                            }
                        }
                    },
                    initialValue: "",
                    in: {
                        $cond: {
                            if: {$eq: ["$$value", ""]},
                            then: "$$this",
                            else: {$concat: ["$$value", " ", "$$this"]}
                        }
                    }
                }
            },
            harmonized_pairs: {
                $map: {
                    input: {
                        $filter: {
                            input: {
                                $cond: {
                                    if: {$isArray: "$Attributes.Attribute"},
                                    then: "$Attributes.Attribute",
                                    else: {
                                        $cond: {
                                            if: {$gt: ["$Attributes.Attribute", null]},
                                            then: ["$Attributes.Attribute"],
                                            else: []
                                        }
                                    }
                                }
                            },
                            as: "attr",
                            cond: {
                                $and: [
                                    {$ne: ["$$attr.harmonized_name", null]},
                                    {$ne: ["$$attr.content", null]},
                                    {$eq: [{$type: "$$attr.harmonized_name"}, "string"]},
                                    {$eq: [{$type: "$$attr.content"}, "string"]}
                                ]
                            }
                        }
                    },
                    as: "validAttr",
                    in: {
                        k: "$$validAttr.harmonized_name",
                        v: "$$validAttr.content"
                    }
                }
            }
        }
    },
    {
        $replaceRoot: {
            newRoot: {
                $mergeObjects: [
                    "$$ROOT",
                    {$arrayToObject: "$harmonized_pairs"}
                ]
            }
        }
    },
    {
        $project: {
            harmonized_pairs: 0
        }
    },
    {
        $out: "biosamples_flattened"  // IMPORTANT: Creates collection used by measurement discovery pipeline
    }
])

// This script flattens the nested biosamples XML structure into a tabular format
// Input: biosamples collection (nested XML structure)
// Output: biosamples_flattened collection (tabular format with harmonized attributes as top-level fields)
