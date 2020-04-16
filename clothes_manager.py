"""Classes for creating user's garments and closets."""

from dataclasses import dataclass


@dataclass
class Garment:
    """Garment class to represent a clothing item (e.g. jeans)"""

    def __init__(self, name: str, warmth: list) -> None:
        """initialize the garment with a name and warmth effect on the four parts of the body
        Arguments:
                name {str} - - name of garment
                warmth{list} --[
                                head {int} - - warmth effect on head (0 to 10),
                                top {int} - - warmth effect on top (0 to 10),
                                bottom {int} - - warmth effect on bottom (0 to 10),
                                feet {int} - - warmth effect on feet (0 to 10)
                                ]
        """
        self.name = name
        self.warmth = warmth

    def __hash__(self):
        return hash(tuple(self.warmth))


@dataclass
class Wardrobe:
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
        for index, item in enumerate(self.contents):
            if item.name == name:
                del self.contents[index]

    def generic_clothes_generator(self) -> None:
        """Generate a set of garments for the closet
        """
        self.contents.extend(
            [
                Garment("beanie", [2, 0, 0, 0]),
                Garment("pom pom hat", [3, 0, 0, 0]),
                Garment("trapper", [4, 0, 0, 0]),
                Garment("short sleeve shirt", [0, 2, 0, 0]),
                Garment("long sleeve shirt", [0, 3, 0, 0]),
                Garment("sweatshirt", [0, 4, 0, 0]),
                Garment("sweater", [1, 5, 0, 0]),
                Garment("winter jacket", [0, 6, 0, 0]),
                Garment("shorts", [0, 0, 1, 0]),
                Garment("cargo shorts", [0, 0, 2, 0]),
                Garment("sweatpants", [0, 0, 3, 0]),
                Garment("slacks", [0, 0, 4, 0]),
                Garment("jeans", [0, 0, 5, 0]),
                Garment("khakis", [0, 0, 6, 0]),
                Garment("cargo skiing pants", [0, 0, 7, 0]),
                Garment("slip-on", [0, 0, 0, 2]),
                Garment("sneakers", [0, 0, 0, 3]),
                Garment("casual shoes", [0, 0, 0, 4]),
                Garment("high-tops", [0, 0, 0, 5]),
                Garment("uggs", [0, 0, 0, 6]),
                Garment("boots", [0, 0, 0, 7]),
            ]
        )
