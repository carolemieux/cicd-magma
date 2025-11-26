# CICD-Magma: Artifact for CI/CD simulation in Magma

This repository contains scripts and data accompanying the paper "Directed or Undirected: Investigating Fuzzing 
Strategies in a CI/CD Setup". The initial report was published in FUZZING'24:

> Madonna Huang and Caroline Lemieux. 2024. Directed or Undirected: Investigating Fuzzing Strategies
> in a CI/CD Setup (Registered Report). In Proceedings of the 3rd ACM International Fuzzing Workshop (FUZZING 2024). 
> Association for Computing Machinery, New York, NY, USA, 33–41. https://doi.org/10.1145/3678722.3685532

The full paper is under submission.

The `tosem-results` directory contains processed data from our evaluation. The README in that folder describes what
each data file is in detail. The `tosem-scripts` directory contains script to (a) process raw data into this processed
data, and (b) present the processed data in the manner presented in the paper.

Raw data from our evaluation can be found at https://zenodo.org/uploads/17664060. Note the whole size of the raw data is huge:
271GB for the main experiment data, 50GB for the sensitivity experiments, and 0.6GB for the coverage data. 

---

For any Magma-specific documentation, refer to [the Magma homepage](https://hexhive.epfl.ch/magma).