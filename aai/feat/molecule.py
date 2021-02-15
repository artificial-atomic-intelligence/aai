"""Generate physical and chemical descriptors for molecules."""
from rdkit import Chem
from rdkit.Chem import Descriptors as D
from rdkit.Chem.rdchem import Mol

from pdbfixer import PDBFixer
from simtk.openmm.app import PDBFile

import urllib
import json
import os

from typing import Tuple, List


def featurize_molecule(mol: Mol) -> Tuple[List, List]:
    """Featurize a molecule.

    Parameters
    ----------
    mol: rdkit Mol
        An rdkit representation of a molecule.

    Returns
    -------
    (feats, labels): Tuple[List, List]
        Numerical features and corresponding labels.

    """

    feats = [
        D.MolLogP(mol),
        D.MolMR(mol),
        D.MolWt(mol),
        D.NumValenceElectrons(mol),
        D.NumRotatableBonds(mol),
        D.RingCount(mol)
    ]

    labels = [
        'LogP', 'Molar Refractivity', 'Molecular Weight',
        'Num Valence Electrons', 'Num Rotatable Bonds', 'Ring Count'
    ]

    return (feats, labels)


def pubchem_cid_to_mol(pubchem_cid: str) -> Mol:
    """Transform Pubchem Compound ID into rdkit Mol.

    Parameters
    ----------
    pubchem_cid: str
        Pubchem CID, e.g. '2244'

    Returns
    -------
    rdkit_mol: rdkit Mol
        rdkit Mol.

    """

    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/%s/property/CanonicalSMILES/JSON' % str(
        pubchem_cid)
    response = urllib.request.urlopen(url)
    json_response = json.load(response)
    smiles = json_response['PropertyTable']['Properties'][0]['CanonicalSMILES']
    rdkit_mol = Chem.MolFromSmiles(smiles)

    return rdkit_mol


def pdb_id_to_mol(pdb_id: str) -> Mol:
    """Transform PDB ID into rdkit Mol.

    Parameters
    ----------
    pdb_id: str
        PDB, e.g. '2244'

    Returns
    -------
    rdkit_mol: rdkit Mol
        rdkit Mol.

    """

    fixer = PDBFixer(pdbid=pdb_id)
    PDBFile.writeFile(fixer.topology, fixer.positions, open('tmp.pdb', 'w'))
    rdkit_mol = Chem.MolFromPDBFile('tmp.pdb', sanitize=True)
    os.remove('tmp.pdb')

    return rdkit_mol
