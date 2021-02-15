from aai.feat.material import featurize_composition
from aai.feat.molecule import featurize_molecule, pubchem_cid_to_mol, pdb_id_to_mol

from rdkit.Chem import MolFromSmiles


def test_featurize_composition():
    c = 'MoS2'
    feats, labels = featurize_composition(c)
    assert len(feats) == 132
    assert len(labels) == 132


def test_featurize_molecule():
    m = MolFromSmiles('CCO')
    feats, labels = featurize_molecule(m)
    assert len(feats) == 6
    assert len(labels) == 6


def test_pubchem_cid_to_mol():
    cid = '2244'
    m = pubchem_cid_to_mol(cid)
    assert m.GetNumAtoms() == 13


def test_pdb_id_to_mol():
    pdb_id = '3cyx'
    p = pdb_id_to_mol(pdb_id)
    assert p.GetNumAtoms() == 1720
