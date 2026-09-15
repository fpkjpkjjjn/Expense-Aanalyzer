import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from categorizer import categorize


class CategorizerTests(unittest.TestCase):
    def test_slovak_groceries(self):
        cases = [
            "Kaufland Košice",
            "Lidl Košice",
            "BILLA",
            "Tesco Stores",
            "COOP Jednota",
            "Fresh Košice",
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assertEqual(categorize(value), "Groceries")

    def test_drugstores_and_health(self):
        for value in ("dm drogerie markt", "DM Kosice"):
            with self.subTest(value=value):
                self.assertEqual(categorize(value), "Health")
        self.assertEqual(categorize("Dr.Max"), "Health")
        self.assertEqual(categorize("lekáreň"), "Health")

    def test_transport_and_food_delivery(self):
        for value in ("DPMK a.s.", "MHD Košice", "Bolt", "Uber4 Trip"):
            with self.subTest(value=value):
                self.assertEqual(categorize(value), "Transport")

        for value in ("Foodora", "Wolt", "Bolt Food"):
            with self.subTest(value=value):
                self.assertEqual(categorize(value), "Dining")

    def test_fuel(self):
        for value in ("Slovnaft", "OMV", "Shell", "benzín", "čerpacia stanica"):
            with self.subTest(value=value):
                self.assertEqual(categorize(value), "Fuel")

    def test_no_diacritic_variants(self):
        self.assertEqual(categorize("lekaren"), "Health")
        self.assertEqual(categorize("elektricka Kosice"), "Transport")
        self.assertEqual(categorize("cerpacia stanica"), "Fuel")

    def test_existing_categories(self):
        self.assertEqual(categorize("Pyaterochka Moscow"), "Groceries")
        self.assertEqual(categorize("Yandex Taxi"), "Transport")
        self.assertEqual(categorize("Spotify Premium"), "Subscriptions")
        self.assertEqual(categorize("Random payment XYZ"), "Other")


if __name__ == "__main__":
    unittest.main()
