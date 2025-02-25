how was Myrold_Biosample_Metadata.csv created?

```js
db.collection.find({
  "Attributes.Attribute": {
    $elemMatch: {
      attribute_name: "emp500_principal_investigator",
      content: "Myrold"
    }
  }
})
```

and then flattening of attribute contents over attribute_names?

goes through column AY... 61 columns?

