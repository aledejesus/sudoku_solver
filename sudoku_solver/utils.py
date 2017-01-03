def remove_zeroes(arr):
    # removes zeroes from arr
    return filter(lambda x: x != 0, arr)


def get_empty_list():
    return list()


def clone_list(original):
    cloned = get_empty_list()

    for i in range(len(original)):
        cloned.append(list(original[i]))

    return cloned
