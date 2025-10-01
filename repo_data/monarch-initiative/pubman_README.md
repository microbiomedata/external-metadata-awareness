# pubman
Publication Manager

An app that helps to manage citations of HPO related articles.

![pubman GUI](src/main/resources/img/pubman.png?raw=true "PubMan")


To use PubMan, enter the PMID of an article that you want to add to the HPO/Monarch citation database. 
Choose one or more of the categories shown. If you choose ``HPO`` then the article will be shown on the
HPO website. If you choose ``Monarch`` the article will be marked as Monarch-specific but not necessarily related
to HPO. The other categories can be used to display certain classes of publications.

If the publication is correct, click the ``Add`` button to add it to the citation list.

If the publication has one of our team members as a coauthor, then we may want to include all publications that
cite this in our citation list. To do so, click the ``Retrieve citing`` button, which will utilize NCBI eUtils to
get a list of citing publications. The red line ``Number of articles in the stack waiting to be checked``
will show how many of these articles were found. Use the ``Show next`` button to retrieve data for the next publication
in the list, and add the publication to the citation database if appropriate.

Publications by our team that are related to the core mission of the HPO project should be marked as ``core``.

Note that the app will keep duplicate entries from being entered and will show the duplication in the GUI (it is possibly a little annoying,
but the app shows this right after you enter an article for this first time to keep you from clicking too many times).

## Show core publications

The app will show a list of all current ``core`` publications if the uyser clicks on the ``Show core publications`` button.

![pubman GUI](src/main/resources/img/pubman-corepubs.png?raw=true "PubMan")

A similar window will show all cutation citations. It is available in the Project menu (Menu entry ``Show curated publications``).

## Fetch new citations

Periodically, we will want to add new citations to the core publications. Press the ``New citations to core publications``
button. This step will take about a minute because we are not allow to rapidly send many requests to the eUtils server.
PubMan will show the publication being cited, which may make it easier to choose the appropriate strategy.

![pubman GUI](src/main/resources/img/pubman-newcitation.png?raw=true "PubMan")




Here is the format of the file that the app produces. It is a simple tab separated format that
can be used to populate a simple database to show on our website etc.


The format is simple. The first six fields include all the information about the citation (authorList, title, journal, year, volume, pages, pmid).
The next is if ``inhouse`` and should be T (for true) if somebody from the Monarch team is a coauthor on the paper.
The next item is ``hpo`` and indicates that the topic is related in some way to HPO (it should be set to true for any article
that cites one of our in house papers). The next item is ``monarch``, which should be set to true for any article that
is related to Monarch but not to the HPO. The final item is ``topic.list``, and contains a list of the topics, in case
we ever want to offer that feature on our webpage (but which we can exploit with scripts for writing reports etc.)

```$xslt
#authorList	title	journal	year	volume	pages	pmid	inhouse	hpo	monarch	topic.list
Jia J, Wang R, An Z, Guo Y, Ni X, Shi T	RDAD: A Machine Learning System to Support Phenotype-Based Rare Disease Diagnosis	Front Genet	2018	9	587	30564269	F	T	F	phenogeno.algorithm
Dozmorov MG	Reforming disease classification system-are we there yet? Ann Transl Med	2018 Nov;6(Suppl 1):S30	2103	PubMed Central PMCID	 PMC6291543	30613605	F	T	F	review
Chen Y, Xu R	Context-sensitive network analysis identifies food metabolites associated with Alzheimer's disease: an exploratory study	BMC Med Genomics	2019	12(Suppl 1)	17	30704467	F	T	F	systems.bio.algorithm
Boudellioua I, Kulmanov M, Schofield PN, Gkoutos GV, Hoehndorf R	DeepPVP: phenotype-based prioritization of causative variants using deep learning	BMC Bioinformatics	2019	20(1)	65	30727941	F	T	F	phenogeno.algorithm
```


# HPO publications
Our goal in the first round is to gather citations of HPO related articles published by our group for display on the HPO website.
The following is a list of publications we have processed in this way.

*  Robinson PN, Köhler S, Bauer S, Seelow D, Horn D, Mundlos S. The Human Phenotype Ontology: a tool for annotating and analyzing human hereditary disease.
  Am J Hum Genet. 2008 Nov;83(5):610-5. PubMed PMID: 18950739
* Köhler S, Schulz MH, Krawitz P, Bauer S, Dölken S, Ott CE, Mundlos C, Horn D, Mundlos S, Robinson PN. Clinical diagnostics in human genetics with semantic
  similarity searches in ontologies. Am J Hum Genet. 2009 Oct;85(4):457-64. PubMed PMID: 19800049
* Robinson PN, Mundlos S. The human phenotype ontology. Clin Genet. 2010 Jun;77(6):525-34. PubMed PMID: 20412080.
* Gkoutos GV, Mungall C, Dolken S, Ashburner M, Lewis S, Hancock J, Schofield P, Kohler S, Robinson PN. Entity/quality-based logical definitions for the human
 skeletal phenome using PATO. Conf Proc IEEE Eng Med Biol Soc. 2009;2009:7069-72.  PubMed PMID: 19964203.
* Köhler S, Bauer S, Mungall CJ, Carletti G, Smith CL, Schofield P, Gkoutos GV,  Robinson PN. Improving ontologies by automatic reasoning and evaluation of
  logical definitions. BMC Bioinformatics. 2011 Oct 27;12:418. PubMed PMID: 22032770.
* Schulz MH, Köhler S, Bauer S, Robinson PN. Exact score distribution computation for ontological similarity searches. BMC Bioinformatics. 2011 Nov
  12;12:441. PubMed PMID: 22078312.
* Köhler S, Doelken SC, Rath A, Aymé S, Robinson PN. Ontological phenotype standards for neurogenetics. Hum Mutat. 2012;33(9):1333-9. PubMed PMID: 22573485.
* Bauer S, Köhler S, Schulz MH, Robinson PN. Bayesian ontology querying for accurate and noise-tolerant semantic searches. Bioinformatics. 2012 Oct
  1;28(19):2502-8. PubMed PMID: 22843981.
*  Köhler S, Doelken SC, Ruef BJ, Bauer S, Washington N, Westerfield M, Gkoutos  G, Schofield P, Smedley D, Lewis SE, Robinson PN, Mungall CJ. Construction and
  accessibility of a cross-species phenotype ontology along with gene annotations for biomedical research. Version 2. F1000Res. 2013 Feb 1 [revised 2014 Jan
  1];2:30. doi: 10.12688/f1000research.2-30.v2. eCollection 2013. PubMed PMID:24358873.
* Doelken SC, Köhler S, Mungall CJ, Gkoutos GV, Ruef BJ, Smith C, Smedley D, Bauer S, Klopocki E, Schofield PN, Westerfield M, Robinson PN, Lewis SE.
  Phenotypic overlap in the contribution of individual genes to CNV pathogenicity  revealed by cross-species computational analysis of single-gene mutations in
  humans, mice and zebrafish. Dis Model Mech. 2013 Mar;6(2):358-72. PubMed PMID: 23104991.
*  Köhler S, Doelken SC, Mungall CJ, Bauer S, Firth HV, Bailleul-Forestier I,
  Black GC, Brown DL, Brudno M, Campbell J, FitzPatrick DR, Eppig JT, Jackson AP,
  Freson K, Girdea M, Helbig I, Hurst JA, Jähn J, Jackson LG, Kelly AM, Ledbetter
  DH, Mansour S, Martin CL, Moss C, Mumford A, Ouwehand WH, Park SM, Riggs ER,
  Scott RH, Sisodiya S, Van Vooren S, Wapner RJ, Wilkie AO, Wright CF, Vulto-van
  Silfhout AT, de Leeuw N, de Vries BB, Washingthon NL, Smith CL, Westerfield M,
  Schofield P, Ruef BJ, Gkoutos GV, Haendel M, Smedley D, Lewis SE, Robinson PN.
  The Human Phenotype Ontology project: linking molecular biology and disease
  through phenotype data. Nucleic Acids Res. 2014 Jan;42(Database issue):D966-74.
  doi: 10.1093/nar/gkt1026. Epub 2013 Nov 11. PubMed PMID: 24217912.
* Oellrich A, Koehler S, Washington N; Sanger Mouse Genetic Project, Mungall C,
  Lewis S, Haendel M, Robinson PN, Smedley D. The influence of disease categories
  on gene candidate predictions from model organism phenotypes. J Biomed Semantics.
  2014 Jun 3;5(Suppl 1 Proceedings of the Bio-Ontologies Spec Interest G):S4. doi:
  10.1186/2041-1480-5-S1-S4. eCollection 2014. PubMed PMID: 25093073
*  Zemojtel T, Köhler S, Mackenroth L, Jäger M, Hecht J, Krawitz P, Graul-Neumann
  L, Doelken S, Ehmke N, Spielmann M, Oien NC, Schweiger MR, Krüger U, Frommer G,
  Fischer B, Kornak U, Flöttmann R, Ardeshirdavani A, Moreau Y, Lewis SE, Haendel
  M, Smedley D, Horn D, Mundlos S, Robinson PN. Effective diagnosis of genetic
  disease by computational phenotype analysis of the disease-associated genome. Sci
  Transl Med. 2014 Sep 3;6(252):252ra123. doi: 10.1126/scitranslmed.3009262. PubMed
  PMID: 25186178.
* Ibn-Salem J, Köhler S, Love MI, Chung HR, Huang N, Hurles ME, Haendel M,
  Washington NL, Smedley D, Mungall CJ, Lewis SE, Ott CE, Bauer S, Schofield PN,
  Mundlos S, Spielmann M, Robinson PN. Deletions of chromosomal regulatory
  boundaries are associated with congenital disease. Genome Biol. 2014 Sep
  4;15(9):423. doi: 10.1186/s13059-014-0423-1. PubMed PMID: 25315429.
* Köhler S, Schoeneberg U, Czeschik JC, Doelken SC, Hehir-Kwa JY, Ibn-Salem J,
  Mungall CJ, Smedley D, Haendel MA, Robinson PN. Clinical interpretation of CNVs
  with cross-species phenotype data. J Med Genet. 2014 Nov;51(11):766-772. doi:
  10.1136/jmedgenet-2014-102633. Epub 2014 Oct 3. PubMed PMID: 25280750.
* Groza T, Köhler S, Doelken S, Collier N, Oellrich A, Smedley D, Couto FM,
  Baynam G, Zankl A, Robinson PN. Automatic concept recognition using the human
  phenotype ontology reference and test suite corpora. Database (Oxford). 2015 Feb
  27;2015. pii: bav005. doi: 10.1093/database/bav005. Print 2015. PubMed PMID:
  25725061;
* Groza T, Köhler S, Moldenhauer D, Vasilevsky N, Baynam G, Zemojtel T, Schriml
  LM, Kibbe WA, Schofield PN, Beck T, Vasant D, Brookes AJ, Zankl A, Washington NL,
  Mungall CJ, Lewis SE, Haendel MA, Parkinson H, Robinson PN. The Human Phenotype
  Ontology: Semantic Unification of Common and Rare Disease. Am J Hum Genet. 2015
  Jul 2;97(1):111-24. doi: 10.1016/j.ajhg.2015.05.020. Epub 2015 Jun 25. PubMed
  PMID: 26119816.
* Mungall CJ, Washington NL, Nguyen-Xuan J, Condit C, Smedley D, Köhler S, Groza
  T, Shefchek K, Hochheiser H, Robinson PN, Lewis SE, Haendel MA. Use of model
  organism and disease databases to support matchmaking for human disease gene
  discovery. Hum Mutat. 2015 Oct;36(10):979-84. doi: 10.1002/humu.22857. Epub 2015
  Sep 8. PubMed PMID: 26269093;
*  Robinson PN, Mungall CJ, Haendel M. Capturing phenotypes for precision
  medicine. Cold Spring Harb Mol Case Stud. 2015 Oct;1(1):a000372. doi:
  10.1101/mcs.a000372. PubMed PMID: 27148566;
*  Meehan TF, Conte N, West DB, Jacobsen JO, Mason J, Warren J, Chen CK, Tudose
  I, Relac M, Matthews P, Karp N, Santos L, Fiegel T, Ring N, Westerberg H,
  Greenaway S, Sneddon D, Morgan H, Codner GF, Stewart ME, Brown J, Horner N;
  International Mouse Phenotyping Consortium, Haendel M, Washington N, Mungall CJ,
  Reynolds CL, Gallegos J, Gailus-Durner V, Sorg T, Pavlovic G, Bower LR, Moore M,
  Morse I, Gao X, Tocchini-Valentini GP, Obata Y, Cho SY, Seong JK, Seavitt J,
  Beaudet AL, Dickinson ME, Herault Y, Wurst W, de Angelis MH, Lloyd KCK, Flenniken
  AM, Nutter LMJ, Newbigging S, McKerlie C, Justice MJ, Murray SA, Svenson KL,
  Braun RE, White JK, Bradley A, Flicek P, Wells S, Skarnes WC, Adams DJ, Parkinson
  H, Mallon AM, Brown SDM, Smedley D. Disease model discovery from 3,328 gene
  knockouts by The International Mouse Phenotyping Consortium. Nat Genet. 2017
  Aug;49(8):1231-1238. doi: 10.1038/ng.3901. Epub 2017 Jun 26. PubMed PMID:
  28650483;
* Bone WP, Washington NL, Buske OJ, Adams DR, Davis J, Draper D, Flynn ED,
  Girdea M, Godfrey R, Golas G, Groden C, Jacobsen J, Köhler S, Lee EM, Links AE,
  Markello TC, Mungall CJ, Nehrebecky M, Robinson PN, Sincan M, Soldatos AG, Tifft
  CJ, Toro C, Trang H, Valkanas E, Vasilevsky N, Wahl C, Wolfe LA, Boerkoel CF,
  Brudno M, Haendel MA, Gahl WA, Smedley D. Computational evaluation of exome
  sequence data using human and model organism phenotypes improves diagnostic
  efficiency. Genet Med. 2016 Jun;18(6):608-17. doi: 10.1038/gim.2015.137. Epub
  2015 Nov 12. PubMed PMID: 26562225;
* Köhler S, Vasilevsky NA, Engelstad M, Foster E, McMurry J, Aymé S, Baynam G,
  Bello SM, Boerkoel CF, Boycott KM, Brudno M, Buske OJ, Chinnery PF, Cipriani V,
  Connell LE, Dawkins HJ, DeMare LE, Devereau AD, de Vries BB, Firth HV, Freson K,
  Greene D, Hamosh A, Helbig I, Hum C, Jähn JA, James R, Krause R, F Laulederkind
  SJ, Lochmüller H, Lyon GJ, Ogishima S, Olry A, Ouwehand WH, Pontikos N, Rath A,
  Schaefer F, Scott RH, Segal M, Sergouniotis PI, Sever R, Smith CL, Straub V,
  Thompson R, Turner C, Turro E, Veltman MW, Vulliamy T, Yu J, von Ziegenweidt J,
  Zankl A, Züchner S, Zemojtel T, Jacobsen JO, Groza T, Smedley D, Mungall CJ,
  Haendel M, Robinson PN. The Human Phenotype Ontology in 2017. Nucleic Acids Res.
  2017 Jan 4;45(D1):D865-D876. doi: 10.1093/nar/gkw1039. Epub 2016 Nov 28. Review.
  PubMed PMID: 27899602;
* Robinson PN, Köhler S, Oellrich A; Sanger Mouse Genetics Project, Wang K,
  Mungall CJ, Lewis SE, Washington N, Bauer S, Seelow D, Krawitz P, Gilissen C,
  Haendel M, Smedley D. Improved exome prioritization of disease genes through
  cross-species phenotype comparison. Genome Res. 2014 Feb;24(2):340-8. doi:
  10.1101/gr.160325.113. Epub 2013 Oct 25. PubMed PMID: 24162188;
*  Oellrich A; Sanger Mouse Genetics Project, Smedley D. Linking tissues to
  phenotypes using gene expression profiles. Database (Oxford). 2014 Mar
  13;2014:bau017. doi: 10.1093/database/bau017. Print 2014. PubMed PMID: 24634472.
*  Oellrich A, Jacobsen J, Papatheodorou I; Sanger Mouse Genetics Project,
  Smedley D. Using association rule mining to determine promising secondary
  phenotyping hypotheses. Bioinformatics. 2014 Jun 15;30(12):i52-59. doi:
  10.1093/bioinformatics/btu260. PubMed PMID: 24932005;
* Smedley D, Köhler S, Czeschik JC, Amberger J, Bocchini C, Hamosh A, Veldboer J, Zemojtel T, Robinson PN (2014)
  Walking the interactome for candidate prioritization in exome sequencing studies of Mendelian diseases.
  Bioinformatics. 2014 Nov 15;30(22):3215-22. PubMed  PMID: 25078397
* Smedley D, Robinson PN. Phenotype-driven strategies for exome prioritization
   of human Mendelian disease genes. Genome Med. 2015 Jul 30;7(1):81. doi:
   10.1186/s13073-015-0199-2. eCollection 2015. Review. PubMed PMID: 26229552;
* Haendel MA, Vasilevsky N, Brush M, Hochheiser HS, Jacobsen J, Oellrich A,
  Mungall CJ, Washington N, Köhler S, Lewis SE, Robinson PN, Smedley D. Disease
  insights through cross-species phenotype comparisons. Mamm Genome. 2015
  Oct;26(9-10):548-55. doi: 10.1007/s00335-015-9577-8. Epub 2015 Jun 20. Review.
  PubMed PMID: 26092691;
* Smedley D, Jacobsen JO, Jäger M, Köhler S, Holtgrewe M, Schubach M, Siragusa
  E, Zemojtel T, Buske OJ, Washington NL, Bone WP, Haendel MA, Robinson PN.
  Next-generation diagnostics and disease-gene discovery with the Exomiser. Nat
  Protoc. 2015 Dec;10(12):2004-15. doi: 10.1038/nprot.2015.124. Epub 2015 Nov 12.
  PubMed PMID: 26562621;
*  Bone WP, Washington NL, Buske OJ, Adams DR, Davis J, Draper D, Flynn ED,
  Girdea M, Godfrey R, Golas G, Groden C, Jacobsen J, Köhler S, Lee EM, Links AE,
  Markello TC, Mungall CJ, Nehrebecky M, Robinson PN, Sincan M, Soldatos AG, Tifft
  CJ, Toro C, Trang H, Valkanas E, Vasilevsky N, Wahl C, Wolfe LA, Boerkoel CF,
  Brudno M, Haendel MA, Gahl WA, Smedley D. Computational evaluation of exome
  sequence data using human and model organism phenotypes improves diagnostic
  efficiency. Genet Med. 2016 Jun;18(6):608-17. doi: 10.1038/gim.2015.137. Epub
  2015 Nov 12. PubMed PMID: 26562225;
* Köhler S, Robinson PN. [Diagnostics in human genetics : Integration of
  phenotypic and genomic data]. Bundesgesundheitsblatt Gesundheitsforschung
  Gesundheitsschutz. 2017 May;60(5):542-549. doi: 10.1007/s00103-017-2538-5.
  German. PubMed PMID: 28293716.
* Maiella S, Olry A, Hanauer M, Lanneau V, Lourghi H, Donadille B, Rodwell C,
  Köhler S, Seelow D, Jupp S, Parkinson H, Groza T, Brudno M, Robinson PN, Rath A.
  Harmonising phenomics information for a better interoperability in the rare
  disease field. Eur J Med Genet. 2018 Nov;61(11):706-714. doi:
  10.1016/j.ejmg.2018.01.013. Epub 2018 Feb 7. Review. PubMed PMID: 29425702.
* Smedley D, Schubach M, Jacobsen JOB, Köhler S, Zemojtel T, Spielmann M, Jäger
  M, Hochheiser H, Washington NL, McMurry JA, Haendel MA, Mungall CJ, Lewis SE,
  Groza T, Valentini G, Robinson PN. A Whole-Genome Analysis Framework for
  Effective Identification of Pathogenic Regulatory Variants in Mendelian Disease.
  Am J Hum Genet. 2016 Sep 1;99(3):595-606. doi: 10.1016/j.ajhg.2016.07.005. Epub
  2016 Aug 25. PubMed PMID: 27569544
* Hombach D, Schwarz JM, Knierim E, Schuelke M, Seelow D, Köhler S. Phenotero:
  Annotate as you write. Clin Genet. 2019 Feb;95(2):287-292. doi:
  10.1111/cge.13471. Epub 2018 Dec 7. PubMed PMID: 30417324.
* Köhler S. Improved ontology-based similarity calculations using a study-wise
  annotation model. Database (Oxford). 2018 Jan 1;2018. doi:
  10.1093/database/bay026. PubMed PMID: 29688377; PubMed Central PMCID: PMC5868182.

