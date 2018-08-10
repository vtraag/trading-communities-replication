# Erratum

This repository contains the data and code needed to replicate the results in the erratum to [Lupu and Traag (2013)](http://journals.sagepub.com/doi/abs/10.1177/0022002712453708).

[![DOI](https://zenodo.org/badge/134671832.svg)](https://zenodo.org/badge/latestdoi/134671832)

## Overview

Please clone using `git clone` or [download](https://github.com/vtraag/trading-communities-replication/archive/master.zip) the zipped repository and unzip to your desired location.

This repository contains two directories: `src` and `data`.

The `data` directory contains all primary data to replicate the results. This is based on the following data sources:

- [Trading network and GDP data](http://privatewww.essex.ac.uk/~ksg/exptradegdp.html), v4.1 from Gleditsch (2000) in file `dependence.dta`.
- Aggregated data from the [EUGene project](http://eugenesoftware.org/) by D. Scott Bennett and Allan C. Stam, III in file `eugene2.dta`. The data we use is in turn based on the following datasets:
  - [Dyadic Militarized Interstate Disputes Dataset](http://vanity.dss.ucdavis.edu/~maoz/dyadmid.html) Version 2.0 (DYDMID2.0), from Zeev Maoz.
  - [Polity IV: Regime Authority Characteristics and Transitions Datasets](http://www.systemicpeace.org/inscrdata.html) from  Marshall and Jaggers (2002).
  - Correlates of War (CoW) [Alliance Data Set](http://www.correlatesofwar.org/data-sets/formal-alliances) v4.1, from Singer and Small (1990).
- Correlates of War (CoW) [International Governmental Organizations Data](http://www.correlatesofwar.org/data-sets/IGOs)  v2.3, from Pevehouse, Nordstrom, and Warnke (2004) in file `igos.dta`.
- Correlates of War (CoW) [State System Membership](http://www.correlatesofwar.org/data-sets/state-system-membership), v2016 in file `states2016.csv`.

The `src` directory contains all code needed to run the replication. It contains two files:

- `network_analysis.py` should be run first, in `Python`.
- `merge_recode_regress_stata.txt` should be run second, in `Stata`.

The `Python` code performs the following:

- define the trade network based on the Gleditsch (2000) data in `dependence.dta`.
- calculate maxflow in the network.
- detect communities using Louvain modularity maximization algorithm.
  - each country-year is assigned a community ID.
  - this is performed 100 times each using three resolution parameters (0.6, 1.1 and 1.7).
- create the `Same Trading Community` variable.
  - for each resolution level, a dyad-year is coded as 1 if the dyad-year members are in the same trading community in 50 or more of the runs, and 0 otherwise.

The resulting maxflow will be written to the file `maxflow.csv` in the directory `results` (this directory will be created by the code). The resulting partitions will be written to files `comms_x.x.csv` for the different resolution parameters in the directory `results`. The dyadic `Same Trading Community` variable will be written to files `dyads_x.x.csv` for the different resolution parameters in the same directory.

The `Stata` code performs the following:

- calculate the mean value of the two directed maxflow measures for each dyad-year. This mean value is used in the logit models.
- merge the `Same Trading Community` and `maxflow` with data on conflict and control variables.
- recode some control variables (e.g., population is logged, missing data categories (e.g., -66, -77, -88) in Polity are coded as missing, etc.)
- generate cubic splines.
- lead the dependent variable by one year.
- estimate the logit models reported in the erratum and export to Latex.

The resulting `LaTeX` table will be written to the file `myfile.tex`.

## Installation instructions

In order to run the code, make sure you have `Python` installed. It is usually most convenient to install the [Anaconda](https://www.anaconda.com/download/) `Python` distribution. Some other libraries will be required by to run the code:

- `python-igraph` (>= 0.7.1)
- `louvain-igraph` (>= 0.6.1)
- `pandas` (>= 0.20)
- `numpy` (>= 1.13)

You should be able to install all these libraries on all platforms (Windows, Mac OS, Linux) using `conda install`. Possibly you may have to add the Anaconda channel `conda-forge` and/or `vtraag`. For more details, you can search for these packages on https://anaconda.org/.

For `Stata` please ensure you have version 13 or higher.

## References

Gleditsch, Kristian S. 2002. "Expanded Trade and GDP Data." Journal of Conflict Resolution 46 (5): 712-724. doi: [10.1177/0022002702046005006](https://doi.org/10.1177/0022002702046005006)

Lupu, Yonatan and Vincent A Traag. 2013. "Trading communities, the networked structure of international relations, and the Kantian peace." Journal of Conflict Resolution 57 (6): 1011-1042. doi: [10.1177/0022002712453708](https://doi.org/10.1177/0022002712453708)

Maoz, Zeev 2005. Dyadic MID Dataset (version 2.0): http://psfaculty.ucdavis.edu/zmaoz/dyadmid.html.

Marshall, Monty, and Keith Jaggers. 2002. "Polity IV Project: Political Regime Characteristics and Transitions, 1800-2002." University of Maryland

Pevehouse, Jon C., Timothy Nordstrom, and Kevin Warnke. 2004. "The Correlates of War 2 International Governmental Organizations Data Version 2.0." Conflict Management and Peace Science 21 (2): 101-19. doi: [10.1080/07388940490463933](https://doi.org/10.1080/07388940490463933)

Singer, J. David, and Melvin Small. 1966. "Formal Alliances, 1815-1939: A Quantitative Description." Journal of Peace Research 3 (1): 1–32. doi: [10.1177/002234336600300101](https://doi.org/10.1177/002234336600300101)
