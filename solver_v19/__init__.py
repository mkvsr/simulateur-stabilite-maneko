"""
solver_v12 package
------------------

Ce package regroupe tous les modules du solver :

- cg.py            → calcul du centre de gravité
- loader.py        → gestion du chargeur (bras + outil)
- static_pfs.py    → stabilité statique
- dynamic_pfd.py   → stabilité dynamique
- wheels.py        → charges aux roues
- geometry.py      → géométrie & rotations
- solver.py        → orchestrateur principal

L’objectif du package est de fournir une API simple :
    from solver_v12 import solve
"""

from .solver import solve

__all__ = ["solve"]
