from mcnpy.data_cards.data_card import DataCardAbstract
from mcnpy.particle import Particle


class Mode(DataCardAbstract):
    """
    Class for the particle mode for a problem.
    """

    def __init__(self, input_card=None, comments=None):
        """
        :param input_card: the Card object representing this data card
        :type input_card: Card
        :param comments: The Comment that may proceed this
        :type comments: Comment
        """
        super().__init__(input_card, comments)
        if input_card:
            self._particles = set()
            for particle in self.words[1:]:
                self._particles.add(Particle(particle.upper()))
        else:
            self._particles = {Particle.NEUTRON}

    @property
    def particles(self):
        """
        The type of particles involved in this problem.

        :rtype: set
        """
        return self._particles.copy()

    def add(self, particle):
        """
        Adds the given particle to the problem.

        """
        if not isinstance(particle, (Particle, str)):
            raise TypeError("particle must be a Particle instance")
        if isinstance(particle, str):
            # error catching not needed
            # enum will raise ValueError "foo is not a valid Particle"
            particle = Particle(particle.upper())
        self._mutated = True
        self._particles.add(particle)

    def remove(self, particle):
        """
        Remove the given particle from the problem
        """
        if not isinstance(particle, (Particle, str)):
            raise TypeError("particle must be a Particle instance")
        if isinstance(particle, str):
            particle = Particle(particle.upper())
        self._mutated = True
        self._particles.remove(particle)

    def __contains__(self, obj):
        return obj in self._particles

    def __iter__(self):
        return iter(self._particles)

    def __len__(self):
        return len(self._particles)

    @property
    def class_prefix(self):
        return "mode"

    @property
    def has_number(self):
        return False

    @property
    def has_classifier(self):
        return 0

    def format_for_mcnp_input(self, mcnp_version):
        if self.mutated:
            words = ["MODE"]
            for particle in self.particles:
                words.append(particle.value)
            self.words = words
            ret = super().format_for_mcnp_input(mcnp_version)
        else:
            ret = self._format_for_mcnp_unmutated(mcnp_version)

        return ret
