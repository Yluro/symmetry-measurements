# SymmetryMeasurements

SymmetryMeasurements is an [Olex2](https://www.olexsys.org/olex2/) plugin that serves as a bridge to [SHAPE 2.1](https://www.ee.ub.edu/continuous-shape-and-symmetry-measures/) to calculate Continuous Shape Measures  (CShM's) directly from within Olex2.

## Requirements

- Olex2 1.5.
- SHAPE 2.1 executable available on your system `PATH`.
  - Download [SHAPE2.1 from the Electronic Strucutre group's webpage](https://www.ee.ub.edu/downloads/)

## Features

- Reads atomic coordinates directly from the `OlexRefinementModel` — no manual input files needed.
- Generates the necessary `.dat` input files for SHAPE automatically.
- Runs SHAPE and parses the resulting `.tab` output.
- Creates a dedicated folder inside the current dataset directory (`FilePath/autoSHAPE/`) containing all input and output files.

## Usage

1. Open a structure in Olex2.
2. Select the central atom of the polyhedron you want to analyse.
3. Run `spy.SymmetryMeasurements.autoSHAPE()` from the Olex2 console or from the Tools/SymmetryMeasurements panel.
4. Results are printed to the console and saved in `<dataset_path>/autoSHAPE/`.

## Known Limitations / TODO

- [ ] Cannot handle disordered structures yet.
- [ ] Smarter program logic is missing (automatic coordination site detection, multiple selections, etc.).
- [ ] Reimplementation of octahedral distortion parameters (Zeta, Sigma, Theta) — relevant for spin-crossover (SCO) complexes.
- [ ] Support for other symmetry measurement programs (Polynator, Continuous Symmetry Operations, etc.)
- [ ] Clean html UI.

## License
- Not yet.

## Citations

1. Olex2 1.5: J. Appl. Cryst. (2009). 42, 339–341. DOI: https://doi.org/10.1107/S0021889808042726

2. SHAPE 2.1: Organometallics (2005), 24, 7, 1556–1562. DOI: https://doi.org/10.1021/om049150z
