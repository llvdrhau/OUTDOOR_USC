========
OUTDOOR
========

OUTDOOR (Open Superstructure Modeling and Optimization Framework) is a comprehensive tool for constructing and solving superstructure optimization models using Mixed Integer Linear Programming (MILP) solvers.

Key Features
===========

* **Modular Component Library**: The `outdoor_core` module provides classes for unit operations (reactors, stream splitters, etc.) and system data components that can be assembled into custom superstructures.

* **Integrated MILP Solver**: Built-in PYOMO abstract model implementation that can be applied to various applications including biorefineries, chemical processing, and Power-to-X technologies.

* **User-Friendly Interface**: Create models through Python scripting with intuitive APIs or use the Excel-based interface for rapid model development.

* **Visualization and Analysis**: Integrated tools for reviewing model structure, analyzing results, and optimizing processes.

Installation
===========

::

    pip install outdoor

For the latest development version:

::

    pip install git+https://github.com/llvdrhau/OUTDOOR_USC.git

Usage
=====

OUTDOOR provides multiple ways to define your superstructure models:

2. **Excel Templates**: Use predefined templates to configure your models
3. **GUI Interface**: Visual modeling environment (if available in your installation)


License
=======

OUTDOOR is available under a Dual commercial license. Free usage is permitted under the GNU General Public License (GPL)
v3.0 for academic and non-commercial purposes. For commercial use, please reach out to lucasvdhauwaert@gmail.com.
See the [Commercial License Agreement](COMMERCIAL_LICENSE.md) for details.

Documentation
============

For full documentation, visit: [Documentation Link, under construction]

Development
==========

To contribute to OUTDOOR:

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest` (proper test need to still be made)

Credit
======

If you wish to use this software, please cite::

    @article{van_der_hauwaert_et_al,
      title = {Designing Sustainable Biorefineries for Agricultural Waste: An Environmental-Economic Optimization of Tomato Pomace},
      author = {Van der Hauwaert, Lucas and Sommer Schjønberg, Mias and Regueira Lopez, Alberte and Mauricio-Iglesias, Miguel},
      journal = {Preprint available at https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5277124}
    }


Contact
=======

For support or inquiries, please contact lucasvdhauwaert@gmail.com

