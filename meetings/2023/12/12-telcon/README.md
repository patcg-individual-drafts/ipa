# Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.

*  this week in the IPA call Daniel will present more on the OPRF implementation for scaling IPA.  You can read more here [https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md](https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md)


## **Attendance**

1. Benjamin Case (Meta)
2. Daniel Masny (Meta)
3. Erik Taubeneck (Meta)
4. Martin Thomson (Mozilla)
5. Nick Doty
6. Phillipp Schoppmann

## Minutes 	

Scribe:  Erik Taubeneck

Slides from Ben: [https://docs.google.com/presentation/d/1Gr6pmA6ObyhYTP-Fn5od9DsAcWpP_W1SUKD84MxOXD8/edit#slide=id.p](https://docs.google.com/presentation/d/1Gr6pmA6ObyhYTP-Fn5od9DsAcWpP_W1SUKD84MxOXD8/edit#slide=id.p)

* Ben:
    * OPRF overview. Don’t get to see individual people, but does reveal # of events per user.
    * Number of events, T, e.g., [1, …, 100]. For each T, helper parties learn the counts of users.
    * We can add non-negative DP noise to each of those counts, but adding sets of random events.
    * Non-negative DP noise provides an (epsilon, delta) guarantee, e.g., there are some extreme cases that may expose an individual’s membership.
    * Nuance here is that the sum of noise is revealed. This is OK with replacement definition of neighboring datasets for DP, and will cost a factor of 2x in sensitivity.
* Nick
    * Helpers would also know how much is added because it’s documented in the protocol
* Ben
    * You’ll generate a random amount each time. Each helper will generate ⅓ of the total noise. 
* Martin
    * Simplest way to do this to do it pairwise, so each party would know ⅔s the data. Need to add 3 times the noise.
* Nick
    * [missed the question]
* Martin
    * Want a strong differential privacy argument, then can make some tuning with the epsilons. Here we want to lay the ground work for the fundamentals.
* Daniel
    * Two aspects with the ⅔s because we get the malicious security. 
* Erik
    * If we didn’t need malicious, it would only be 1.5 more.
* Martin
    * Manipulation could get nasty, so we’ll certainly want malicious security.
* Ben
    * Need to compose across this histogram. Analogous to the Laplace Mechanism that lets us add (epsilon/Delta delta/Delta)-DP to each component of a vector where Delta = L1 or L2 norm sensitivity, to get (epsilon, delta)-DP
* Martin
    * What’s the net effect?
* Ben
    * The L1 norm will be 2.
* Martin
    * Concretely, the amount of noise will be proportional to what?
* Ben
    * Proportional to 2, regardless of the number of bins or the size of the histogram.
    * For the non-negative noise, with sensitivity 2, you have an expectation n. 
    * You then have to generate the number of events of the size of each bin, e.g. n people with 1 event, n people with 2 events (2*n events), etc. 
    * Should actually be that they know ⅔ the noise, and multiply by 3.
    * [Table]
* Martin
    * Is that a billion?!
* Ben
    * Yes, it really depends on the parameters
    * Next slide for discussion, what should those parameters be?
    * Should it factor into the budget? It’s not (intentionally) revealed to the consumer.
* Martin
    * Prefer this not to be deducted from the budget.
    * Range from 1-10 is probably acceptable here.
* Daniel
    * Curious how this compares to other DP mechanisms.
* Ben
    * Can’t use regular laplace or gaussian because we can only add dummies.
* Martin
    * Don’t need to do this in MPC, can just do it pairwise. 
* Daniel
    * Is the problem with gaussian that it’s not discrete?
* Martin
    * Just saying we don’t need it in MPC.
* Daniel
    * Can’t you just round up?
* Martin
    * There are papers on that.
* Ben
    * Any thoughts on delta?
* Martin
    * Currently using ~10^-9 probability of detection in the implementation.
    * Reasonably comfortable with 10^-8 or 10^-9.
    * 1 in a million is on the edge, 
* Ben
    * What’s a reasonable value for the cap? It makes a big difference.
* Erik
    * Can’t it be configurable?
* Martin
    * Needs to be configured on the device.
* Erik
    * These epsilons are per query, so if you use your budget to run lots of queries, this will grow..
* Martin
    * If you’re making a query with ε=1, then the dummy event epsilon is ε*M, for some multiplier, e.g, 10. The loss towards the helper parties is worse, but we trust them somewhat.
* Ben
    * What if we assume multiple sites colluding with the helper?
* Phillip
    * One nice thing about tying it to the budget is you have a tradeoff.
* Nick
    * Are there important business cases where the user visits 10k times?
* Martin
    * I think one of the problems is that on a site like Instagram, where every nth content is an ad, and you need to throw all those in a bucket.
