# apollo-log-scraper

    node logListener.js -f ~/.aws/credentials.json -b apollo-usage-2.0.5-snapshot 

Credentials are:
  
    
	{ "accessKeyId": "AKXXXXXXXXXXXXXXXXXQ", "secretAccessKey": "xbnXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXs4uK", "region": "us-west-1" }

Logs are of the form:


```
XX.AA.YY.ZZ	19/Nov/2016:22:52:50         +0000      server=ApolloSever-14465169311962751821&environment=test
XX.AA.YY.ZZ	19/Nov/2016:22:52:46         +0000      server=ApolloSever-6175292871747850087829579771&environment=test
XX.AA.YY.ZZ	19/Nov/2016:22:52:46         +0000      server=ApolloSever-1633772635320257128467956521&environment=test
XX.AA.YY.ZZ	19/Nov/2016:22:53:41         +0000      server=ApolloSever-13256381278476684281448727691&environment=test
XXX.Y.ZZZ.BB 19/Nov/2016:22:54:31 +0000      server=ApolloSever-15358652641710876876&environment=test
XXX.Y.ZZZ.BB 19/Nov/2016:22:54:10 +0000      server=ApolloSever-15358652641710876876&environment=test&message=running&num_users=0&num_organisms=0
ZZ.XX.YY.BB  17/Nov/2016:22:12:44 +0000      message=start
ZZ.XX.YY.BB  17/Nov/2016:22:12:45 +0000      message=running
ZX.YA.YY.AA  17/Nov/2016:22:13:09 +0000      None
XXX.Y.ZZZ.AA    17/Nov/2016:23:48:12 +0000      server=ApolloSever-9810672151655334278255254646&environment=development&message=running&numUsers=2&numAnnotations=273127&numOrganisms=3
XXX.Y.ZZZ.AA    17/Nov/2016:23:48:17 +0000      server=ApolloSever-9810672151655334278255254646&environment=development&message=running&numUsers=2&numAnnotations=273127&numOrganisms=3
XXX.Y.ZZZ.AA    17/Nov/2016:23:48:22 +0000      server=ApolloSever-9810672151655334278255254646&environment=development&message=running&numUsers=2&numAnnotations=273127&numOrganisms=3
XXX.Y.ZZZ.AA    17/Nov/2016:23:48:27 +0000      server=ApolloSever-9810672151655334278255254646&environment=development&message=running&numUsers=2&numAnnotations=273127&numOrganisms=3
```
