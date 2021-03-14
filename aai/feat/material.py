"""Generate physical and chemical descriptors of inorganic materials."""
from matminer.featurizers.composition import ElementProperty
from pymatgen import *

from typing import List, Tuple


def featurize_composition(comp: str,
                          preset: str = 'magpie') -> Tuple[List, List]:
    """Featurize a chemical composition.

    Parameters
    ----------
    comp: str
        A chemical composition, e.g. 'MoS2'.
    preset: str (default 'magpie')
        A matminer composition featurizer preset

    Returns
    -------
    (feats, labels): Tuple[List, List]
        Numerical features and corresponding labels.

    """

    ep = ElementProperty.from_preset(preset)
    c = Composition(comp)
    feats = ep.featurize(c)
    labels = ep.feature_labels()

    return (feats, labels)
