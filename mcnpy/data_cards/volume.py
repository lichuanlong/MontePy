from mcnpy.data_cards.cell_modifier import CellModifierCard
from mcnpy.errors import *
from mcnpy.input_parser.mcnp_input import Jump


# TODO: handle defaults!


class Volume(CellModifierCard):
    """
    Class for the data input that modifies cell volumes; ``VOL``.
    """

    def __init__(
        self, input_card=None, comments=None, in_cell_block=False, key=None, value=None
    ):
        super().__init__(input_card, comments, in_cell_block, key, value)
        self._volume = None
        self._calc_by_mcnp = True
        if self.in_cell_block:
            if key:
                try:
                    value = float(value)
                    assert value >= 0.0
                except (ValueError, AssertionError) as e:
                    raise ValueError(
                        f"Cell volume must be a number ≥ 0.0. {value} was given"
                    )
                self._volume = value
                self._calc_by_mcnp = False
        elif input_card:
            self._volume = []
            words = self.words[1:]
            if self.words[1].lower() == "no":
                self.calc_by_mcnp = False
                words = self.words[2:]
            for word in words:
                if isinstance(word, str):
                    try:
                        value = float(word)
                        assert value >= 0
                        self._volume.append(value)
                    except (ValueError, AssertionError) as e:
                        raise MalformedInputError(
                            input_card, f"Cell volumes by a number ≥ 0.0: {word} given"
                        )
                elif isinstance(word, Jump):
                    self._volume.append(word)
                else:
                    raise TypeError(
                        f"Word: {word} cannot be parsed as a volume as a str, or Jump"
                    )

    @property
    def class_prefix(self):
        return "vol"

    @property
    def has_number(self):
        return False

    @property
    def has_classifier(self):
        return 0

    @property
    def volume(self):
        if self.in_cell_block:
            return self._volume

    @volume.setter
    def volume(self, value):
        if not isinstance(value, float):
            raise TypeError("Volume must be set to a float")
        if value < 0.0:
            raise ValueError("Volume must be set to a number ≥ 0")
        self._volume = volume
        self._mutated = True

    @volume.deleter
    def volume(self):
        self._volume = None
        self._mutated = True

    @property
    def is_mcnp_calculated(self):
        """"""
        if self._problem and self.in_cell_block:
            # TODO need nice way to interact with "NO" as user
            if not self._problem.cells._volume.is_mcnp_calculated:
                return False
        return self._calc_by_mcnp

    @property
    def set(self):
        """
        If this volume is set.
        """
        if self._volume is not None:
            return True

    def merge(self, other):
        raise MalformedInputError(
            other, "Cannot have two volume inputs for the problem"
        )

    def push_to_cells(self):
        if not self.in_cell_block and self._problem and self._volume:
            cells = self._problem.cells
            for i, cell in enumerate(cells):
                vol = self._volume[i]
                if cell._volume.set_in_cell_block:
                    raise MalformedInputError(
                        self,
                        f"Cell: {cell.number} provided IMP data when those data were in the data block",
                    )
                if not isinstance(vol, Jump):
                    cell.volume = vol

    def _clear_data(self):
        del self._volume

    def format_for_mcnp_input(self, mcnp_version):
        ret = []
        if self.in_cell_block:
            if self._volume:
                ret.extend(self.wrap_string_for_mcnp(f"VOL={self.volume}", mcnp_version, False))
        else:
            mutated = self.mutated
            if not mutated:
                mutated = self.has_changed_print_style
                for cell in self._problem.cells:
                    if cell._volume.mutated:
                        mutated = True
                        break
        return ret
