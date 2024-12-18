Priority should be given to classes that were found in the GOLDTERMS mappings 
and/or are associated with a large number of NCBI studies.

Note that, as of 2024-12-11, the nmdc_scoped_count is Biosample based 
and the ncbi_scoped_count is BioProject (aka study) based.

In some cases it may be possible to distill our observations from the voting sheet into a more basic rule, 
like all terrestrial biomes for soil env_broad_scale

A single previously-agreed-upon enumeration is provided as a reference in most cases. For example, 
a new soil env_broad_scale voting sheet may use the EnvBroadScaleSoilEnum from submission-schema 10.7 as a reference.
10.7 is recommended because that was the last version before we started replacing the enumeration 
with the results of the new "voting process"

There's no legacy EnvBroadScaleSedimentEnum or EnvBroadScalePlantAssociatedEnum yet, 
so EnvBroadScaleSoilEnum is probably the best reference we have. 
If a newer schema, like 11.1 has a newer EnvBroadScaleSoilEnum, and we all trust it, 
then we could use that as the reference.

As of 2024-12-11, there probably isn't any useful reference enumeration for any water value set

The voting sheets will contain three columns related to the reference enumeration:
- is the class on any given row present in the reference enumeration?
- how many of that class' ancestors are present in the reference enumeration?
- how many of that class' descendants are present in the reference enumeration?

If the ancestor or descendant counts are high, then the class is too specific or too general, respectively.

# Filtering:
## all slots: obsolete = false
envo_native = true in most cases (but possibly not plant-associated?)

## env_broad_scale: biome = true
more specific subclasses of that are terrestrial_biome, aquatic_biome, etc.

## env_local_scale: abp = true
astronomical body part
more specific subclasses of that are human_construction, building, building_part, etc.
I assume that those will be used for exclusion, not inclusion
biome = false
env_mat = false

## env_medium: env_mat = true
environmental material
more specific subclasses of that are liquid_water, soil etc.

