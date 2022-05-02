import math

from Privacy import Entropy
from Privacy.Distributions import ProbabilityDistribution, JointProbabilityDistribution
from Sanitise import Helper
from Sanitise.Helper import GeneralisationFunction


def shannon_entropy(prob_distr: ProbabilityDistribution):
    entropy_inner_sum = 0
    for event in prob_distr.get_events():
        prob_event = prob_distr[event]
        if prob_event != 0:
            entropy_inner_sum += prob_event * math.log(1 / prob_event, 2)
        else:
            continue
    return entropy_inner_sum


def conditional_shannon_entropy(prob_distr_Y: ProbabilityDistribution, prob_distr_X: ProbabilityDistribution,
                                joint: JointProbabilityDistribution):
    """
    Returns the shannon entropy of A conditioned on B (i.e. H(A|B))

    In the case of these algorithms, each joint probability P[A_i,B_i] is simplified to P[A_i] as they are equivalent.
    This is not true for the general case of conditional shannon entropy.
    """
    events_X, events_Y = prob_distr_X.get_events(), prob_distr_Y.get_events()
    entropy_inner_sum = 0
    for event_X in events_X:
        for event_Y in events_Y:
            prob_event_X, prob_event_Y = prob_distr_X[event_X], prob_distr_Y[event_Y]
            # simplification made in the paper as they are equivalent in our unique case
            # of sensitive/generalised patterns in input/output sequences
            # joint_prob = prob_event_Y  # P[p,ph] = P[p] because P[ph|p] = 1; unique solution for each p

            joint_prob = joint.get(event_X, event_Y)
            # FIXME sometimes joint_prob is None - why?
            if joint_prob == 0:
                continue
            cond_prob = joint_prob / prob_event_X  # P(Y_i | X_i) = P(Y_i, X_i) / P(X_i)
            entropy_inner_sum += joint_prob * math.log(1 / cond_prob, 2)
    return entropy_inner_sum


def mutual_information(a: ProbabilityDistribution, b: ProbabilityDistribution, joint: JointProbabilityDistribution):
    H_S = shannon_entropy(a)
    H_S_giv_G = conditional_shannon_entropy(a, b, joint)
    I_S_G = H_S - H_S_giv_G
    tests = 0 <= H_S and 0 <= H_S_giv_G and H_S_giv_G <= H_S and I_S_G <= H_S
    if not tests:
        print(f"Test failed.")
        print(f"H({a}) = {H_S:.2f}")
        print(f"H({a}|{b}) = {H_S_giv_G:.2f}")
        print()
    return shannon_entropy(a) - conditional_shannon_entropy(a, b, joint)


def inference_gain(input_sequence, sensitive_patterns, generalisation_strategies: GeneralisationFunction):
    generalised_patterns = Helper.sanitise_pats(sensitive_patterns, generalisation_strategies)
    sanitised_sequence = Helper.sanitise_seq(input_sequence, generalisation_strategies)
    # Sensitive pattern probability distribution
    S = ProbabilityDistribution(input_sequence)
    # Generalised pattern probability distribution
    G = ProbabilityDistribution(sanitised_sequence)
    joint_S_G = JointProbabilityDistribution(input_sequence, sanitised_sequence)
    return Entropy.mutual_information(S, G, joint_S_G)
