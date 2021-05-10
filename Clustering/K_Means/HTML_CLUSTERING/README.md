# html clustering
> by Lloyd’s algorithm & Mini Batch K-Means

step|what|how
---|---|---
1|chooses the initial centroids, choose k|(1)**random choice** with Cross-Validation(unrealized)<br>(2)k-means + + 
2|Turn k templates to feature vectors|(1)Each vector entry is the count of a given tag and class attribute<br>(2)The dimension of the vectors will change as new pages with new tags or class attributes arrive.
3|assign the remaining templates to its nearest centroid|calculate each template Euclidean distances
4|The difference between the old and the new centroids are computed and the algorithm repeats these last two steps until this value is less than a threshold

### Reference
1. [page_clustering](https://github.com/scrapinghub/page_clustering)
2. [scrapely](https://github.com/scrapy/scrapely)
3. [k-means](https://scikit-learn.org/stable/modules/clustering.html#k-means)
4. [min batch k-means](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans)
