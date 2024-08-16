select accession,
       package,
       env_broad_scale,
       da.*
from attributes_plus ap
         join ncbi_package_definitions npd
              on
                  ap.package = npd."Name"
         join detected_annotations da
              on
                  ap.env_broad_scale = da.raw_text
where npd."EnvPackage" in ('soil', 'water');
