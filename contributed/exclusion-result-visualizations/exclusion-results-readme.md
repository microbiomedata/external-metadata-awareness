The visualizations in this directory are created with commands like

```shell
poetry run runoak --input sqlite:obo:envo viz --down --predicates i 'planetary structural layer'
```

## Mark suggests adding these things back in, because they are amond the excluded classes:

- removed by 'transport feature'
    - bridge
    - road
- removed by 'protected area'
    - 'wildlife management area'
- removed by 'fluid layer'
    - .desc//p=i 'lake layer'
- .desc//p=i island

'interface layer' removes a few potentially useful terms especially for water samples like "lake surface", but even some
for soil too, like "forrest floor". No action yet.

## No visualizations for these large hierarchies yet

- biome (intended for `env_broad_scale`)
- environmental material (intended for `env_medium`)
- 'chemical entity'
- 'environmental system'

## May also want to remove everything whose label includes these?
- ice
- marine
- saline

**No visualizations of the classes lost by removing leaf classes yet**