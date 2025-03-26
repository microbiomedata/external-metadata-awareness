db.sra_metadata.aggregate([{
    $unwind: "$attributes"
}, {
    $group: {
        _id: "$attributes.k", count: {
            $sum: 1
        }
    }
}, {
    $match: {
        count: {
            $gte: 2
        }
    }
}, {
    $sort: {
        count: -1
    }
}, {
    $out: "sra_attributes_k_doc_counts_gt_1"
}])
