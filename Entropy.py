from Distributions import ProbabilityDistribution
import math


def shannon_entropy(prob_distr: ProbabilityDistribution):
    entropy_inner_sum = 0
    for event in prob_distr.get_events():
        prob_event = prob_distr[event]
        if prob_event != 0:
            entropy_inner_sum += prob_event * math.log(prob_event)
        else:
            continue
    return -entropy_inner_sum


def conditional_shannon_entropy(prob_distr_a: ProbabilityDistribution, prob_distr_b: ProbabilityDistribution):
    """
    Returns the shannon entropy of A conditioned on B (i.e. H(A|B))

    In the case of these algorithms, each joint probability P[A_i,B_i] is simplified to P[A_i] as they are equivalent.
    This is not true for the general case of conditional shannon entropy.
    """
    events_A, events_B = prob_distr_a.get_events(), prob_distr_b.get_events()
    entropy_inner_sum = 0
    for event_A in events_A:
        for event_B in events_B:
            prob_event_A, prob_event_B = prob_distr_a[event_A], prob_distr_b[event_B]
            if prob_event_A != 0 and prob_event_B != 0:
                entropy_inner_sum += prob_event_A * math.log(prob_event_B / prob_event_A)
            else:
                continue
    return entropy_inner_sum


def mutual_information(a: ProbabilityDistribution, b: ProbabilityDistribution):
    return shannon_entropy(a) - conditional_shannon_entropy(a, b)
