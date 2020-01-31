import operator

from clothes_manager import Garment, Wardrobe


def subsetsum_lists(myclothes: Wardrobe, warmth_required: list) -> list:

    if warmth_required == [0, 0, 0, 0]:
        return None
    elif len(myclothes) == 0:
        return None
    else:
        if myclothes[0].warmth == warmth_required:
            # print(myclothes[0].name, myclothes[0].warmth)
            return [myclothes[0].name]
        else:
            with_v = subsetsum_lists(myclothes[1:], (list(
                map(operator.sub, warmth_required, myclothes[0].warmth))))
            if with_v:
                # print(myclothes[0].name, myclothes[0].warmth)
                return [myclothes[0].name] + with_v
            else:
                return subsetsum_lists(myclothes[1:], warmth_required)


def findMin(warmth_required: int, clothes_ihave: dict, body_part: int) -> list:
    # Inspired by https://medium.com/@emailarunkumar/coin-exchange-problem-greedy-or-dynamic-programming-6e5ebe5a30b5
    """Use a napasack solving algorithm to find clothes needed to achieve the desired temperature

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
        # FIXME: Must reduce all positions when items that have effects on multiple positions like coat are chosen
        while (warmth_required >= warmths_sorted[i]):
            warmth_required = warmth_required - warmths_sorted[i]
            outfit.append(clothes_ihave[warmths_sorted[i]].name)
            # no more than one item from shoes
            if body_part == 3:
                return outfit
        i -= 1
    return outfit


def translate_outfit(wardrobe: Wardrobe, outfit_in_numbers: list) -> list:
    """get an outfit in numbers and translate it to a list of outfits in words

    Arguments:
        wardrobe {Wardrobe} - - the closet of the user
        outfit_in_numbers {list} - - the outfit suggested in numbers

    Returns:
        list -- the outfit suggested in words
    """
    outfit_in_words = subsetsum_lists(wardrobe.contents, outfit_in_numbers)
    print(outfit_in_numbers)
    original_outfit_in_numbers = outfit_in_numbers.copy()
    print(outfit_in_words)
    wardrobe_contents_warmths = [
        garment.warmth for garment in wardrobe.contents]
    all_wardrobe = [sum(garment_warmth)
                    for garment_warmth in zip(*wardrobe_contents_warmths)]
    difference = (list(
        map(operator.sub, original_outfit_in_numbers, all_wardrobe)))
    print("difference", difference)
    i = difference.index(max(difference))
    while outfit_in_words == None:
        outfit_in_numbers[i] -= 1
        difference[i] -= 1
        outfit_in_words = subsetsum_lists(wardrobe.contents, outfit_in_numbers)
        i = difference.index(max(difference))
        print(outfit_in_words)
    final_outfit_state = [
        garment.warmth for garment in wardrobe.contents if garment.name in outfit_in_words]
    print(f"Clothes suggested are {final_outfit_state}")
    final_outfit_state_numbers = [sum(garment_warmth)
                                  for garment_warmth in zip(*final_outfit_state)]
    print(
        f"Used {final_outfit_state_numbers}, instead of {original_outfit_in_numbers}")
    if sum(final_outfit_state_numbers) < sum(original_outfit_in_numbers):
        print("Looks like someone needs to go shopping")
    return outfit_in_words


if __name__ == "__main__":
    my_closet = Wardrobe()
    my_closet.generic_clothes_generator()
    outfit_in_numbers = [9, 10, 10, 11]
    outfit_in_words = translate_outfit(my_closet, outfit_in_numbers)
