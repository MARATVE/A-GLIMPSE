from experiments.comparison_experiments import bandit_glimpse, recompute_glimpse, run_static_glimpse
import os
from time import sleep
from glimpse.src.experiment_base import DBPedia, KnowledgeGraph, Freebase
from glimpse.src.query import generate_query
import repl_assistant as repl
import numpy as np
from multiprocessing import Process
import experiment


def makeTrainingTestSplit(answers, kg):
    train_split = [[entity for entity in answer_list if kg.is_entity(
        entity)] for answer_list in answers[0:140]]
    test_split = [[entity for entity in answer_list if kg.is_entity(
        entity)] for answer_list in answers[140:]]

    return train_split, test_split


def run_glimpse_once():
    K = [10**-i for i in range(1, 6)]
    E = [1e-2]

    answer_version = "2"
    version = "3"
    e = 0.1
    k = 0.01
    os.system('cd originalprojects && python3 experiments.py'
              + ' --method glimpse'
              + ' --percent-triples ' + str(k)
              + ' --version ' + version
              + ' --version-answers ' + answer_version
              + ' --epsilon ' + str(e)
              #                  + ' > ' + 'GLIMPSE' + version+'a' + answer_version + ' #K' + str(k) + '#E' + str(e) + '.out'
              #                  + ' &')
              )


def synthetic_experiment():
    kg = DBPedia('DBPedia3.9/')
    kg.load()
    number_of_topics = 200
    topics = kg.entity_names()
    topic_keys = [x for x in topics.keys()]
    topics = [topics[topic_keys[x]] for x in range(number_of_topics)]
    topic_keys = []
    queries = [generate_query(kg, topic) for topic in topics]
    answers = [x['Parse']['Answers'] for x in queries]
    answer_entity_names = [[a_name['EntityName']
                            for a_name in answer] for answer in answers]
    train_split, test_split = makeTrainingTestSplit(answer_entity_names, kg)
    e = 0.1
    k = 0.01
    summary = GLIMPSE(kg, k, train_split, e)
    mean_accuracy, total_entities, total_count = calculateAccuracyAndTotals(
        test_split, summary)
    print(mean_accuracy, total_entities, total_count)


def parameters_experiment():

    exp = experiment.Experiment("Static", "Parameters experiment")

    E = np.linspace(0.01, 1, 20, endpoint=False)
    for i in range(0, 20):
        run_static_glimpse(10000, 30, E[i], exp)

    for i in range(0, 20):
        recompute_glimpse(10000, 100, E[i], 10, exp)

    for i in range(0, 20):
        recompute_glimpse(10000, 100, 0.1, 5 * (i+1), exp)


def exp3m_parameters():
    exp = experiment.Experiment(
        comment="Diverse experiment med bandit parametre")

    E = np.linspace(0.01, 1, 10, endpoint=False)

    for i in range(0, 10):
        bandit_glimpse(10000, 1000, exp, E[i], same_queries=True)

    for i in range(0, 10):
        bandit_glimpse(10000, 1000, exp, E[i], same_queries=False)


def exp3m_longrun():
    exp = experiment.Experiment(
        comment="exp3m longrun same queries")

    bandit_glimpse(10000, 3000, exp, 0.1, same_queries=True)


def exp_longrun():
    exp = experiment.Experiment(comment="exp3 longrun")

    bandit_glimpse(10000, 10800, exp, 0.1, "exp3", same_queries=True)

def exp3m_non_adversarial():
    exp = experiment.Experiment(
        comment="exp3m non adversarial queries",
        adversarial_degree=0.00001)

    bandit_glimpse(10000, 2000, exp, 0.1, same_queries=True)

def exp3_non_adversarial():
    exp = experiment.Experiment(
        comment="exp3 non adversarial queries",
        adversarial_degree=0.00001)

    bandit_glimpse(10000, 2000, exp, 0.1, same_queries=True)


if __name__ == "__main__":
    from multiprocessing import Process
    p1 = Process(target=exp3m_non_adversarial)
    p2 = Process(target=exp3_non_adversarial)

    p1.start()
    p2.start()
