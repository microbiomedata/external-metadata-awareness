# Synopsis #
NCBI SRA accepts genetic data and the associated quality scores produced by next generation sequencing technologies. Files
can be compressed using `gzip` or `bzip2`, and may be submitted in a tar archive. All file names must be unique and not
contain any sensitive information. File names as submitted will appear publicly in the Goolge and AWS clouds. Finally, all
files for a submission must be uploaded into a single folder. If you have any question or concern about your data or
submission, you should contact [SRA support](mailto:sra@ncbi.nlm.nih.gov).

Submission to SRA requires a submission xml file and fastq files. The required XML file for submission will be provided by [NMDC 
runtime](https://github.com/microbiomedata/nmdc-runtime). The Python scripts here will help validating the xml file, staging the FASTQ files, uploading files to the NCBI server 
and monitoring the submission status. Scripts are adapted from [METAGENOTE](https://github.com/niaid/metagenote/tree/master/sra_submission). 

The `sra_xml_validation.py` will validate the submission.xml through by NCBI biosample validate service.

The `sra_stage_files.py` will download fastq files into a stage folder.

The `sra_ascp.py` will sends all files to NCBI SRA server using ascp command.

The `sra_ascp_result_monitor.py` will check report.xml files for the NCBI SRA submission using ascp command.

**Note**: Do not submit human data into the public SRA database without consent. Make sure that you have consent from the
donating individual to make this data available in an unprotected database. Do not transmit human data intended for dbGAP
submissions to the public SRA database. For more information, please visit
[NCBI SRA submission guideline](https://www.ncbi.nlm.nih.gov/sra/docs/submit/).

# Prerequisites #
* Python 3.6 or newer
* `xml.dom.minidom`: a minimal DOM implementation for Python
* `xml.etree.ElementTree`: the ElementTree API, a simple and lightweight XML processor for Python
* `ascp`: [Aspera connect](https://www.ibm.com/aspera/connect/)

# Example #
### Validate the XML Files ###

The folder `test` contains an example submission.xml. To validate the XML required for SRA submission, run the command:

```
sra_xml_validation.py -i test/submission.xml 
```

If the command completes successfully, you should see the message similar to the one below. The script should generate a XML
files, `validate.xml` which shows the validation results.

```
Validating Biosample block 1 (SampleId: nmdc:bsm-12-gnfpt4835)...
{
  "Passed": "Yes"
}
```

The following is the description of the arguments and its default value.

* `-i/--input-file`: submission.xml 
* `-o/--output-file`: validation result xml (default: validate.xml)
  

### Staging FASTQ Files ###

The folder `test_staging` contains an example url text file `test_staging_files_url.txt`.

```
./sra_stage_files.py -i test_staging/test_staging_files_url.txt -o test
```

The command will have log info print on the screen as following. The fastq files should be downloaed to the staging folder `test`.

```
[2024-07-02 15:15] INFO: Downloading file test.1.fastq.gz to test/
[2024-07-02 15:15] INFO: Downloading file test.2.fastq.gz to test/
[2024-07-02 15:15] INFO: Downloading file test2.1.fastq.gz to test/
[2024-07-02 15:15] INFO: Downloading file test2.2.fastq.gz to test/
```

The following is the description of the arguments and its default value.

* `-i/--input-file`: a list of https url to files 
* `-o/--output-dir`: data staging directory


### Submit to SRA ###

When you are ready to submit to SRA, type:

```
sra_ascp.py --ncbi-sra-dir 'submit/Test/' --input-dir 'test/'  --ncbi-username 'username' --ncbi-private-key 'keyfile'
```

**Note**: Do not run this command unless you have collected all required files for your project. The input folder should
contain only the files required (example: `submission.xml`, `test.1.fastq.gz`, `test.1.fastq.gz` `test2.1.fastq.gz` and `test2.2.fastq.gz`, please remove `*.txt` file and `validate.xml`) by SRA for a submission. 

This script will run `ascp` to transfer all the files to SRA. You should make sure that `ascp` has been successfully
installed on the system. Otherwise, the command will fail. NCBI has chosen to use a product from
[Aspera, Inc (Emeryville, CA)](https://www.aspera.com/en/) because of improved data transfer characteristics. The software
includes a command line tool (`ascp`) that allows scripted data transfer. The software client is free for users exchanging
data with NCBI. For more information about `ascp`, please visit the
[Aspear Transfer Guide](https://www.ncbi.nlm.nih.gov/books/NBK242625/).

The following is the description of the arguments.

* `-f/--input-dir`: Directory that contains all the files for a submission.
* `-d/--ncbi-sra-dir`: Path to the destination BioProject SRA submission folder.
* `-i/--ncbi-private-key`: Path to your private key file. In order to use the Aspera upload service you will need to use a
private SSH key, individual users should contact [SRA](mailto:sra@ncbi.nlm.nih.gov) to request an Aspera private key.
* `-u/--ncbi-username`: Username of your SRA account.

### Check submission status ###

After submission, you can check the status, run the command:

```
sra_ascp_result_monitor.py --input-dir test -d submit/Test --ncbi-username 'username' --ncbi-private-key 'keyfile'

```

If the submission is successful, you should see the message similar to the one below.

```
[2024-07-02 15:36] INFO: BioSample nmdc:bsm-12-gnfpt4833 SAMN02350845
[2024-07-02 15:36] INFO: BioSample nmdc:bsm-12-gnfpt4833 SAMN02350845
[2024-07-02 15:36] INFO: BioSample nmdc:bsm-12-kwnkx8977 SAMN02350844
[2024-07-02 15:36] INFO: BioSample nmdc:bsm-12-kwnkx8977 SAMN02350844
[2024-07-02 15:36] INFO: SRA test1.fastq.gzbsm-12-gnfpt4833 SRR00255873
[2024-07-02 15:36] INFO: SRA test2.fastq.gz-nmdc:bsm-12-kwnkx8977 SRR00255872
[2024-07-02 15:36] INFO: Successfully Submit test_nmdc to NCBI
```

If the submission has errors, you should see error messages similar to the one below.

```
[2024-07-02 15:36] ERROR: An error occurred during submission processing. Please contact SRA helpdesk for more information. Please do not create another (duplicate) submission with the same data.
[2024-07-02 15:36] ERROR: Submission processing may be delayed due to necessary curator review. Please check spelling of organism, current information could not be resolved automatically and will require a taxonomy consult. For more information about providing a valid organism, including new species, metagenomes (microbiomes) and metagenome-assembled genomes, see https://www.ncbi.nlm.nih.gov/biosample/docs/organism/.
[2024-07-02 15:36] ERROR: These samples have the same Sample Names and different attributes. If they are different samples, please provide a unique Sample Name for each. If one is intended to be an update of the other, please stop this submission and contact biosamplehelp@ncbi.nlm.nih.gov.
[2024-07-02 15:36] ERROR: We will automatically transform the attribute value(s) you provided as follows.
```

If no `report.xml` is retrieved, this does not necessarily mean your submission failed.
The SRA system may not have generated it yet.

The following is the description of the arguments.

* `-f/--input-dir`: Directory that contains all the files for a submission.
* `-d/--ncbi-sra-dir`: Path to the destination BioProject SRA submission folder.
* `-i/--ncbi-private-key`: Path to your private key file. In order to use the Aspera upload service you will need to use a
private SSH key, individual users should contact [SRA](mailto:sra@ncbi.nlm.nih.gov) to request an Aspera private key.
* `-u/--ncbi-username`: Username of your SRA account.
* `-m/--max-time`: maximum time in sec for checking report.xml from remote site. (default: 1800)

# Epilogue #

You should receive email notification about the submission from NCBI. 

If your submission contain errors, the email will inform you about the error which should be similar to 
`sra_ascp_result_monitor.py` command report above.  You should wait for notification from the SRA that the submission has been
received and processed. During error correction, only make changes to SRA detected errors. All other changes will be ignored
by the SRA during resubmission. If additional changes are required, they can be made using the NCBI website after successful
submission.

If you are unsuccessful with the submission, you should contact [SRA staff](mailto:sra@ncbi.nlm.nih.gov) with the temporary
submission ID for further assistance.

# Comments and Suggestions #
If you have any comments or suggestions, please create an issue on github.



