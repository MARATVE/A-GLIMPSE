from glimpse.src import glimpse
import util as util
from glimpse.src import user
import topics as t
import numpy as np
import logging
from glimpse.src.glimpse import GLIMPSE, Summary
import time
import glimpseonline as g
from importlib import reload
from random import sample, randint


def generate_run_name():
    return time.time()


run_name = generate_run_name()


# //TODO: Make a split
def generate_queries(kg, number_of_queries):
    nt = randint(int(number_of_queries/1000), int(number_of_queries/5))
    reload(g)
    reload(util)

    return util.generate_queries(kg, t.topics, number_of_queries, nt)


# //TODO: Make sure it works
def run_static_glimpse(kg, k, rounds, e, queries_train, queries_validation):
    global run_name
    t1 = time.time()

    # //TODO: Make sure GLIMPSE works with new indices
    summary = GLIMPSE(
        kg, k, queries_train, e
    )
    t2 = time.time()

    write_buffer = []
    # //TODO: Fix the path
    with open(f"runs/{run_name}.csv", "w+") as f:
        f.write(
            "round, unique_hits, no_unique_entities, total_hits, total, accuracy, speed_summary\n")

        for i in range(rounds):
            unique_hits, no_unique, total_hits, total, accuracy = compute_accuracy(
                # //TODO: Is it :i?
                kg, queries_validation[:i], summary)

            write_buffer.append(
                f"{i+1},{unique_hits},{no_unique},{total_hits},{total},{accuracy},{t2-t1}\n")

        for line in write_buffer:
            f.write(line)

# //TODO: Audit it


def recompute_glimpse(kg, k, rounds, e, queries_train, queries_validation, n):
    global run_name
    t1 = time.time()

    # //TODO: Make sure GLIMPSE works with new indices
    summary = GLIMPSE(
        kg, k, queries_train, e
    )
    t2 = time.time()

    write_buffer = []
    # //TODO: Fix the path
    with open(f"runs/{run_name}.csv", "w+") as f:
        f.write(
            "round, unique_hits, no_unique_entities, total_hits, total, accuracy, speed_summary\n")

        for i in range(rounds):
            unique_hits, no_unique, total_hits, total, accuracy = compute_accuracy(
                # //TODO: Is it :i?
                kg, queries_validation[:i], summary)

            # //TODO: Is it placed right?
            if i % n == 0:
                summary = GLIMPSE(
                    # //TODO: Is it :i ?
                    kg, k, queries_train.extend([queries_validation[:i]]), e
                )

            write_buffer.append(
                f"{i+1},{unique_hits},{no_unique},{total_hits},{total},{accuracy},{t2-t1}\n")

        for line in write_buffer:
            f.write(line)


def bandit_glimpse(kg, k, rounds, e, queries_train, queries_validation):

    # //TODO: Fix path
    with open(f"runs/{run_name}.csv", "w+") as f:
        f.write(
            "round, unique_hits, no_unique_entities, total_hits, total, accuracy, speed_summary, speed_feedback\n")

        write_buffer = []

        # //TODO: initial entities must have the entities extracted from the queries (I.e the answers)
        glimpse_online = g.Online_GLIMPSE(
            kg, k, initial_entities=queries_train)

        for i in range(rounds):
            t1 = time.time()
            summary = glimpse_online.construct_summary()
            t2 = time.time()
            # //TODO: Is :i right?
            round_queries = queries_validation[:i]
            glimpse_online.update_queries(round_queries)
            t3 = time.time()

            unique_hits, no_unique, total_hits, total, accuracy = compute_accuracy(
                kg, round_queries, summary)

            write_buffer.append(
                f"{i+1},{unique_hits},{no_unique},{total_hits},{total},{accuracy},{t2-t1},{t3-t2}\n")

        for line in write_buffer:
            f.write(line)


# //TODO: Fix for GLIMPSE summaries
def compute_accuracy(kg, queries, summary):
    # //TODO: Get no unique entities from bandit trainer code
    global no_unique_entities
    total_hits = 0
    total = 0
    unique_hits = set()
    for q in queries:
        for answer in q:
            total += 1
            answer = kg.entity_to_id[answer]
            if summary.has_entity(answer):
                unique_hits.add(answer)
                total_hits = total_hits + 1

    return len(unique_hits), no_unique_entities, total_hits, total, len(unique_hits)/no_unique_entities