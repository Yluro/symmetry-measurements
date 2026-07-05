# SymmetryMeasurements

SymmetryMeasurements is an [Olex2](https://www.olexsys.org/olex2/) plugin that serves as a bridge to [SHAPE 2.1](https://www.ee.ub.edu/continuous-shape-and-symmetry-measures/) to calculate Continuous Shape Measures  (CShM's) directly from within Olex2.

## Requirements

- Olex2 1.5.
- SHAPE 2.1 executable available on your system `PATH`.
  - Download [SHAPE2.1 from the Electronic Strucutre Group's webpage](https://www.ee.ub.edu/downloads/)

## Features
All analysis methods in Symmetry Measurements will read the atomic coordinates directly from the `OlexRefinementModel` — no manual input files needed.
## AutoSHAPE
- Generates the necessary `.dat` input files for SHAPE automatically.
- Runs SHAPE and parses the resulting `.tab` output.
- Creates a dedicated folder inside the current dataset directory (`FilePath/autoSHAPE/`) containing all input and output files.
### Usage

1. Open a structure in Olex2.
2. Select the central atom of the polyhedron you want to analyse.
3. Run `spy.SymmetryMeasurements.autoSHAPE()` from the Olex2 console or from the Tools/SymmetryMeasurements panel.
4. Results are printed to the console and saved in `<dataset_path>/autoSHAPE/`.

## Octahedral Distortion Parameters.
Reimplementation of the OctaDist algorithm based on a topological approach. Values are normally consistent with OctaDist. 
- Bond length distortion
```math
\zeta = \sum_{i=1}^6 |d_i - d_{mean}|
```
where $d_i$ is individual M-X bond distance and $d_{mean}$ is the mean metal-ligand bond distance.
- Octahedral tilting parameter
```math
\Delta = \sum_{i=1}^6 \left|\frac{d_i - d_{mean}}{d_{mean}}\right|
```
where $d_i$ is individual M-X bond distance and $d_{mean}$ is the mean metal-ligand bond distance.
- Cis-angle distortion
```math
\Sigma = \sum_{i=1}^{12} |90^\circ - \phi_i|
```
where $\phi_i$ are the cis angles.
```math
\tau = \sum_{i=1}^3 |180^\circ - \psi_i|
```
where $\psi_i$ are the trans angles.
```math
\Theta = \sum_{i=1}^{24}  |60^\circ - \theta_i|
```
where $\theta_i$ are the individual twisting angles between the vectors of two opposite faces.

### Usage
1. Open a structure in Olex2.
2. Select the central atom of a 6-coordinate complex.
3. Run `spy.SymmetryMeasurements.autoOCTADIST()`
4. Results are printed in the console. A graph will saved in `FilePath/OH_distortion` showing the extracted octahedron. 


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
