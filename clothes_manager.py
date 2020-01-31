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
        self.contents.extend([Garment("short sleeve shirt",
                                      0, 2, 0, 0),
                              Garment("long sleeve shirt",
                                      0, 3, 0, 0),
                              Garment("sweatshirt",
                                      0, 3, 0, 0),
                              Garment("sweater",
                                      0, 3, 0, 0),
                              Garment("winter jacket",
                                      0, 4, 0, 0),
                              Garment("winter coat",
                                      1, 5, 2, 0),
                              Garment("beanie",
                                      2, 0, 0, 0),
                              Garment("hat",
                                      3, 0, 0, 0),
                              Garment("pom pom hat",
                                      4, 0, 0, 0),
                              Garment("shorts",
                                      0, 0, 3, 0),
                              Garment("sweatpants",
                                      0, 0, 4, 0),
                              Garment("jeans",
                                      0, 0, 6, 0),
                              Garment("light socks",
                                      0, 0, 0, 1),
                              Garment("sneakers",
                                      0, 0, 0, 3),
                              Garment("thick socks",
                                      0, 0, 0, 2),
                              Garment("casual shoes",
                                      0, 0, 0, 4)])
