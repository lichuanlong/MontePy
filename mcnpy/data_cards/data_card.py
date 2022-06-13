from mcnpy.errors import *
from mcnpy.mcnp_card import MCNP_Card


class DataCard(MCNP_Card):
    """
    Parent class to describe all MCNP data inputs.
    """

    def __init__(self, input_card=None, comment=None):
        """
        :param input_card: the Card object representing this data card
        :type input_card: Card
        :param comment: The Comment that may proceed this
        :type comment: Comment
        """
        super().__init__(input_card, comment)
        if input_card:
            self._words = input_card.words
            self.__split_name()
        else:
            self._words = []

    @property
    def words(self):
        """
        The words of the data card, not parsed.

        :rtype: list
        """
        return self._words

    @words.setter
    def words(self, words):
        assert isinstance(words, list)
        for word in words:
            assert isinstance(word, str)
        self._mutated = True
        self._words = words

    @property
    def prefix(self):
        """The text part of the card identifier.

        For example: for a material like: m20 the prefix is 'm'

        this will always be lower case
        """
        return self._prefix.lower()

    @property
    def particle_classifier(self):
        """The particle class part of the card identifier.

        For example: the classifier for `F7:n` is `:n`, and `imp:n,p` is `:n,p`
        """
        return self._classifier.lower()

    def format_for_mcnp_input(self, mcnp_version):
        ret = super().format_for_mcnp_input(mcnp_version)
        if self.mutated:
            ret += DataCard.wrap_words_for_mcnp(self.words, mcnp_version, True)
        else:
            ret = self._format_for_mcnp_unmutated(mcnp_version)
        return ret

    def update_pointers(self, data_cards):
        """
        Connects data cards to each other

        :param data_cards: a list of the data cards in the problem
        :type data_cards: list
        """
        pass

    def __str__(self):
        return f"DATA CARD: {self._words}"

    def __split_name(self):
        name = self._words[0]
        prefix_extras = ["*"]
        number_extras = ["-"]
        classifier_extras = [":",","]
        is_digit = [(c.isdigit() or c in number_extras or c in classifier_extras) for c in name]
        classifier = None
        if True in is_digit:
            i = is_digit.index(True)
            prefix, number = name[:i], name[i:]
        else:
            prefix = name
            number = None
        assert all(c.isalpha() or c in prefix_extras for c in prefix)
        if number:
            is_classifier = [(c.isalpha() or c in classifier_extras) for c in number]
            if True in is_classifier:
                i = is_classifier.index(True)
                number, classifier = number[:i],name[i:]
            if number:
                assert all(c.isdigit() or c in number_extras for c in number)
                self._input_number = int(number)
        self._prefix = prefix
        self._classifier = classifier

    def __lt__(self, other):
        type_comp = self.prefix < other.prefix
        if type_comp:
            return type_comp
        elif self.prefix > other.prefix:
            return type_comp
        else:  # otherwise first part is equal
            return self._input_number < other._input_number
