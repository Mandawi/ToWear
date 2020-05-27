"""Functions that help us create suggested outfits given the user's closet."""

import operator
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


def closest(myclothes: Wardrobe, warmth_required: list, body_part: int):
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
        if body_part == 3:
            return Garment("slippers", [0, 0, 0, 0])
        if body_part == 2:
            return Garment("shorts", [0, 0, 0, 0])
        return Garment("nothing", [0, 0, 0, 0])
    if not list(filter(lambda x: x.warmth[body_part] != 0, myclothes)):
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
            ],
            reverse=True,
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
        if not tops:
            tops.append(Garment("tank top", [0, 0, 0, 0]))
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
    MY_CLOSET.delete_by_name("beanie")
    MY_CLOSET.delete_by_name("pom pom hat")
    MY_CLOSET.delete_by_name("trapper")
    NUMERICAL_OUTFIT = [2, 5, 5, 0]
    print(translate_outfit(MY_CLOSET, NUMERICAL_OUTFIT))
