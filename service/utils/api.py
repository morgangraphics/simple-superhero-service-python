from . import ServiceUtils


class ApiUtils(ServiceUtils):
    def __init__(self):
        """
        Inheritance here is probably not needed but done for testing out the idea
        """
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

    def help_search(self, universe):
        """
        Returns Universe specific examples/documentation based on param
        :param universe: (str) Marvel/DC
        :return:
        """
        return f"""
  character  |         | empty    | Output format (currently only JSON)
             |         |          | {{keyword1}},{{keyword2}} e.g. {self.doc_params.get(universe)["characters"][0]},{self.doc_params.get(universe)["characters"][1]} will search for each character individually
             |         |          | {{keyword1}}+{{keyword2}} e.g. {self.doc_params.get(universe)["search"][0]}+{self.doc_params.get(universe)["search"][1]} will search for a character name with both '{self.doc_params.get(universe)["search"][0]}' AND '{self.doc_params.get(universe)["search"][1]}' in it
             |         |          | {{keyword1}},-{{keyword2}} e.g. {self.doc_params.get(universe)["characters"][0]},{self.doc_params.get(universe)["exclude"]} will search for character names containing '{self.doc_params.get(universe)["characters"][0]}' EXCLUDING results with {self.doc_params.get(universe)["exclude"]} in it
             |         |          |{self.help_base}
"""

    def handle_config(self, args):
        """
        Normalize configuration dict used for retrieving data
        :param args: (dict) of arguments passed in via GET Querystring, or POST JSON
        :return: (dict) Normalized configuration dictionary
        """
        config = dict()
        present = [True, "true", ""]

        if args.get("characters") is not None:
            config["characters"] = self.character_search_dict(args.get("characters"))

        config["format"] = "json"

        if args.get("h"):
            val = ""
            if isinstance(args.get("h"), str):
                val = args.get("h").split(",")
            if isinstance(args.get("h"), list):
                val = args.get("h")
            config["h"] = val

        config["help"] = True if (args.get("help") in present) else False

        config["limit"] = (
            int(args.get("limit"))
            if args.get("limit") or args.get("limit") == 0
            else 100
        )

        config["nulls"] = args.get("nulls") if args.get("nulls") else "first"

        config["pretty"] = True if (args.get("pretty") in present) else False

        config["prune"] = True if (args.get("prune") in present) else False

        if "random" in args:
            config["random"] = True if (args.get("random") in present) else False

        if args.get("s"):
            config["s"] = self.sort_dict(args.get("s"))

        if "seed" in args:
            config["seed"] = True if (args.get("seed") in present) else False

        config["universe"] = args.get("universe")

        self.config = config

        return config

    def character_search_dict(self, characters):
        """
        Breaks up Search pattern into recognizable search filter dictionary to processing during filtering stage
        e.g. spider+man or spider-man,-616
        :param characters: (str) Character Search String
        :return: (dict) list of search options
        """
        search_list = self.handle_param_types(characters)
        search = dict()
        search["some"] = list()
        search["every"] = list()
        search["exclude"] = list()
        for characters in search_list:
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

    def show_help(self):
        """
        Helper method to display help text
        :return: (text) Text based help
        """
        if not self.config.get("characters"):
            return self.help_base
        else:
            return self.help_search(self.config.get("universe"))



    def sort_dict(self, sort_str):
        """
        Method converts a specially formatted query param into a list of dictionaries
        s=name,appearances:desc becomes
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
        for i in sort_list:
            if isinstance(i, str) and ":" in i:
                slst = i.split(":")
                sort.append({"column": slst[0], "sort": self.direction(slst[1])})
            elif isinstance(i, dict) and i.get("sort"):
                i["sort"] = self.direction(i["sort"])
                sort.append(i)
            else:
                sort.append({"column": i, "sort": self.direction("asc")})
        return sort
