import numpy as np
import itertools as it


def mergings_from(A, B):
    # Calculate number of mergings to reach B from A
    A2B = {}
    d = 0
    mapped_to = set({})
    for a in A:
        if A[a] not in A2B:
            A2B[A[a]] = B[a]
            if B[a] in mapped_to:
                d += 1
            else:
                mapped_to.add(B[a])
        elif A2B[A[a]] != B[a]:
            return -1
    return d


def all_maximal_partitions(qubits, NS_list):
    # Initial partition
    partitions = [{i: i for i in qubits}]
    # Add all constraints sequentially
    # Here there is room for improvement in the order of the NSs
    for NS in NS_list:
        surely_maximal = []
        potentially_maximal = []
        for partition in partitions:
            # Find DMs on both sides
            DMs = {
                i: set(
                    [
                        p
                        for p in partition.values()
                        if len([j for j in gi if partition[j] == p]) > 0
                    ]
                )
                for i, gi in enumerate(NS)
            }
            if len(DMs[0] & DMs[1]) != 0:
                # NS already fulfilled for partition
                surely_maximal.append(partition.copy())
            else:
                # Add all the mergings compatible with NS
                potentially_maximal += [
                    {i: A if partition[i] == B else partition[i] for i in partition}
                    for A, B in it.product(DMs[0], DMs[1])
                ]

        # Filter 1: some Ps in potentially_maximal may be trivially generated from others in surely_maximal
        potentially_maximal = [
            p
            for p in potentially_maximal
            if np.array([mergings_from(m, p) < 0 for m in surely_maximal]).all()
        ]
        filtered_maximal = []
        for i, p in enumerate(potentially_maximal):
            # Filter 2: some Ps in potentially_maximal may be trivially generated from others in same set
            not_from_potent_maximal = np.array(
                [
                    mergings_from(m, p) < 1
                    for j, m in enumerate(potentially_maximal)
                    if j != i
                ]
            ).all()
            # Filter 3: some Ps in potentially_maximal may be repeated
            not_already_in_filtered = np.array(
                [mergings_from(m, p) < 0 for m in filtered_maximal]
            ).all()
            if not_from_potent_maximal and not_already_in_filtered:
                filtered_maximal.append(p.copy())
        partitions = surely_maximal + filtered_maximal
    return clean(partitions)


def clean(partitions):
    # Order the partitions according to smallest element in each group
    clean = []
    for P in partitions:
        smallest = {}
        for p in P:
            if P[p] not in smallest or p < smallest[P[p]]:
                smallest[P[p]] = p
        sort = sorted(smallest, key=smallest.get)
        clean.append({p: sort.index(P[p]) for p in sorted(P)})
    return clean
