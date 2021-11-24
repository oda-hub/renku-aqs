### Suggesting projects for astro users of Renku


* I work in some particular astrophysical domain: [HMXB](https://en.wikipedia.org/wiki/X-ray_binary#High-mass_X-ray_binary). I want to start with some example workflow on renku
* I type in a search field HXMB. As I type, I see a connected tag cloud (subselected, scaled graph) relevant to my input. 
* I also see list of relevant workflows, sorted according to my request
* I find a useful workflows analysing NuSTAR data for [Cyg X-1](https://en.wikipedia.org/wiki/Cygnus_X-1) (which is an HMXB - massive star and a black hole orbiting each other) and use it as an example


![](https://user-images.githubusercontent.com/3909535/142020701-65523b70-2a9d-42c2-b645-58d23b394cfe.png)

### Helping learn how to build a workflow

* I work on a astronomical workflow: requesting some data from **astroquery**, reducing it, producing results.
* I want to get some ideas of what to improve in my workflow. Perhaps substitute parts of my workflow (or even whole workflow)
* I get suggestions, incorporate them in my work (or use them instead my own workflow, and focus on interpretation)

## Simple new workflow composition
### Suggesting new relevant and valuable inputs for my workflow

* I work on a astronomical workflow: requesting some data with **astroquery**, reducing the data, producing scientific results.
* I want to get some ideas of how to apply my workflow to other cases
* I get suggestions for new relevant variations of my workflow runs by changing input parameters: I worked with Cyg X-1, but I could also apply it to V 0332+52. Both are HXMB so this is a likely suggestion.
* Runs are suggested to me. They may be also executed automatically. I inspect results and expand impact of my workflow

*See examples* of this sort of suggestions based on KG, supported by community-provided ontologies: https://github.com/oda-hub/renku-aqs/tree/upgraph

### New observatory data

* I recieve new data from an observatory, and I want to analyse them.
* I download the data. I want to find the best tools to reduce them: extract basic products, perhaps some more or less superficial conclusions
* My data has coordinates close to Cyg X-1. I get suggested workflows tuned to analyse Cyg X-1. 
* I adapt and run suggested workflows

*Note*: this can be used, for example, in INTEGRAL quick-look activities, with workflows built for [cross-calibration](https://indico.ict.inaf.it/event/1001/contributions/10148/)

### New astrophysical events or sources are discovered and published

* New intersting astrophysical event happens, it is reported in publications. It is an HXMB (Cyg X-1) associated with a Neutrino, at certain time moment.
* I am interested to derive relevant standard results for this event. 
* I get suggestions for workflows which fetch and analyse Cyg X-1 observations near the time of interest, and also relevant already executed runs.
* I produce reproducible results, publish

### New scientific software

* I have produced a new scientific software version
* I want to check it on data where it was previously relevant. 
* I get suggestions, run them (perhaps automatically), compare results with the previous ones

*Note*: this **has been** used in INTEGRAL [cross-calibration activities](https://indico.ict.inaf.it/event/1001/contributions/10148/)

## Reproducibility

### Ensuring reproducibility of my results by workflow mutation

* I produced some results but they might depend on particular implementation. I want to check if they change when something is changed about the workflow
* I get suggestions for changing parameters: replacing scientific software version

### Verifying reproducibility of published results 

* I find some published results but they might depend on particular implementation. I want to see if I can reproduce them with workflows available to me.
* I get suggestions for workflows reproducing the result, and determine if the published results are reliable

## Workflow structure

### Suggest astroquery and/or ODA requests

* I am building a workflow in renku. I am using `astroquery` to fetch SDSS data of Cyg X-1
* I may want to incorporate other data to enhance my analysis. I ask for suggestions of which `astroquery` calls I should use.
* Renku suggests me what else I might want to do with `astroquery` relevant for current context: I should request INTEGRAL data.


## More complex workflow composition
### Suggest relevant further steps following outputs of my workflow

* I used renku-hosted workflow to reduce INTEGRAL data of Cyg X-1. I produced some images.
* I want to analyse this images. I ask renku for relevant workflows which can consume inputs I produced.
* I get a suggestion to use typical astrophysical source extraction method, and apply it to my data and get useful standard results
* I also get a suggestion (lower priority) to run particularly efficient workflow for image analysis developed in medical imaging. I apply it as well and see if it  performs well.