from . import ServiceUtils


class ApiUtils(ServiceUtils):
    """
    ApiUtils
    Pre-formatted documentation, default configuration, and sorting helpers.
    """

    def __init__(self) -> None:
        super().__init__()

        self.cols = """
             |         |          | Variable          | Definition
             |         |          | ------------------|----------------
             |         |          | page_id           | The unique identifier for that characters page within the wikia
             |         |          | name              | The name of the character
             |         |          | urlslug           | The unique url within the wikia that takes you to the character
             |         |          | id                | The identity status of the character (Secret Identity, Public identity, [on marvel only: No Dual Identity])
             |         |          | align             | If the character is Good, Bad or Neutral
             |         |          | eye               | Eye color of the character
             |         |          | hair              | Hair color of the character
             |         |          | sex               | Sex of the character (e.g. Male, Female, etc.)
             |         |          | gsm               | If the character is a gender or sexual minority (e.g. Homosexual characters, bisexual characters)
             |         |          | alive             | If the character is alive or deceased
             |         |          | appearances       | The number of appearances of the character in comic books *
             |         |          | first appearance  | The month and year of the character’s first appearance in a comic book, if available
             |         |          | year              | The year of the character’s first appearance in a comic book, if available
             |         |          |"""

        self.config = ""

        self.doc_params = {
            "marvel": {
                "display": "Marvel",
                "characters": ["iron man", "spider-man"],
                "search": ["spider", "man"],
                "exclude": "earth-616",
            },
            "dc": {
                "display": "DC",
                "characters": ["superman", "batman"],
                "search": ["bat", "man"],
                "exclude": "-woman",
            },
        }

        self.help_base = f"""
  format     | format  | json     | Output format (currently only JSON)
  headers    | h       | all      | Available Columns (page_id, name, urlslug, id, align, eye, hair, sex, gsm, alive, appearances, first appearance, year)
             |         |          | {self.cols}
  help       | help    | false    | Display Help
  limit      | limit   | 100      | Limit results ( 0 = unlimited)
  nulls      | nulls   | first    | null values sorted first or last e.g. [null, 1, 2, 3] or [1, 2, 3, null] †
  pretty     | pretty  | false    | Pretty print JSON results
  prune      | prune   | false    | Remove null values from output
  random     | random  | false    | Array of random characters based on limit
  sort       | s       | unsorted | Sort response asc|desc e.g. s=name,appearances:desc
  seed       | seed    | false    | Keep the same random characters on multiple requests


    * (as of Sep. 2, 2014. Number will become increasingly out of date as time goes on)
    † Does not apply when sorting on column/header which contains a null value, records with null values are removed
        """

    def help_search(self, universe: str) -> str:
        """
        Returns universe-specific examples/documentation.
        :param universe: "marvel" or "dc"
        """
        return f"""
  character  |         | empty    | Output format (currently only JSON)
             |         |          | {{keyword1}},{{keyword2}} e.g. {self.doc_params.get(universe)["characters"][0]},{self.doc_params.get(universe)["characters"][1]} will search for each character individually
             |         |          | {{keyword1}}+{{keyword2}} e.g. {self.doc_params.get(universe)["search"][0]}+{self.doc_params.get(universe)["search"][1]} will search for a character name with both '{self.doc_params.get(universe)["search"][0]}' AND '{self.doc_params.get(universe)["search"][1]}' in it
             |         |          | {{keyword1}},-{{keyword2}} e.g. {self.doc_params.get(universe)["characters"][0]},{self.doc_params.get(universe)["exclude"]} will search for character names containing '{self.doc_params.get(universe)["characters"][0]}' EXCLUDING results with {self.doc_params.get(universe)["exclude"]} in it
             |         |          |{self.help_base}
"""

    def handle_config(self, args: dict) -> dict:
        """
        Normalise the configuration dict used for retrieving data.
        :param args: Query-string or POST-body parameters.
        :return: Normalised configuration dictionary.
        """
        present = [True, "true", ""]
        config: dict = {"format": "json"}

        if args.get("characters") is not None:
            config.update({"characters": self.character_search_dict(args.get("characters"))})

        if args.get("h"):
            h_val: str | list = args.get("h")
            config.update({"h": h_val.split(",") if isinstance(h_val, str) else h_val})

        config.update({
            "help": args.get("help") in present,
            "limit": int(args.get("limit")) if (args.get("limit") or args.get("limit") == 0) else 100,
            "nulls": args.get("nulls") or "first",
            "pretty": args.get("pretty") in present,
            "prune": args.get("prune") in present,
            "universe": args.get("universe"),
        })

        if "random" in args:
            config.update({"random": args.get("random") in present})

        if args.get("s"):
            config.update({"s": self.sort_dict(args.get("s"))})

        if "seed" in args:
            config.update({"seed": args.get("seed") in present})

        self.config = config
        return config

    def character_search_dict(self, characters: str | list | dict) -> dict:
        """
        Break up a search pattern into a recognisable filter dictionary.
        e.g. ``spider+man`` or ``spider-man,-616``
        :param characters: Character search string.
        :return: Dict with keys ``some``, ``every``, and ``exclude``.
        """
        search_list = self.handle_param_types(characters)
        search = dict()
        search["some"] = list()
        search["every"] = list()
        search["exclude"] = list()
        for characters in list(search_list):
            if characters.startswith("-"):
                chars = self.permutate(characters.replace("-", ""))
                search["exclude"] = search["exclude"] + chars
            elif "+" in characters:
                chars = self.permutate(characters.split("+"))
                search["every"] = search["every"] + chars
            else:
                chars = self.permutate(characters)
                search["some"] = search["some"] + chars
        return search

    def show_help(self) -> str:
        """Return help text appropriate to the current config."""
        if not self.config.get("characters"):
            return self.help_base
        else:
            return self.help_search(self.config.get("universe"))



    def sort_dict(self, sort_str: str | list | dict) -> list:
        """
        Convert a specially formatted query param into a list of dicts.
        ``s=name,appearances:desc`` becomes
        [{
           "column": "name",
           "sort": False,
          }, {
           "column": "appearances",
           "sort": True,
        }]
        :param sort_str: (str) Representation of sort order
        :return: (list) of dict's representing a normalized column/header sort pattern
        """
        sort = list()
        sort_list = self.handle_param_types(sort_str)
        for i in list(sort_list):
            if isinstance(i, str) and ":" in i:
                slst = i.split(":")
                sort.append({"column": slst[0], "sort": self.direction(slst[1])})
            elif isinstance(i, dict) and i.get("sort"):
                i["sort"] = self.direction(i["sort"])
                sort.append(i)
            else:
                sort.append({"column": i, "sort": self.direction("asc")})
        return sort
