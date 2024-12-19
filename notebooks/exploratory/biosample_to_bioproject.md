The NCBI BioProject web page says that EMP500 has 1024 BioSamples

https://www.ncbi.nlm.nih.gov/bioproject/686344

But this sql doesn't find them in the duckdb BioSample links table

```sql
select
	*
from
	main.links l
where
	target = 'bioproject'
	and content = '686344' ;
```

This doesn't work either. See how I picked those identifiers below.

```sql
select
	*
from
	main.links l
where
	target = 'bioproject'
	and id = 17124288 ;
```

```xml
<DocumentSummary uid="686344">
    <Project>
        <ProjectID>
            <ArchiveID accession="PRJEB42019" archive="EBI" id="686344"/>
            <CenterID center="EBI" id="0">ERP125879</CenterID>
            <LocalID submission_id="qiita_sid_13114">University of California San Diego Microbiome Initiative</LocalID>
        </ProjectID>
        <ProjectDescr>
            <Title>Earth Microbiome Project Multi-omics (EMP500)</Title>
            <Description>The Earth Microbiome Project Multi-omics component (EMP500) involves amplicon and shotgun metagenomic sequencing and metabolomic profiling of over five hundred microbial communities from diverse environments on our planet. We developed new protocols for shotgun metagenomic sequencing and assembly, with the goal of applying this workflow to a range of environmental samples, combined with metabolomic profiling. 16S, 18S, and ITS amplicon sequencing was done in addition. We acquired a set of &gt;500 fresh environmental samples across a range of habitats, with the help of the EMP network of collaborators. A biobank of frozen aliquots for all samples is maintained at UCSD (soil samples stored at the Pacific Northwest National Laboratory) for future methods testing and analysis.</Description>
        </ProjectDescr>
        <ProjectType>
            <ProjectTypeSubmission>
                <Target capture="eWhole" material="eGenome" sample_scope="eMonoisolate"/>
                <Method method_type="eSequencing"/>
                <Objectives>
                    <Data data_type="eOther">Unspecified Objective</Data>
                </Objectives>
                <ProjectDataTypeSet>
                    <DataType>Other</DataType>
                </ProjectDataTypeSet>
            </ProjectTypeSubmission>
        </ProjectType>
    </Project>
    <Submission last_update="2020-12-18" submitted="2020-12-18">
        <Description>
            <!-- Submitter information has been removed -->
            <Organization role="owner" type="center">
                <Name>University of California San Diego Microbiome Initiative</Name>
                <!-- Contact information has been removed -->
            </Organization>
            <Access>public</Access>
        </Description>
    </Submission>
</DocumentSummary>
```

Example EMP500 BioSample:

```xml
<BioSampleSet>
	<BioSample access="public" publication_date="2020-12-17T00:00:00.000" last_update="2021-08-23T00:27:46.000" submission_date="2020-12-20T10:49:06.376" id="17124288" accession="SAMEA7724404">
		<Ids>
			<Id db="BioSample" is_primary="1">SAMEA7724404</Id>
			<Id db="SRA">ERS5471781</Id>
		</Ids>
		<Description>
			<Title>13114.makhalanyane.47.s005</Title>
			<Organism taxonomy_id="1671699" taxonomy_name="sand metagenome">
				<OrganismName>sand metagenome</OrganismName>
			</Organism>
			<Comment>
				<Paragraph>Dune sand from Namibia</Paragraph>
			</Comment>
		</Description>
		<Owner>
			<Name>EBI</Name>
		</Owner>
		<Models>
			<Model>Generic</Model>
		</Models>
		<Package display_name="Generic">Generic.1.0</Package>
		<Attributes>
			<Attribute attribute_name="ENA first public">2020-12-17</Attribute>
			<Attribute attribute_name="ENA last update">2020-12-16</Attribute>
			<Attribute attribute_name="ENA-CHECKLIST">ERC000011</Attribute>
			<Attribute attribute_name="External Id">SAMEA7724404</Attribute>
			<Attribute attribute_name="INSDC center alias">UCSDMI</Attribute>
			<Attribute attribute_name="INSDC center name">University of California San Diego Microbiome Initiative</Attribute>
			<Attribute attribute_name="INSDC first public">2020-12-17T04:08:05Z</Attribute>
			<Attribute attribute_name="INSDC last update">2020-12-16T03:49:13Z</Attribute>
			<Attribute attribute_name="INSDC status">public</Attribute>
			<Attribute attribute_name="Submitter Id">qiita_sid_13114:13114.makhalanyane.47.s005</Attribute>
			<Attribute attribute_name="alpha_shotgun_woltka_faithspd">1.9567655166611075</Attribute>
			<Attribute attribute_name="alpha_shotgun_woltka_richness">2.0</Attribute>
			<Attribute attribute_name="alpha_shotgun_woltka_shannon">0.9910760598382222</Attribute>
			<Attribute attribute_name="ammonium_mg_per_l">0.48</Attribute>
			<Attribute attribute_name="barcode_prefix">makhalanyane.47.s005</Attribute>
			<Attribute attribute_name="calcium_mg_per_l">0.75</Attribute>
			<Attribute attribute_name="chloride_mg_per_l">15.91</Attribute>
			<Attribute attribute_name="coarse_sand_percent">4.97</Attribute>
			<Attribute attribute_name="collection_timestamp">11/16/14 0:00</Attribute>
			<Attribute attribute_name="depth_sample">not provided</Attribute>
			<Attribute attribute_name="elevation" harmonized_name="elev" display_name="elevation">380</Attribute>
			<Attribute attribute_name="emp500_principal_investigator">Makhalanyane</Attribute>
			<Attribute attribute_name="emp500_study_id">47</Attribute>
			<Attribute attribute_name="emp500_title">Namibia dune aridity gradient soils</Attribute>
			<Attribute attribute_name="empo_0">EMP sample</Attribute>
			<Attribute attribute_name="empo_1">Free-living</Attribute>
			<Attribute attribute_name="empo_2">Non-saline</Attribute>
			<Attribute attribute_name="empo_3">Soil (non-saline)</Attribute>
			<Attribute attribute_name="env biome" harmonized_name="env_broad_scale" display_name="broad-scale environmental context">tropical desert biome</Attribute>
			<Attribute attribute_name="env feature" harmonized_name="env_local_scale" display_name="local-scale environmental context">dune</Attribute>
			<Attribute attribute_name="env package" harmonized_name="env_package" display_name="environmental package">soil</Attribute>
			<Attribute attribute_name="env_material" harmonized_name="env_medium" display_name="environmental medium">desert sand</Attribute>
			<Attribute attribute_name="environmental_package" harmonized_name="env_package" display_name="environmental package">soil</Attribute>
			<Attribute attribute_name="experimental_factor" harmonized_name="experimental_factor" display_name="experimental factor">Aridity</Attribute>
			<Attribute attribute_name="fine_sand_percent">28.04</Attribute>
			<Attribute attribute_name="gcms_analysis_batch">note applicable</Attribute>
			<Attribute attribute_name="gcms_run_location">PNNL</Attribute>
			<Attribute attribute_name="gcms_sample_name">EMP_TDS4_027_GC</Attribute>
			<Attribute attribute_name="geo loc name" harmonized_name="geo_loc_name" display_name="geographic location">Namibia</Attribute>
			<Attribute attribute_name="host subject id" harmonized_name="host_subject_id" display_name="host subject id">TDS4</Attribute>
			<Attribute attribute_name="investigation type" harmonized_name="investigation_type" display_name="investigation type">metagenome</Attribute>
			<Attribute attribute_name="iron_mg_per_l">0.4</Attribute>
			<Attribute attribute_name="latitude">-23.82001667</Attribute>
			<Attribute attribute_name="lcms_batch">8.15</Attribute>
			<Attribute attribute_name="lcms_extraction_protocol">Bulk_Seed_PNNL</Attribute>
			<Attribute attribute_name="lcms_position">8C5</Attribute>
			<Attribute attribute_name="lcms_replicate">no</Attribute>
			<Attribute attribute_name="lcms_sample_name_cmn">8C5_TDS4</Attribute>
			<Attribute attribute_name="lcms_sample_name_fbmn">8C5_TDS4.mzML</Attribute>
			<Attribute attribute_name="lcms_sample_type">Sample</Attribute>
			<Attribute attribute_name="lcms_sample_type_sub">Bulk</Attribute>
			<Attribute attribute_name="longitude">14.83786667</Attribute>
			<Attribute attribute_name="magnesium_mg_per_l">0.28</Attribute>
			<Attribute attribute_name="medium_sand_percent">57.78</Attribute>
			<Attribute attribute_name="nitrate_mg_per_l">0.57</Attribute>
			<Attribute attribute_name="original sample id">Makhalanyane47.TDS4</Attribute>
			<Attribute attribute_name="ph" harmonized_name="ph" display_name="pH">7.1</Attribute>
			<Attribute attribute_name="phosphorus_mg_per_l">0.14</Attribute>
			<Attribute attribute_name="physical_specimen_location">UCSD Knight Lab Freezer I</Attribute>
			<Attribute attribute_name="physical_specimen_remaining">TRUE</Attribute>
			<Attribute attribute_name="potassium_mg_per_l">0.21</Attribute>
			<Attribute attribute_name="project name" harmonized_name="project_name" display_name="project name">Namibia dune aridity gradient</Attribute>
			<Attribute attribute_name="read_count_shotgun_r1">156.0</Attribute>
			<Attribute attribute_name="read_count_shotgun_rep200">67.0</Attribute>
			<Attribute attribute_name="read_count_shotgun_woltka_uniq">9.0</Attribute>
			<Attribute attribute_name="sample name" harmonized_name="sample_name" display_name="sample name">qiita_sid_13114:13114.makhalanyane.47.s005</Attribute>
			<Attribute attribute_name="sample type" harmonized_name="sample_type" display_name="sample type">soil</Attribute>
			<Attribute attribute_name="sample_name_original">Makhalanyane47.TDS4</Attribute>
			<Attribute attribute_name="sample_name_plus_plate">9.Makhalanyane46.TDS4</Attribute>
			<Attribute attribute_name="sampling method">bulk</Attribute>
			<Attribute attribute_name="silt_and_clay_percent">0.45</Attribute>
			<Attribute attribute_name="sodium_mg_per_l">18.62</Attribute>
			<Attribute attribute_name="songbird_train_empo_3">Train</Attribute>
			<Attribute attribute_name="study_sample_number">5</Attribute>
			<Attribute attribute_name="sulfate_mg_per_l">5.57</Attribute>
			<Attribute attribute_name="very_coarse_sand_percent">0.03</Attribute>
			<Attribute attribute_name="very_fine_sand_percent">8.73</Attribute>
		</Attributes>
		<Status status="live" when="2020-12-20T10:49:06.378"/>
	</BioSample>
</BioSampleSet>
```