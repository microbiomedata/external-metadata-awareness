## Synopsis
    
    :- use_module(library(semsim)).
    :- use_module(library(semsim/basic_rdfs)).
    :- use_module(library(semweb/rdf_db)).
    :- use_module(library(semweb/rdf_turtle)).
    
    load_all :-
        rdf_load('data/go-sample.ttl').
    
    t :-
        load_all,
        writeln(ix_start),
        generate_term_indexes,
        writeln(ix_done),
        semsim_element_pair(F1,F2),
        semsim_pair_all_scores(F1,F2,Scores),
        format('~w -vs- ~w:~n',[F1,F2]),
        forall(member(Score,Scores),
               format('  ~w~n',[Score])),
        fail.

## Description

Semantic similarity module for SWI-Prolog


