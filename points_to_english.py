"""Functions that help us create suggested outfits given the user's closet."""

import operator
from functools import lru_cache
from clothes_manager import Wardrobe

# TODO: Fix lru_cache unhashable garment error
# @lru_cache(maxsize=5040)  # because 10*9*8*7 is 5040


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
    with_v = subsetsum_lists(tuple(myclothes[1:]), tuple(list(
        map(operator.sub, warmth_required, myclothes[0].warmth))))
    if with_v:
        return [myclothes[0].name] + with_v
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
    # * we will later use this to know in which places the user lacks enough garments
    # * so we can better approximate
    maximum_outfit = [sum(garment_warmth)
                      for garment_warmth in zip(*wardrobe_contents_warmths)]
    # get the difference between the suggested outfit and the maximum outfit
    difference = (list(
        map(operator.sub, original_outfit_in_numbers, maximum_outfit)))
    while outfit_in_words is None:
        # start at index where the difference between the suggested outfit
        # and the maximum outfit is greatest
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


# ! for testing only
if __name__ == "__main__":
    MY_CLOSET = Wardrobe()
    MY_CLOSET.generic_clothes_generator()
    NUMERICAL_OUTFIT = [9, 10, 10, 11]
    WORDED_OUTFIT = translate_outfit(MY_CLOSET, NUMERICAL_OUTFIT)
