=======
History
=======


0.4.0 (2022-03-18)
------------------

* Drop: Support for Python 3.5-3.7
* Add: Support for Python 3.8-3.9
* Update: Use QuTiP 4.6

This is a maintenance release updating to the latest versions of Python and QuTiP and dropping support of versions that have reached end-of-life


0.3.2 (2019-08-02)
------------------

* Fix: adapt to changes in QuTiP 4.4
* Fix: adapt to changes in Sphinx (better-apidoc 0.3.1)


0.3.1 (2019-02-15)
------------------

* Fix: the routine ``make_PE_krotov_chi_constructor`` now returns a function that is compatible with a stricter interface for ``chi_constructor`` in the `krotov` packages (which now requires that ``chi_constructor`` routines accept keyword arguments).


0.3.0 (2019-01-26)
------------------

* Add: routine ``make_PE_krotov_chi_constructor`` for calculating the boundary conditions for the backward propagation in an optimization towards a perfect entangler using Krotov's method

0.2.1 (2018-12-18)
------------------

* Bugfix: project metadata

0.2.0 (2018-12-18)
------------------

* Add: Conversion between canonical basis and Bell basis: functions ``bell_basis``, ``gate``, and ``mapped_basis``

0.1.0 (2018-11-22)
------------------

* Initial release
