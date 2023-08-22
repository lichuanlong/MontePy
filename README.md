# MCNPy

A python library to read, edit, and write MCNP input files. 

## Installing


### System Wide (for the current user).

>>>
Note: If you are planning to use this in a jupyter notebook on an HPC, 
the HPC may use modules for python, which may make it so the installed MCNPy package doesn't show up in the jupyter environment.
In this case the easiest way to deal with this is to open a teminal inside of `jupyter lab` and to install the package there.
>>>

1. [Go to the packages page.](https://hpcgitlab.hpc.inl.gov/experiment_analysis_all/software/mcnpy/-/packages)
1. Select the release you want to install. The latest version is: ![latest release](https://hpcgitlab.hpc.inl.gov/experiment_analysis_all/software/mcnpy/-/badges/release.svg)
1. Scroll down to the bottom of the page, and download the wheel or tar ball file.
1. Navigate to the location you downloaded the file to.
1. Install it by running `pip install --user mcnpy.XXXXXX.tar.gz` or `pip install --user mcnpy-0.1.5-py3-none-any.whl`.

### Install specific version for a project

The best way maybe to setup a project-specific conda, momba, a venv environment.
The steps for installing inside one of those environments are the same as the previous steps.

Another option is to clone the repository and to use symbolic-links. In this scenario we'll assume that your local
repository is located at `~/dev/mcnpy`, and your project is located at `~/foo/bar`. 

1. Move to the repository parent folder: `cd ~/dev`
1. Clone this repository: `git clone git@hpcgitlab.hpc.inl.gov:experiment_analysis_all/software/mcnpy.git` 
1. Enter the repository: `cd mcnpy`
1. Checkout the specific version you want. These are tagged with git tags
    1. You can list all tags with `git tag`
    1. You can then checkout that tag: `git checkout <tag>`
1. Install the dependent requirements: `pip install -r requirements/common.txt`
1. Move to your project folder: `cd ~/foo/bar`
1. Create a symbolic link in the project folder to the repository: `ln -s ~/dev/mcnpy/mcnpy mcnpy`

Now when you run a python script in that folder (*and only in that folder*) `import mcnpy` will use the specific version you want. 

## User Documentation

MCNPy has a [sphinx website](https://experiment_analysis_all.pages.hpc.inl.gov/software/mcnpy/). 
This has a getting started guide for users,
as well as API documentation. 
There is also a developer's guide covering the design and approach of MCNPy, and how to contribute.

## Features
	
* Handles almost all MCNP input syntax including: message blocks, & continue, comments, etc.
* Parses Cells, surfaces, materials, and transforms very well.	
* Can parse the following surfaces exactly P(X|Y|Z), C(X|Y|Z), C/(X|Y|Z) (I mean it can do PX, and PY, etc.)
* Can read in all other cards but not understand them	
* Can write out full MCNP problem even if it doesn't fully understand a card.	
* Can write out the MCNP problem verbatim, if it has not been modified at all.
* Can quickly access cells, surfaces, and materials by their numbers. For example: `cell = problem.cells[105]`.
* Can quickly update cell importances. For example `cell.importance.neutron = 2.0`.
* Has over 240 test cases right now 

 
Quick example for renumbering all of the cells in a problem:

```python
import mcnpy
foo = mcnpy.read_input("foo.imcnp")
i = 9500
for cell in foo.cells:
  cell.number = i
  i = i + 5
  
foo.write_to_file("foo_update.imcnp")

```

## Limitations

Here a few of the known bugs and limitations:

	
* Cannot handle vertical input mode.
* Does not support tallies in an easy way.
* Does not support source definition in an easy way.
	
## Bugs, Requests and Development

So MCNPy doesn't do what you want? Right now development is done with a  Just-In-Time development approach, as in features are added JIT for a developer to use them on my current projects. 
If there's a feature you want add an issue here with the feature request tag. 
If you want to add a feature on your own talk to Micah Gale (but still add the issue). 
The system is very modular and you should be able to develop it pretty quickly.
Also read the [developer's guide](https://experiment_analysis_all.pages.hpc.inl.gov/software/mcnpy/developing.html).

# Version Numbering Scheme

* Software on `develop` and feature branches are subject to change without a version number increment. These version
  may be suffixed as dev (e.g., `0.1.0.dev2`) and may change as features and bug fixes are implemented.

* Versions are official if and only if they are:
   1. on the branch `main`.
   1. has a release git tag assigned
   1. has distribution packages created and released
   Official shall not change. New merges to main shall have a version number incremented.

 
# Finally: make objects not regexs!
