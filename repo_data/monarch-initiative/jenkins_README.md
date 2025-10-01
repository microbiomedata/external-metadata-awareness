#### Monarch Ingest Pipeline

Jenkins pipeline for the monarch data ingest

##### FAQ

1. Cannot delete directory x, permission denied

In some failure states docker volumes will hang around and the jenkins user
will not be able to delete them. In this case ssh in and manually delete the director(ies).


2. A stage fails

Rerunning from the failed stage is fine, assuming no code has changed in the Jenkinsfile.

Note that the clique leader tsv in the QC script will not work if solr onward fails,
since it relys on the build ID of the current pipeline and the scigraph logs.
See https://github.com/monarch-initiative/release-utils/blob/master/scripts/parse-clique-warnings.sh

3. Golr load runs out of memory

Theres not much that can be done except messing with memory allocations of the various parts, or running on a larger machine.
Another option is to decrease the number of concurrent cypher queries here:
https://github.com/SciGraph/golr-loader/blob/master/src/main/java/org/monarch/golr/Pipeline.java#L53

Solr and Solr loader memory is set here:
https://github.com/monarch-initiative/solr-docker-monarch-golr/blob/master/files/run.sh#L19-L20

4. Golr load reports "Cannot contact high_mem:"

high_mem is the name of the jenkins agent on monarch4.
This may be a sign of an oncomming out of memory exception, or sometimes it resolves on its own.

5. Couldn't destroy threadgroup
```
[WARNING] Couldn't destroy threadgroup org.codehaus.mojo.exec.ExecJavaMojo$IsolatedThreadGroup[name=org.monarch.golr.SimpleLoaderMain,maxpri=10]

java.lang.IllegalThreadStateException
...
```

This happens at the end of the scigraph and solr stages sometimes, but doesn't seem to effect anything. The stage should still pass.

6. I've killed a stage using the jenkins UI but it is still running

This seems common especially for jobs running in a container.  In these cases you may need to ssh in and manually kill the job.

