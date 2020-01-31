import operator

from clothes_manager import Garment, Wardrobe
from functools import lru_cache


def findMin(warmth_required: int, clothes_ihave: dict, body_part: int) -> list:
    # ! NOTE: This function is expired and is no longer in use; for reason, see BUG below
    """Inspired by https://medium.com/@emailarunkumar/coin-exchange-problem-greedy-or-dynamic-programming-6e5ebe5a30b5
    Use a simple brute force algorithm to find clothes needed to achieve the desired temperature

    Arguments:
        warmth_required {int} - - the needed warmth
        clothes_ihave {dict} - - the wardrobe contents as {warmth[position]: garment} dictionary
        body_part {int} - - the body part 0: head, 1:top, 2:bottom, 3:feet

    Returns:
        list - - the outfit for this position
    """
    # outfit is a list of lists of Garments for each part of the body
    outfit = []
    warmths_sorted = sorted(clothes_ihave.keys(), reverse=False)
    i = len(warmths_sorted)-1
    while (i > 0):
        # ! BUG: Does not work when items that have effects on multiple body parts, such as coats, are chosen
        while (warmth_required >= warmths_sorted[i]):
            warmth_required = warmth_required - warmths_sorted[i]
            outfit.append(clothes_ihave[warmths_sorted[i]].name)
            # no more than one item from shoes
            if body_part == 3:
                return outfit
        i -= 1
    return outfit


@lru_cache(maxsize=5040)  # because 10*9*8*7 is 5040
def subsetsum_lists(myclothes: Wardrobe, warmth_required: list) -> list:
    """Use a recursive algorithm to find the smallest subset of myclothes
    such that its sum is equal to that of warmth_required, subset sum style.
    In addition, we use an lru_cache to make this much faster

    Arguments:
        myclothes {Wardrobe} -- the user's closet
        warmth_required {list} -- the list of suggested warmths (outfit_in_numbers) given by suggest_outfit in try_towear

    Returns:
        list -- the list of garment names whose warmths satisfy the warmth_required
    """
    myclothes = list(myclothes)
    warmth_required = list(warmth_required)
    if warmth_required == [0, 0, 0, 0]:
        return None
    elif len(myclothes) == 0:
        return None
    else:
        if myclothes[0].warmth == warmth_required:
            return [myclothes[0].name]
        else:
            with_v = subsetsum_lists(tuple(myclothes[1:]), tuple(list(
                map(operator.sub, warmth_required, myclothes[0].warmth))))
            if with_v:
                return [myclothes[0].name] + with_v
            else:
                return subsetsum_lists(tuple(myclothes[1:]), tuple(warmth_required))


def translate_outfit(wardrobe: Wardrobe, outfit_in_numbers: list) -> list:
    """Get an outfit in numbers and translate it to a list of outfits in words

    Arguments:
        wardrobe {Wardrobe} - - the closet of the user
        outfit_in_numbers {list} - - the outfit suggested in numbers

    Returns:
        list -- the outfit suggested in words
    """
    # save a copy of the outfit_in_numbers so that we can later modify it
    original_outfit_in_numbers = outfit_in_numbers.copy()
    # try subsetsum_lists on the current wardrobe contents and suggested outfit
    # * if we can't make an outfit that satisfies the warmth required, we'll try to approximate
    outfit_in_words = subsetsum_lists(
        tuple(wardrobe.contents), tuple(outfit_in_numbers))
    # get the warmths of all of the user's garments
    wardrobe_contents_warmths = [
        garment.warmth for garment in wardrobe.contents]
    # create an outfit combining everything in the user's closet
    # * we will later use this to know in which places the user lacks enough garments so we can better approximate
    maximum_outfit = [sum(garment_warmth)
                      for garment_warmth in zip(*wardrobe_contents_warmths)]
    # get the difference between the suggested outfit and the maximum outfit
    difference = (list(
        map(operator.sub, original_outfit_in_numbers, maximum_outfit)))
    while outfit_in_words == None:
        # start at index where the difference between the suggested outfit and the maximum outfit is greatest
        index_to_approximate = difference.index(max(difference))
        # > code for server logs
        print(
            f"The differnce between suggested outfit and maximum outfit is {difference}")
        # > end of code for server logs
        # reduce the warmth of the suggested outfit based on where the user lacks enough clothes
        outfit_in_numbers[index_to_approximate] -= 1
        difference[index_to_approximate] -= 1
        # try again
        outfit_in_words = subsetsum_lists(
            tuple(wardrobe.contents), tuple(outfit_in_numbers))
    # get the warmths of the garments in the outfit created
    final_outfit_state = [
        garment.warmth for garment in wardrobe.contents if garment.name in outfit_in_words]
    # > code for server logs
    final_outfit_state_numbers = [sum(garment_warmth)
                                  for garment_warmth in zip(*final_outfit_state)]
    print(
        f"Used: {final_outfit_state_numbers} versus Recommended: {original_outfit_in_numbers}")
    if sum(final_outfit_state_numbers) < sum(original_outfit_in_numbers):
        print("Looks like someone needs to go shopping")
    # > end of code for server logs
    return outfit_in_words


# * for testing only
if __name__ == "__main__":
    my_closet = Wardrobe()
    my_closet.generic_clothes_generator()
    outfit_in_numbers = [9, 10, 10, 11]
    outfit_in_words = translate_outfit(my_closet, outfit_in_numbers)
