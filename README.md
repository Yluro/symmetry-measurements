# SymmetryMeasurements

SymmetryMeasurements is an [Olex2](https://www.olexsys.org/olex2/)$^1$ plugin that serves as a bridge to [SHAPE 2.1](https://www.ee.ub.edu/continuous-shape-and-symmetry-measures/)$^2$ to calculate Continuous Shape Measures (CShM's) directly from within Olex2.

### Features
- All analysis methods in Symmetry Measurements will read the atomic coordinates directly from the `OlexRefinementModel` — no manual input files needed.
- SHAPE 2.1 direct bridge and output parser.
- Octahedral distortion parameter calculations.


## Requirements
- Olex2 1.5.
- SHAPE 2.1 executable available on your system `PATH`.
  - Download [SHAPE2.1 from the Electronic Strucutre Group's webpage](https://www.ee.ub.edu/downloads/)

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
Symmetry Measurements comes with a reimplementation of the [OctaDist](https://octadist.github.io/)$^3$ algorithm. This implementation is based on a topological approach. Several features from the original program have been pruned for the ease of portability to Olex2 and overall redundancy. The Octahedral distortion parameters module calculates all the values normally produced by Octadist.Values are normally consistent with OctaDist. 
- Bond length distortion:
```math
\zeta = \sum_{i=1}^6 |d_i - d_{mean}|
```
where $d_i$ is individual M-X bond distance and $d_{mean}$ is the mean metal-ligand bond distance.
- Octahedral tilting parameter:
```math
\Delta = \sum_{i=1}^6 \left|\frac{d_i - d_{mean}}{d_{mean}}\right|
```
where $d_i$ is individual M-X bond distance and $d_{mean}$ is the mean metal-ligand bond distance.
- Cis-angle distortion:
```math
\Sigma = \sum_{i=1}^{12} |90^\circ - \phi_i|
```
- Trans angle distortion:
where $\phi_i$ are the cis angles.
```math
\tau = \sum_{i=1}^3 |180^\circ - \psi_i|
```
where $\psi_i$ are the trans angles.
- Octahedral twisting distortion:
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
- [x] Reimplementation of octahedral distortion parameters (Zeta, Sigma, Theta) — relevant for spin-crossover (SCO) complexes.
- [ ] Support for other symmetry measurement programs (Polynator, Continuous Symmetry Operations, etc.)
- [ ] Clean html UI.

## License
- Not yet.

## Citations

1. _J. Appl. Cryst._ (2009). 42, 339–341. DOI: https://doi.org/10.1107/S0021889808042726
2. _Organometallics_ (2005), 24, 7, 1556–1562. DOI: https://doi.org/10.1021/om049150z
3. _Dalton Trans._ (2021) 50, 3, 1086–1096. DOI: https://doi.org/10.1039/d0dt03988h
