# Biodb-expression-atlas

This library is for extracting upregulated and downregulated genes related to Parkinson's disease from microarray experiments in [Expression Atlas](https://www.ebi.ac.uk/gxa/home) based on p-value and log2 fold change values. 

---

## Getting Started
This is an example of how you may give instructions on setting up your project locally. To get a local copy up and running follow these simple example steps.

#### Installation

1. Clone the repository
   
``` shell
    git clone (https://gitlab.informatik.uni-bonn.de/biodb-2022/packages/biodb-expression-atlas.git
```
2. Install package

```shell
    pip install -e biodb_expression_atlas
```

#### Usage

1. Import database

```shell
    biodb_expression_atlas import-database
```

2. OpenAPI using Swagger

```shell
    biodb_expression_atlas serve -o
```