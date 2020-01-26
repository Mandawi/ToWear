class Garment():
    """Garment class to represent a clothing item (e.g. jeans)"""

    def __init__(self, name: str, head: int, top: int, bottom: int, feet: int) -> None:
        """initialize the garment with a name and warmth effect on the four parts of the body
        Arguments:
            name {str} - - name of garment
            head {int} - - warmth effect on head (0 to 10)
            top {int} - - warmth effect on top (0 to 10)
            bottom {int} - - warmth effect on bottom (0 to 10)
            feet {int} - - warmth effect on feet (0 to 10)
        """
        # FIXME: Garment must have an affect on one and only one part of the body
        self.name = name
        self.warmth = [head, top, bottom, feet]
    pass


class Wardrobe():
    """Wardrobe class to represent a user's closet"""

    def __init__(self) -> None:
        self.contents = list()

    def add_item(self, garment: Garment) -> None:
        """add an item to the closet

        Arguments:
            garment {Garment} -- the garment to be added
        """
        self.contents.append(garment)

    def change_warmth(self, name: str, warmth: list) -> None:
        """change an item's warmth

        Arguments:
            name {str} -- the name of the item whose warmth will change
            warmth {list} -- the new warmth
        """
        for item in self.contents:
            if item.name == name:
                garment_to_change = item
                garment_to_change.warmth = warmth

    def delete_by_name(self, name: str) -> None:
        """delete an item using its name

        Arguments:
            name {str} -- the name of the item to be deleted
        """
        for item in self.contents:
            if item.name == name:
                garment_to_delete = item
                self.contents.remove(garment_to_delete)

    def generic_clothes_generator(self) -> None:
        """Generate a set of garments for the closet
        """
        self.contents.extend([Garment("tank top", 0, 1, 0, 0),
                              Garment("short sleeve shirt", 0, 1, 0, 0),
                              Garment("long sleeve shirt", 0, 2, 0, 0),
                              Garment("sweatshirt", 0, 2, 0, 0),
                              Garment("sweater", 0, 3, 0, 0),
                              Garment("winter jacket", 0, 4, 0, 0),
                              Garment("winter coat", 0, 7, 0, 0),
                              Garment("beanie", 2, 0, 0, 0),
                              Garment("hat", 3, 0, 0, 0),
                              Garment("pom pom hat", 4, 0, 0, 0),
                              Garment("trapper hat", 6, 0, 0, 0),
                              Garment("shorts", 0, 0, 1, 0),
                              Garment("sweatpants", 0, 0, 3, 0),
                              Garment("jeans", 0, 0, 5, 0),
                              Garment("sneakers and light socks",
                                      0, 0, 0, 3),
                              Garment("winter boots and thick socks",
                                      0, 0, 0, 6)])


def findMin(warmth_required: int, clothes_ihave: dict) -> list:
    # Inspired by https://medium.com/@emailarunkumar/coin-exchange-problem-greedy-or-dynamic-programming-6e5ebe5a30b5
    """Use a napasack solving algorithm to find clothes needed to achieve the desired temperature

    Arguments:
        warmth_required {int} - - the needed warmth
        clothes_ihave {dict} - - the wardrobe contents as {warmth[position]: garment} dictionary

    Returns:
        list - - the outfit for this position
    """
    # outfit is a list of lists of Garments for each part of the body
    outfit = []
    warmths_sorted = sorted(clothes_ihave.keys())
    i = len(warmths_sorted)-1
    while (i > 0):
        # FIXME: Must reduce all positions when items that have effects on multiple positions like coat are chosen
        while (warmth_required >= warmths_sorted[i]):
            warmth_required = warmth_required - warmths_sorted[i]
            outfit.append(clothes_ihave[warmths_sorted[i]].name)
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
