# RTDB-Neo4J
a Neo4J based implementation of Referent Tracking

Implements a persistence mechanism for RT tuples from the rts_core library. Specifically, it mainly implements the RtsStore interface from there using Neo4J embedded database as a back end.

Suggested command to kick the tires:

mvn -Dexec.classpathScope="test" -Dexec.cleanupDaemonThreads=false -Dexec.mainClass="neo4jtest.test.App" test-compile exec:java 1>test-run-output.txt 2>test-run-output.err
