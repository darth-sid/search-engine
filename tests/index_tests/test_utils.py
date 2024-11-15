import unittest
import indexer.utils as util

class TestTokenize(unittest.TestCase):
    def test_tokenize_basic(self):
        text = "I can see deer near the water"
        self.assertEqual(list(util.tokenize(text,stem=False)), text.lower().split())

    def test_tokenize_with_num(self):
        text = "There are 12 apples at the table"
        self.assertEqual(list(util.tokenize(text,stem=False)), text.lower().split())

    def test_tokenize_with_alnum(self):
        text = "The product code AB123 is unique"
        self.assertEqual(list(util.tokenize(text,stem=False)), text.lower().split())

    def test_tokenize_with_stemming(self):
        text = "The runners completed two 5K races last weekend"
        text2 = "The runner completes two 5K races last weekend"
        self.assertEqual(list(util.tokenize(text)), list(util.tokenize(text2)))

    def test_tokenize_with_symbols(self):
        text = "The price of the item is $45!"
        self.assertEqual(list(util.tokenize(text, stem=False)), text.lower().split()[:-1] + ["45"])

    def test_tokenize_with_nonenglish(self):
        text = "I love 吃蛋糕 and coffee."
        self.assertEqual(list(util.tokenize(text,stem=False)), ["i", "love", "and", "coffee"])
    
    def test_tokenize_on_whitespace(self):
        text = "        "
        self.assertEqual(len(list(util.tokenize(text))), 0)

    def test_tokenize_complex(self):
        text = "She completed 5 tasks & 3 assignments successfully"
        text2 = "She completes 5 task & 3 assignment successful"
        self.assertEqual(list(util.tokenize(text)), list(util.tokenize(text2)))
    
    def test_stem(self):
        self.assertEqual(util.stem_word("hammers"), util.stem_word("hammering"))
        self.assertNotEqual(util.stem_word("runner"), util.stem_word("running"))
        self.assertNotEqual(util.stem_word("revisited"), util.stem_word("visiting"))
