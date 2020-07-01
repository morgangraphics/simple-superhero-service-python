import csv
import locale
import random
from operator import itemgetter
from pathlib import Path

locale.setlocale(locale.LC_ALL, "en_US.utf8")


class ReadFile:
    def __init__(self, cfg):
        self.character_sets = {
            "dc": "dc-wikia-data_csv.csv",
            "marvel": "marvel-wikia-data_csv.csv",
        }
        self.config = cfg
        self.limit_buffer = 200
        self.seed = 888222
        self.total_data = 0
        self.universe = cfg.get("universe")

    def filter_characters(self, data):
        """
         s = ['superman', 'super man', 'super-man'] (some)
         e = ['super', 'man']   (all/every)
         If len(s) > 0 and item.get("name") includes ANY entry in s
         OR
         If len(e) > 0 and item.get("name") includes ALL entries in e
         AND
         Doesn't contain any exclusions add to search array
        :param data:
        :return:
        """
        data_in_play = list()
        s = self.config["characters"].get("some")
        e = self.config["characters"].get("every")
        x = self.config["characters"].get("exclude")

        for character in data:
            if (
                (len(s) > 0 and any(item in character.get("name") for item in s))
                or (len(e) > 0 and all(item in character.get("name") for item in e))
            ) and not any(item in character.get("name") for item in x):
                data_in_play.append(character)

        return data_in_play

    def filter_data(self, data):
        """
        Filter data set based on params
        :param data: (list) List of "fixed" data meaning Type coercions, unicode decoding etc
        :return: (list) of filtered results
        """

        # Seeding ensures we have the same data set on each request
        if self.config.get("seed"):
            random.seed(self.seed)

        # CHARACTERS
        if self.config.get("characters"):
            data_in_play = self.filter_characters(data)
        else:
            data_in_play = data

        # LIMITING
        results = self.filter_limit(data_in_play)

        # SORTING - Custom Locale Aware sorting function
        if self.config.get("s"):
            results = self.sort_results(results)

        return results

    def filter_limit(self, data):
        """
        Filter data based on Limits
        :param data: (list) List of Filtered Character data
        :return:
        """
        data_in_play = list()
        limit = 0

        # override default if condition is met
        if self.config.get("limit") and self.config.get("limit") != 0:
            limit = self.config.get("limit")

        # buffr is an attempt help Python reduce the number of overlaps on multiple requests by generating
        # a unique list form a larger pool of numbers
        if limit > 0 and self.config.get("random"):
            buffr = (
                limit
                if (limit + self.limit_buffer >= self.total_data)
                else (limit + self.limit_buffer)
            )
            uniques = random.sample(range(0, len(data)), buffr)
            for i in uniques[0:limit]:
                data_in_play.append(data[i])
        if limit > 0 and not self.config.get("random"):
            data_in_play = data[0:limit]
        if limit == 0:
            data_in_play = data

        return data_in_play

    def get_data(self):
        """
        This method will open the correct file and
        1. Coerce data types to the correct type
        2. Strip out the double // in the Name and UrlSlug columns
        3. Decode Unicode escaped/encoded values e.g. \u00c4kr\u00e4s to Äkräs
        4. Coerce empty values "" to None (which translates to null) when JSON encoded
        5. Optional: Show only the Columns/Headers Requested
        6. Optional: Prune all None(null) values
        7. Ensure that row is removed if sorting and prune are defined and sorting key is null
        8. Pass to Filter function which will data set based on parameters passed in
        :return: (list) List of dictionaries of Characters which meet the requirements
        """
        type_map = {"page_id": int, "appearances": int, "year": int}

        # page_id, name, urlslug, id, align, eye, hair, sex, gsm, alive, appearances, first appearance, year
        try:
            file_path = (
                Path(__file__).parent.parent
                / "files"
                / self.character_sets.get(self.universe)
            )

            with open(file_path, newline="") as file:
                dl = list()
                for row in csv.DictReader(file):
                    rl = dict()
                    for key, value in list(row.items()):

                        # CSV file doesn't coerce values by default. We update the row directly for later processing
                        if key in type_map and value:
                            row.update({key: type_map[key](value)})

                        # clean up escaped values
                        if key in ["name", "urlslug"] and '"' in value or "/" in value:
                            row.update({key: value.replace("\\", "")})

                        # this will take a unicode_escaped string e.g. \u00c4kr\u00e4s and
                        # convert it to the proper encoding e.g. Äkräs
                        if key in ["name"] and "\\u" in value:
                            row.update(
                                {
                                    key: value.replace("\\/", "/")
                                    .encode()
                                    .decode("unicode_escape")
                                    .lower()
                                }
                            )

                        # json.dumps will output empty values in the JSON (which is technically incorrect) { "a": "" }
                        # so we force empty values to None so they will appear as null
                        # in the end JSON output { "a": null }
                        if not value:
                            row.update({key: None})

                        # pull out requested csv headers if header is requested and header exists or add all the headers
                        if (self.config.get("h") and key in self.config.get("h")) or (
                            not self.config.get("h")
                        ):
                            rl[key] = row[key]

                        # if prune is set, remove any columns with a value of None
                        if self.config.get("prune") and row[key] is None and key in rl:
                            del rl[key]

                    # if prune is set and we are sorting, we have to ensure the rows have all the columns to sort on
                    if self.config.get("prune") and self.config.get("s"):
                        cur_kz = list(rl.keys())
                        srt_on = list(map(itemgetter("column"), self.config.get("s")))
                        if all(item in cur_kz for item in srt_on):
                            dl.append(rl)
                    else:
                        dl.append(rl)

                self.total_data = len(dl)

        except TypeError:
            raise TypeError("Invalid Universe File")

        return self.filter_data(dl)

    def sort_results(self, results, srt_ordr=None):
        """
        Custom sorting function that allows for sorting None while also maintaining locale aware sorting
        config["nulls"] will allow for sorting None and putting them at the front or end of the list

        l = [1, 3, 2, 5, 4, None, 7]
        print('Last = ', sorted(l, key=lambda x: (x is None, x)))
        Last = [1, 2, 3, 4, 5, 7, None]
        print('First = ', sorted(l, key=lambda x: (x is not None, x)))
        First = [None, 1, 2, 3, 4, 5, 7]

        :param results: (list) e.g. [{'name': 'richard jones (earth-616)', 'appearances': 590, 'year': 1962}]
        :param srt_ordr: (dict) e.g. {'column': 'name', 'sort': False}
        :return: (tuple) e.g. (False, True, 1969) tuples are sorted by item type, this means that all non-None elements
        will come first (since False < True), and then be sorted by value.
        """
        srt_dict = srt_ordr if srt_ordr is not None else self.config.get("s")

        for i in reversed(srt_dict):
            results.sort(key=lambda itm: self.sort_i18n_str(itm, i), reverse=i["sort"])

        return results

    def sort_i18n_str(self, row, direction):
        """
        in the direction list - sort = True|False is referring to reverse in the python sort method
        :param row: (dict) dictionary with keys sort on
        :param direction: (dict) sort list e.g. [{'column': 'eye', 'sort': False}]
        :return:
        """
        itm = row[direction["column"]]

        if itm is not None and isinstance(itm, str):
            itm = locale.strxfrm(row[direction["column"]])

        # Sorting None must also survive sort direction (asc|desc) or reverse=True|False
        if self.config.get("nulls") == "first" and not self.config.get("prune"):
            # if sort = False (meaning reverse=False meaning sort = ASC = A => Z)
            if not direction["sort"]:
                srt_tpl = (itm is not None, itm != "", itm)
            else:
                srt_tpl = (itm is None, itm != "", itm)
        else:
            if not direction["sort"]:
                srt_tpl = (itm is None, itm != "", itm)
            else:
                srt_tpl = (itm is not None, itm != "", itm)

        return srt_tpl
