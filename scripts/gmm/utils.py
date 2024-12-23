"""
* Based on https://github.com/dimitymiller/openset_detection/blob/main/mmdetection/utils.py
* BSD 3-Clause License
* Copyright (c) 2021, Dimity Miller
* Copyright (c) SafeDNN group 2023
"""

import sklearn.mixture as sm
import numpy as np


def fit_gmms(
    logits,
    labels,
    ious,
    confs,
    scoreThresh,
    iouThresh,
    num_classes,
    components=1,
    covariance_type="full",
):
    gmms = [None for i in range(num_classes)]
    for i in range(num_classes):
        ls = logits[labels == i]
        iou = ious[labels == i]
        conf = confs[labels == i]

        if (
            len(ls) < components + 2
        ):  # no objects from this class were detected, or not enough given the components number
            continue

        # mask for high iou and high conf
        mask = (iou >= iouThresh) * (conf >= scoreThresh)
        lsThresh = ls[mask]

        # only threshold if there is enough logits given the amount of components
        if len(lsThresh) < components + 2:
            lsThresh = ls

        gmms[i] = sm.GaussianMixture(
            n_components=components,
            random_state=0,
            max_iter=200,
            n_init=2,
            covariance_type=covariance_type,
        ).fit(lsThresh)

    return gmms


def gmm_uncertainty(allLogits, gmms):
    gmmScores = []
    # test all data in 10 batches - not too slow, doesn't overload cpu
    # intervals = np.ceil(len(allLogits) / 10)
    # rn = 10 if len(allLogits) > 10 else len(allLogits)
    # sI = [int(i * intervals) for i in range(rn)]
    # eI = [int(s + intervals) for s in sI]
    for i in range(allLogits.shape[0]):
        clsScores = []
        ls = allLogits[i].reshape((1, -1))

        # find logit log likelihood for every class GMM
        for clsIdx, gmm in enumerate(gmms):
            if gmm == None:
                continue

            gmmLL = gmm.score_samples(ls)
            clsScores += [gmmLL]

        clsScores = np.array(clsScores)

        # we use the maximum likelihood to reperesent uncertainty
        maxScore = np.max(clsScores, axis=0)
        gmmScores += list(maxScore)

    gmmScores = np.array(gmmScores)
    return gmmScores
