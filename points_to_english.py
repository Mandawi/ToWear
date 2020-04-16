"""Functions that help us create suggested outfits given the user's closet."""

import operator
from functools import lru_cache
from clothes_manager import Wardrobe, Garment


class view(object):
    """class used by balsum
    source: https://stackoverflow.com/questions/9962568/fast-solution-to-subset-sum-algorithm-by-pisinger/9997386
    """

    def __init__(self, sequence, start):
        self.sequence, self.start = sequence, start

    def __getitem__(self, index):
        return self.sequence[index + self.start]

    def __setitem__(self, index, value):
        self.sequence[index + self.start] = value


def balsub(w: list, c: int) -> list:
    """A balanced algorithm for Subset-sum problem by David Pisinger
    
    Arguments:
        w {list} -- weights
        c {int} -- capacity of the knapsack
    
    Returns:
        list -- list of numbers whose sum add up to c
    """
    n = len(w)
    assert n > 0
    sum_w = 0
    r = 0
    for wj in w:
        # assert wj > 0
        sum_w += wj
        # assert wj <= c
        r = max(r, wj)
    assert sum_w > c
    b = 0
    w_bar = 0
    while w_bar + w[b] <= c:
        w_bar += w[b]
        b += 1
    s = [[0] * 2 * r for i in range(n - b + 1)]
    s_b_1 = view(s[0], r - 1)
    for mu in range(-r + 1, 1):
        s_b_1[mu] = -1
    for mu in range(1, r + 1):
        s_b_1[mu] = 0
    s_b_1[w_bar - c] = b
    for t in range(b, n):
        s_t_1 = view(s[t - b], r - 1)
        s_t = view(s[t - b + 1], r - 1)
        for mu in range(-r + 1, r + 1):
            s_t[mu] = s_t_1[mu]
        for mu in range(-r + 1, 1):
            mu_prime = mu + w[t]
            s_t[mu_prime] = max(s_t[mu_prime], s_t_1[mu])
        for mu in range(w[t], 0, -1):
            for j in range(s_t[mu] - 1, s_t_1[mu] - 1, -1):
                mu_prime = mu - w[j]
                s_t[mu_prime] = max(s_t[mu_prime], j)
    solved = False
    z = 0
    s_n_1 = view(s[n - b], r - 1)
    while z >= -r + 1:
        if s_n_1[z] >= 0:
            solved = True
            break
        z -= 1
    if solved:
        x = [False] * n
        for j in range(0, b):
            x[j] = True
        for t in range(n - 1, b - 1, -1):
            s_t = view(s[t - b + 1], r - 1)
            s_t_1 = view(s[t - b], r - 1)
            while True:
                j = s_t[z]
                assert j >= 0
                z_unprime = z + w[j]
                if z_unprime > r or j >= s_t[z_unprime]:
                    break
                z = z_unprime
                x[j] = False
            z_unprime = z - w[t]
            if z_unprime >= -r + 1 and s_t_1[z_unprime] >= s_t[z]:
                z = z_unprime
                x[t] = True
        return [w[j] for j in range(n) if x[j] == True]


def closest(myclothes: Wardrobe, warmth_required: list, body_part: list):
    """returns the closest item in the closet to the warmth_required for head, bottom, and feet
    inspiration: https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
    
    Arguments:
        myclothes {Wardrobe} -- the user's closet
        warmth_required {list} -- the warmth required for each body part
        body_part {int} -- the integer representing the body part (0: head, 2: bottom, 3: feet)
    
    Returns:
        list -- the list of garment names whose warmths satisfy the warmth_required for this body part
    """
    if warmth_required[body_part] <= 0:
        return Garment("nothing", [0, 0, 0, 0])
    suggested_item = myclothes[
        min(
            range(len(myclothes)),
            key=lambda i: abs(
                myclothes[i].warmth[body_part] - warmth_required[body_part]
            ),
        )
    ]
    return suggested_item


@lru_cache()  # because 10*9*8*7 is 5040
def subsetsum_lists(myclothes: Wardrobe, warmth_required: list) -> list:
    """Use a recursive algorithm to find the smallest subset of myclothes
    such that its sum is equal to that of warmth_required, subset sum style.
    In addition, we use an lru_cache to make this much faster

    Arguments:
        myclothes {Wardrobe} -- the user's closet
        warmth_required {list} -- the list of suggested warmths (outfit_in_numbers)
        given by suggest_outfit in try_towear

    Returns:
        list -- the list of garment names whose warmths satisfy the warmth_required
    """
    myclothes = list(myclothes)
    warmth_required = list(warmth_required)
    if warmth_required == [0, 0, 0, 0]:
        return None
    if not myclothes:
        return None
    if myclothes[0].warmth == warmth_required:
        return [myclothes[0].name]
    new_subset = subsetsum_lists(
        tuple(myclothes[1:]),
        tuple(list(map(operator.sub, warmth_required, myclothes[0].warmth))),
    )
    if new_subset:
        return [myclothes[0].name] + new_subset
    return subsetsum_lists(tuple(myclothes[1:]), tuple(warmth_required))


def translate_outfit_deprecated(wardrobe: Wardrobe, outfit_in_numbers: list) -> list:
    """Get an outfit in numbers and translate it to a list of outfits in words

    Arguments:
        wardrobe {Wardrobe} - - the closet of the user
        outfit_in_numbers {list} - - the outfit suggested in numbers

    Returns:
        list -- the outfit suggested in words
    """
    # TODO: IF SUGGESTED OUTFIT HAS NEGATIVE NUMBERS (i.e. it does not make sense) JUST GIVE BACK MAXIMUM CLOTHING
    # save a copy of the outfit_in_numbers so that we can later modify it
    original_outfit_in_numbers = outfit_in_numbers.copy()
    # try subsetsum_lists on the current wardrobe contents and suggested outfit
    # * if we can't make an outfit that satisfies the warmth required, we'll try to approximate
    outfit_in_words = subsetsum_lists(
        tuple(wardrobe.contents), tuple(outfit_in_numbers)
    )
    # get the warmths of all of the user's garments
    wardrobe_contents_warmths = [garment.warmth for garment in wardrobe.contents]
    # create an outfit combining everything in the user's closet
    # * we will later use this to know in which places the user lacks enough garments
    # * so we can better approximate
    maximum_outfit = [
        sum(garment_warmth) for garment_warmth in zip(*wardrobe_contents_warmths)
    ]
    # get the difference between the suggested outfit and the maximum outfit
    difference = list(map(operator.sub, original_outfit_in_numbers, maximum_outfit))
    while outfit_in_words is None:
        # start at index where the difference between the suggested outfit
        # and the maximum outfit is greatest
        index_to_approximate = difference.index(max(difference))
        # > code for server logs
        print(f"The suggested outfit is {outfit_in_numbers}")
        print(
            f"The differnce between suggested outfit and maximum outfit is {difference}"
        )
        # > end of code for server logs
        # reduce the warmth of the suggested outfit based on where the user lacks enough clothes
        outfit_in_numbers[index_to_approximate] -= 1
        difference[index_to_approximate] -= 1
        # try again
        outfit_in_words = subsetsum_lists(
            tuple(wardrobe.contents), tuple(outfit_in_numbers)
        )
    # get the warmths of the garments in the outfit created
    final_outfit_state = [
        garment.warmth
        for garment in wardrobe.contents
        if garment.name in outfit_in_words
    ]
    # > code for server logs
    final_outfit_state_numbers = [
        sum(garment_warmth) for garment_warmth in zip(*final_outfit_state)
    ]
    print(
        f"Used: {final_outfit_state_numbers} versus Recommended: {original_outfit_in_numbers}"
    )
    if sum(final_outfit_state_numbers) < sum(original_outfit_in_numbers):
        print("Looks like someone needs to go shopping")
    # > end of code for server logs
    return outfit_in_words


def translate_outfit(wardrobe: Wardrobe, outfit_in_numbers: list) -> list:
    """Get an outfit in numbers and translate it to a list of outfits in words.
    Uses closest function and pseudolinear Pisinger balsum for top.
    One closest warmth item each on head, bottom and feet.

    Arguments:
        wardrobe {Wardrobe} - - the closet of the user
        outfit_in_numbers {list} - - the outfit suggested in numbers

    Returns:
        list -- the outfit suggested in words
    """
    suggested_tops = balsub(
        sorted(
            [
                clothing.warmth[1]
                for clothing in wardrobe.contents
                if clothing.warmth[1] > 0
            ]
        ),
        outfit_in_numbers[1],
    )
    tops = [closest(wardrobe.contents, [0, top, 0, 0], 1) for top in suggested_tops]
    merged_top_bottom = []
    for top in tops:
        if sum(list(map(operator.sub, outfit_in_numbers, top.warmth))) < sum(
            outfit_in_numbers[:1] + outfit_in_numbers[2:]
        ):
            merged_top_bottom.append(top)
            tops.remove(top)
        outfit_in_numbers = list(map(operator.sub, outfit_in_numbers, top.warmth))
        if len(tops) == 0:
            tops.append(Garment("nothing", [0, 0, 0, 0]))
    if merged_top_bottom:
        worded_oufit = [
            f"Overall: {(', '.join([top_bottom.name for top_bottom in merged_top_bottom]))}.",
            f"Head: {closest(wardrobe.contents, outfit_in_numbers, 0).name}.",
            f"Top: {(', '.join([top.name for top in tops]))}.",
            f"Bottom: {closest(wardrobe.contents, outfit_in_numbers, 2).name}.",
            f"Feet: {closest(wardrobe.contents, outfit_in_numbers, 3).name}.",
        ]
    else:
        worded_oufit = [
            f"Head: {closest(wardrobe.contents, outfit_in_numbers, 0).name}.",
            f"Top: {(', '.join([top.name for top in tops]))}.",
            f"Bottom: {closest(wardrobe.contents, outfit_in_numbers, 2).name}.",
            f"Feet: {closest(wardrobe.contents, outfit_in_numbers, 3).name}.",
        ]
    return worded_oufit


# ! for testing only
if __name__ == "__main__":
    MY_CLOSET = Wardrobe()
    MY_CLOSET.generic_clothes_generator()
    NUMERICAL_OUTFIT = [0, 3, 2, 1]
    print(translate_outfit(MY_CLOSET, NUMERICAL_OUTFIT))
