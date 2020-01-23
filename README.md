# Narrative Smoothing
Python script to generate a dynamic network of interacting speakers in TV series, as detailed in the following articles :

[Xavier Bost, Vincent Labatut, Serigne Gueye, Georges Linarès.
*Extraction and Analysis of Dynamic Conversational Networks from TV Series.*
Springer. Social Network Based Big Data Analysis and Applications, 2018](https://doi.org/10.1007/978-3-319-78196-9_3)

[Xavier Bost, Vincent Labatut, Serigne Gueye, Georges Linarès.
*Narrative Smoothing: Dynamic Conversational Network for the Analysis of TV Series Plots.*
DyNo: 2nd International Workshop on Dynamics in Networks, in conjunction with the 2016 IEEE/ACM International Conference ASONAM, Aug 2016, San Francisco, United States. pp.1111-1118](https://doi.org/10.1109/ASONAM.2016.7752379)

The annotated input files are parts of the *Serial Speakers* dataset (*Breaking Bad*, *Game of Thrones* and *House of Cards*), available at https://figshare.com/articles/TV_Series_Corpus/3471839

## Usage

```
python3 gen_dynamic_network.py  --input_annot_fname (path of one of the three following files: "bb.json", "got.json", "hoc.json") \
                                --output_graph_fname (path of the output graph file in .graphml format)
 ```

## Output

A multigraph, with multiple edges between two interacting nodes. Every edge between two nodes is indexed by a scene number (attribute "id" in the output .graphml file), and weighted according to the strength of the corresponding relationship in this particular scene (key "d0"). The current episode is recorded in the "d1" key.

Excerpt of the generated .graphml file (evolving strength of the relationship between Arya and Jon (*Game of Thrones*) in the scenes 10--14):

```
...
<edge source="Jon Snow" target="Arya Stark" id="10">
  <data key="d0">0.2479</data>
  <data key="d1">S01E01</data>
</edge>
<edge source="Jon Snow" target="Arya Stark" id="11">
  <data key="d0">0.2588</data>
  <data key="d1">S01E01</data>
</edge>
<edge source="Jon Snow" target="Arya Stark" id="12">
  <data key="d0">0.2588</data>
  <data key="d1">S01E01</data>
</edge>
<edge source="Jon Snow" target="Arya Stark" id="13">
  <data key="d0">0.2915</data>
  <data key="d1">S01E01</data>
</edge>
<edge source="Jon Snow" target="Arya Stark" id="14">
  <data key="d0">0.2915</data>
  <data key="d1">S01E01</data>
</edge>
...
```
