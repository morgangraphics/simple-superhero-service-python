import re


class ServiceUtils:
    """
    ServiceUtils
    Sorting direction helper, param-type normalisation, name permutations.
    """

    def __init__(self) -> None:
        return

    @staticmethod
    def direction(val: str) -> bool:
        """
        Internal Method that determines sort direction reverse=False|True

        :param val: asc or dsc
        :return: Boolean
        """
        return val != "asc"

    @staticmethod
    def handle_param_types(param: str | list | dict) -> list:
        """
       Parameters can come in several different formats. This private method tests for the
       format and prepares it accordingly

        :param param: (str|list|dict}
        :return: (list)
        """
        response = ""
        if isinstance(param, str):
            response = param.split(",")
        if isinstance(param, list):
            response = param
        if isinstance(param, dict):
            response = [param]
        return response

    @staticmethod
    def permutate(names: str | list) -> list:
        """
        Will attempt to make permutations on names passed in so empty result sets are limited
        e.g. spider man, spider-man, spiderman

        :param names: (str) Character names
        :return: (list) List of character name permutations
        """
        options = list()
        characters = [names]

        if isinstance(names, list):
            characters = map(str.strip, names)

        for character in characters:
            if character not in options:
                options.append(character)

            if " " in character:
                options.append(character.replace(" ", "-"))

            if "-" in character:
                options.append(character.replace("-", " "))

            if re.search(r"[\s-]", character):
                options.append(re.sub(r"[\s-]", "", character))

        return options
