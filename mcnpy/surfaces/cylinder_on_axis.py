from .surface_type import SurfaceType
from .surface import Surface
from mcnpy.errors import *


class CylinderOnAxis(Surface):
    """
    Represents surfaces: CX, CY, CZ
    """

    def __init__(self, input_card, comment=None):
        """
        :param input_card: The Card object representing the input
        :type input_card: Card
        :param comment: the Comment object representing the
                        preceding comment block.
        :type comment: Comment
        """
        super().__init__(input_card, comment)
        ST = SurfaceType
        if self.surface_type not in [ST.CX, ST.CY, ST.CZ]:
            raise ValueError("CylinderOnAxis must be of surface_type: CX, CY, CZ")
        if len(self.surface_constants) != 1:
            raise ValueError("CylinderOnAxis only accepts one surface_constant")
        self._radius = self.surface_constants[0]

    @property
    def radius(self):
        """
        The radius of the cylinder
        """
        return self._radius

    @radius.setter
    def radius(self, radius):
        if not isinstance(radius, float):
            raise TypeError("radius must be a float")
        if radius <= 0.0:
            raise ValueError("radius must be larger than 0")
        self._mutated = True
        self._radius = radius

    def validate(self):
        super().validate()
        if not self.radius:
            raise IllegalState(f"Surface: {self.number} does not have a radius set.")

    def find_duplicate_surfaces(self, surfaces, tolerance):
        ret = []
        # do not assume transform and periodic surfaces are the same.
        if not self.old_periodic_surface:
            for surface in surfaces:
                if surface != self and surface.surface_type == self.surface_type:
                    if not surface.old_periodic_surface:
                        if abs(self.radius - surface.radius) < tolerance:
                            if self.transform:
                                if surface.transform:
                                    if self.transform.equivalent(
                                        surface.transform, tolerance
                                    ):
                                        ret.append(surface)
                            else:
                                if surface.transform is None:
                                    ret.append(surface)
            return ret
        else:
            return []
