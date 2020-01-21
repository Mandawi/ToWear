'''
Translate outfit data to normal english
'''

# clothing item class which has a warmth points attirbute


class Garment():
    def __init__(self, name, head, top, bottom, feet, stackable):
        self.name = name
        self.warmth = [head, top, bottom, feet] # only one should be > 0, everything else is 0.
        self.stackable = bool(stackable)
    pass


class Wardrobe():
    def __init__(self):
        self.contents = list()

    def add_item(self, garment):
        self.contents.append(garment)

    def delete_by_name(self, name):
        for item in self.contents:
            if item.name == name:
                garment_to_delete = item
                self.contents.remove(garment_to_delete)

    def generic_clothes_generator(self):
        self.contents.extend([Garment("tank top", 0, 1, 0, 0, True),
                              Garment("short sleeve shirt", 0, 1, 0, 0, True),
                              Garment("long sleeve shirt", 0, 2, 0, 0, True),
                              Garment("sweatshirt", 0, 2, 0, 0, False),
                              Garment("sweater", 0, 3, 0, 0, False),
                              Garment("winter jacket", 0, 4, 0, 0, False),
                              Garment("winter coat", 0, 7, 0, 0, False),
                              Garment("beanie", 2, 0, 0, 0, False),
                              Garment("hat", 3, 0, 0, 0, False),
                              Garment("pom pom hat", 4, 0, 0, 0, False),
                              Garment("trapper hat", 6, 0, 0, 0, False),
                              Garment("shorts", 0, 0, 1, 0, False),
                              Garment("sweatpants", 0, 0, 3, 0, True),
                              Garment("jeans", 0, 0, 5, 0, False),
                              Garment("sneakers and light socks",
                                      0, 0, 0, 3, False),
                              Garment("winter boots and thick socks",
                                      0, 0, 0, 6, False)])

    def content_display(self):
        display_string = ["Name : Warmth : Stackable"]
        for item in self.contents:
            display_string.append(
                f"{item.name}: {item.warmth}: {item.stackable}")
        return display_string


def findMin(warmth_required, clothes_ihave: dict):
    # Inspired by https://medium.com/@emailarunkumar/coin-exchange-problem-greedy-or-dynamic-programming-6e5ebe5a30b5
    """Use a napasack solving algorithm to find

    Arguments:
        warmth_required {int} -- the needed warmth
        clothes_ihave {dict} -- the wardrobe contents as warmth[position]:garment dictionary

    Returns:
        list -- the outfit for this position
    """
    # BUG: Must reduce all positions when items that have effects on multiple positions like coat are chosen
    outfit = []
    warmths_sorted = sorted(clothes_ihave.keys())
    i = len(warmths_sorted)-1
    while (i > 0):
        unstackable_used = False
        while (warmth_required >= warmths_sorted[i] and unstackable_used == False):
            warmth_required = warmth_required - warmths_sorted[i]
            outfit.append(clothes_ihave[warmths_sorted[i]].name)
            if clothes_ihave[warmths_sorted[i]].stackable == False:
                unstackable_used = True
        i -= 1
    return outfit


def translate_outfit(wardrobe: Wardrobe, outfit_in_numbers: list):
    """get an outfit in numbers and translate it to a list of outfits in words

    Arguments:
        outfit_in_numbers {[type]} -- [description]
    """
    outfit_in_words = [[] for _ in outfit_in_numbers]
    for position, outfit_element in enumerate(outfit_in_numbers):
        # outfit_element_options = []
        if outfit_element == 0:
            outfit_in_words[position].append("nothing")
        elif len(wardrobe.contents) > 0:
            wardrobe_by_element = {
                garment.warmth[position]: garment for garment in wardrobe.contents}
            outfit_in_words[position].extend(
                findMin(outfit_element, wardrobe_by_element))
    return outfit_in_words
