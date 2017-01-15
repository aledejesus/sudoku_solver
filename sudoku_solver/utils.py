def remove_zeroes(arr):
    # removes zeroes from arr
    return filter(lambda x: x != 0, arr)


def get_empty_list():
    return list()


def clone_list(original, contains_lists):
    cloned = list()

    if contains_lists:
        for lst in original:
            cloned.append(list(lst))
    else:
        cloned = list(original)

    return cloned
