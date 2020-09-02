# Automatic Identification of Politically Extreme Communities on Reddit

## Motivation

The goal of this work is to create a means by which *"politically extreme"* communities can be identified by means of an algorithm analyzing a series of consecutive posts within that community.  In particular; the community studied here is Reddit, which-- briefly-- is a site that hosts "subreddits", essentially individual messageboards.  Reddit, like many large social networking site, has perennial scandals in which extremist groups become heavily based within them, which then attracts great ire from the wider public and generates significant criticism prior to action being taken.  

The goal here, then, is to create a tool by which subreddits can be automatically identified as harboring such groups.  The intent here being not that groups so classfied would be automatically pruned; but rather that such identification -- previously acknoweldged as a daunting task to be done by humans on so large a site -- could be used to inform early monitoring and awareness, consequently avoiding having one caught with their proverbial pants down.  Smaller tack-on uses are apparent, e.g. helping to coordinate user reports.  Indeed, *similar* tools are already employed on facebook and twitter, though operating at a more finely-grained level than what is intended here. 

Concretely, the main focus here is to take in 100 conesecutive posts from a given subreddit-- conveniently the maximum limit that can be grabbed from reddit's API-- and to try to identify if they come from a group classified as "politically extreme" or not.  


## Overaching Concerns

### Labelling

Determining whether or not a given group or ideology is "extreme" is of course a highly subjective and thorny topic; and perhaps not the best word for what's being sought here (though all alternatives thought of seem to carry similar problems).  In determining reddit communities that would be classed as "extreme", such decisions were made with the core motivation of the project in mind -- minimizing future problems with broad furor by other users as the public at large.  As such, a seemingly reasonable criteria was set and followed even when results might seem a little "off" in practice.  Specifically, the groups assigned as "extreme" were those that had either:
- Been the subject of criticism by a major publication and referred to or explicitly self-identified as political.
- Been referred to as extreme by a widely-acknowledged organization that studies such issues (e.g, the SPLC). 
- Been explicitly political and ultimately banned by Reddit. 

Each criteria has nuances to it, of course, but some prior decicision making process must be laid out to temper individaul predilections.  Given the nature of the goal some slippage is "baked in" in any case, so being broadly in the vicinity of a valid labelling is likely sufficient, particulary if it's stable under small perturbations of the labelling.  We discuss some extensions of this idea later on. 

### Evaluation

Two measures of success, one of which not being immediately quantitative and so not easily collapsible with the other into a single objective, errr, objective, were considered here.  First, directly: The goal here is to be aware of the presence and proliferation of "extreme" groups. This, along with the consideration that (almost by definition for a site in the position of Reddit) extreme communities must represent a small fraction of the users as a whole, suggests recall as the apppropriate metric for use; we wish to prioritize aptitude for catching those groups that are extreme.

The second measure of success is the familiar sense of reasonableness as a safeguard against overfitting or spurious results.  We seek an explainable (that is, not black-box) model so that decisions can be interrogated, further we wish to see identifiable features that at least in principle appear to make sense.  There is a real risk here of just learning quirks of the posts we're able to process, we'd like to see meaningful important features to suggest the opposite.  Models achieving a commendable recall but failing in this regard or rejected for that reason. 


## Data


### Sourcing & Processing

Our data was gathered by direct export from a data set available through pushhift.io's collection of reddit comments. The data unfortunately came "raw", with no strong attempt to avoid conflit with any potential .csv separators, and so much attention had to be paid to cleaning throughout the process. Two month's of data were used, representing all reddit comments from August and September of 2017. August of 2017 contained 84,658,503 posts; September contained 83,165,192. The use of two months was due to an external constraint; namely to make the data processing be even remotely feasible. The months chosen were semi-arbitrary, they fulfilled two criteria of not being obviously "special" with respect to political activity (somewhat removed in time from the previous election, not obviously around any major political stories relative to what's possible, etc) and being far enough back in time that it was possible to have some semblence of removednesses from current ongoings in order to try to assess media spotlighting of specific communities. 

Computational and time constraints limited the data that was able to be used from this original data set; rather it was used for the inital sampling. The method used is readily extensible though, and this should be one of the first priorities for future work.  The positive ("extreme") class was assembled by explicit manual identification of a number of qualifying groups, all of whose posts were selected.  The negative ("neutral") class was obtained by sampling other random subforums with a weighting equivalent to their prevalence in the community as a whole. Note that these are different methods of random sampling and both have apparent flaws.  This represents a serious weakness in this project as a whole and, with more resources, should be rectified (this directly ties into the above mentioned first-priority for future work). In the model analysis later in the project some attempt is made to gauge  if the results seemed reliable despite this. 

Each post was grouped into sets of 100 sequential posts, thereafter referred to as a "snapshot", to represent the intended mode in which the model would be deployed.  Internal divisions between posts were not tracked.  Further details on the way the data was obtained and processed are found in the <font color='red'>Data Harvesting</font> notebok.

### Cleaning

The data was extremely noisy (the "raw" posts being raw in the truest sense, not having consistent formatting and encluding metacharacters, spuriously included text, etc.) and severe issues arising from this during the initial importing process were handled at that stage through automatic detection and removal, necessary for said import to proceed.  

Standard NLP cleaning was done (tokenization, conversion of case, stripping spurious characters, etc) with some special considerations given to information context.  For example, the use of internal referrals on Reddit between communities and users are writtten as /r/subforumname or /u/username; cleaning attempted to preserve this information.  Details on cleaning are given in the <font color='red'>Data Cleaning</font> notebook. 

## Modelling

### Creation And Selection

All models were created within a pipeline first consisting of TF-IDF vectorization,  with varying parameters, followed by a random undersampling of the majority class (the positive class, an artifact of the data collection process) and then a classifier.  Multinomial Naive Bayes, Complement Naive Bayes, Linear Support Vector Machine, and Logistic Regressor Classification were examined. The latter two models were obtained by means of sklearn's implementation of stochastic gradient descent, with the appropriate loss function. Multinomial Naive Bayes was used initially as a baseline model and the relationship of its cross-validated performance to the maximum feature size allowed for in the TF-IDF vectorization was used for refinement of the feature space on which the models would then be evaluated, which was chosen to be 1000.  

<font color='green'>performance picture</font>

Smaller feature sizes produced similar results but did not correspond well with reasonability concerns.  Evaluation of these models within this space lead to a selection of Complement Naive Bayes as the preferred model selection, as it did well under both of the selection criterions given above. 



### Evaluation

All models did very well, raising a strong spectre of overfitting not escaped by a train-test split due to initial difficulties in the initial sampling prospect; though there is reason to be optimistic given the perfomance on more difficult, held-back data as discussed in the executive notebook. 

**Disclaimer:** Given the nature of the data being examined here, the raw text being examined, occasionally visible within the notebooks immediately, can at times be, well, quite extreme.  Please be aware. 
