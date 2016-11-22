from rets.interpreters.search import Search
from rets.exceptions import InvalidSearch
import unittest
import datetime
from collections import OrderedDict


class SearchTester(unittest.TestCase):
    """
    OrderedDict is used with multiple keys in the tests to ensure consistent expected expression results
    """

    def test_float(self):
        search_interpreter = Search()
        dict1 = OrderedDict()
        dict1["ListPrice"] = {"$gte": 150000}
        dict1["Status"] = "A"
        expected1 = '(ListPrice=150000.00+),(Status=A)'
        result = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual(expected1, result)

    def test_invalid_operator(self):
        search_operator = Search()
        dict1 = {"Status": {"$not": "this does not work"}}
        with self.assertRaises(InvalidSearch):
            search_operator.filter_to_dmql(filter_dict=dict1)

    def test_key_count(self):
        search_operator = Search()
        dict1 = {"ListingPrice": {"$gte": 100000, "$lte": 200000}}
        search_operator.filter_to_dmql(filter_dict=dict1)

        dict2 = {"ListingPrice": {"$gte": 100000, "$contains": 200000}}
        with self.assertRaises(InvalidSearch):
            search_operator.filter_to_dmql(filter_dict=dict2)

        dict3 = {"ListingPrice": {"$gte": 100000, "$lte": 200000, "$neq": 150000}}
        with self.assertRaises(InvalidSearch):
            search_operator.filter_to_dmql(filter_dict=dict3)

    def test_inbetween(self):
        search_interpreter = Search()
        dict1 = {"Status": {"$gte": "A"}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict1)

        dict2 = {"Status": {"$lte": "A"}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

        dict3 = {"Status": {"$gte": "A", "$lte": "P"}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict3)

        dict4 = {"ListingPrice": {"$gte": 100, "$lte": 200}}
        res4 = search_interpreter.filter_to_dmql(filter_dict=dict4)
        self.assertEqual(res4, '(ListingPrice=100.00-200.00)')

        dict5 = {"CreatedDate": {"$gte": datetime.datetime(2016, 11, 22, 15, 22, 00),
                                 "$lte": datetime.datetime(2016, 11, 22, 15, 23, 00)}}
        res5 = search_interpreter.filter_to_dmql(filter_dict=dict5)
        self.assertEqual(res5, '(CreatedDate=2016-11-22T15:22:00-2016-11-22T15:23:00)')

    def test_gte(self):
        search_interpreter = Search()
        dict1 = {"ListPrice": {"$gte": 100}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual(res1, '(ListPrice=100.00+)')

        dict2 = {"ListPrice": {"$gte": 100.000}}
        res2 = search_interpreter.filter_to_dmql(filter_dict=dict2)
        self.assertEqual(res2, '(ListPrice=100.00+)')

        dict3 = {"ListPrice": {"$gte": 'A'}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict3)

        dict4 = {"CreatedDate": {"$gte": datetime.datetime(2016, 11, 22, 15, 22, 00)}}
        res4 = search_interpreter.filter_to_dmql(filter_dict=dict4)
        self.assertEqual('(CreatedDate=2016-11-22T15:22:00+)', res4)

    def test_lte(self):
        search_interpreter = Search()
        dict1 = {"ListPrice": {"$lte": 100}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual(res1, '(ListPrice=100.00-)')

        dict2 = {"ListPrice": {"$lte": 100.000}}
        res2 = search_interpreter.filter_to_dmql(filter_dict=dict2)
        self.assertEqual(res2, '(ListPrice=100.00-)')

        dict3 = {"ListPrice": {"$lte": 'A'}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict3)

        dict4 = {"CreatedDate": {"$lte": datetime.datetime(2016, 11, 22, 15, 22, 00)}}
        res4 = search_interpreter.filter_to_dmql(filter_dict=dict4)
        self.assertEqual('(CreatedDate=2016-11-22T15:22:00-)', res4)

    def test_in(self):
        search_interpreter = Search()
        dict1 = {"Status": {"$in": ['Active', 'Pending', 'Sold']}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(Status=Active,Pending,Sold)', res1)

        dict2 = {"ListingPrice": {"$in": [120000, 1201000]}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

        dict3 = {"Status": {"$in": "Active"}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict3)

    def test_nin(self):
        search_interpreter = Search()
        dict1 = {"Status": {"$nin": ['Pending', 'Sold']}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(Status=~Pending,Sold)', res1)

        dict2 = {"ListingPrice": {"$nin": [120000, 1201000]}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

        dict3 = {"Status": {"$nin": "Active"}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict3)

    def test_contains(self):
        search_interpreter = Search()
        dict1 = {"FullAddress": {'$contains': "main"}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(FullAddress=*main*)', res1)

        dict2 = {"FullAddress": {'$contains': 100}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

    def test_begins(self):
        search_interpreter = Search()
        dict1 = {"FullAddress": {'$begins': "main"}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(FullAddress=main*)', res1)

        dict2 = {"FullAddress": {'$begins': 100}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

    def test_ends(self):
        search_interpreter = Search()
        dict1 = {"FullAddress": {'$ends': "main"}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(FullAddress=*main)', res1)

        dict2 = {"FullAddress": {'$ends': 100}}
        with self.assertRaises(InvalidSearch):
            search_interpreter.filter_to_dmql(filter_dict=dict2)

    def test_neq(self):
        search_interpreter = Search()
        dict1 = {"Baths": {'$neq': 2}}
        res1 = search_interpreter.filter_to_dmql(filter_dict=dict1)
        self.assertEqual('(Baths=~2)', res1)