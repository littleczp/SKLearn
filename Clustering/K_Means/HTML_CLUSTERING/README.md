# html clustering
> Model: Mini Batch K-Means<br>
> Theory: HTML Dom frequency<br>
> Approaches: Centroid Euclidean Distances

# Directory
```
data/           # main data_set
test/           # test HTML_CLUSTERING
utils/
    __init__.py # build dom structure
    html.py     # HTML Tag class

./
    __init__.py
    feature.py  # calculate tag frequency
    kmeans.py   # KMeans model
    main.py     # build kmeans
```

step|purpose|how
---|---|---
1|Chooses the initial centroids, choose k|(1)**Random choice** with Cross-Validation(unrealized, only once random)<br>(2)[gap-statistic](https://statweb.stanford.edu/~gwalther/gap)
2|Turn k templates to feature vectors|(1)Each vector entry is the count of a given tag and class attribute<br>(2)The dimension of the vectors will change as new pages with new tags or class attributes arrive.
3|Assign the remaining templates to its nearest centroid|Calculate each template [Euclidean distances](https://en.wikipedia.org/wiki/Euclidean_distance#Squared_Euclidean_distance)
4|Repeats until the centroids do not move significantly|The difference between the old and the new centroids are computed and the algorithm repeats these last two steps until this value is less than a threshold

#### feature vectors
```html
<html>
    <body>
        <table class="table1">
            <tr>A</tr>
            <tr>B</tr>
        </table>
        <table class="table2">
            <tr>M</tr>
            <tr>N</tr>
        </table>
    </body>
</html>
```
| tag, class     | position | count |
|----------------|----------|-------|
| html           | 0        | 1     |
| body           | 1        | 1     |
| table, table1  | 2        | 1     |
| tr             | 3        | 4     |
| table, table2  | 4        | 1     |

> Each non-closing (tag, class) pair is mapped to a vector position<br>and the number of times it appears in the document is the value of the vector at that position

When a new page arrives it can be possible that new (tag, class) pairs appear.
For example imagine that this new page arrives:

```html
<html>
    <body>
        <a>Another page</a>
    </body>
</html>
```
The new page would be mapped according to this table:

| tag, class     | position | count |
|----------------|----------|-------|
| html           | 0        | 1     |
| body           | 1        | 1     |
| table, table1  | 2        | 1     |
| tr             | 3        | 4     |
| table, table2  | 4        | 1     |
| **a**          | 5        | 1     |

### How to use
1. Place the templates in the `test/download` folder
2. Run test.py (You can modify the **max_std_dev** in the run.py to Control the degree of differentiation)

### Reference
1. [page_clustering](https://github.com/scrapinghub/page_clustering)
2. [scrapely](https://github.com/scrapy/scrapely)
3. [k-means](https://scikit-learn.org/stable/modules/clustering.html#k-means)
4. [min batch k-means](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans)
