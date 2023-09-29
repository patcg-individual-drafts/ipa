# 3IPA Overview (Draft)

Daniel Masny ([@danielmasny](https://github.com/danielmasny))

We describe the high level flow of IPA that uses a PRF, i.e. the Dodis-Yampolski PRF, to shard events by match key. This allows us to group user events efficiently. However it leaks the amount of user events. We can use DP to hide this leakage.

This documents only describes the high level flow, but not the specific protocol that is used for evaluating the PRF nor a scalable shuffle protocol. 

The **main bottleneck** for the horizontal scalability of this approach is currently the shuffling protocol that happens at the end of the second stage. 

## Query format 
A query from the report collector to the helper servers contains the following information:

  * How much DP budget is spent on this query, `dpb`
  * A DP sensitivity cap, `cap`
  * A bound on the number of events per session, `N_s`
  * A bound on sessions per user, `U_s`
  * Amount of events, `N`
  * A list of `N` encrypted events (this does not need to be sorted by timestamp). The encryption contains the following information:
    * match key: arithmetic share over `ℤp`, where `p` is the amount of curve points of the PRF elliptic curve
    * timestamp: Boolean share
    * trigger bit: Boolean share
    * trigger value: Boolean share (s.t. shared value is guaranteed to be `<cap`)
    * breakdown key: Boolean share

## First Stage, Preparing the MPC Computation
The MPC helper server do the following:
  1. Check whether the report collector has enough budget. If not abort, otherwise subtract `dpb` from the budget.
  2. Event Clean Up:
      1. Each helper decrypts all events. They mark all events for which decryption fails
      2. The helpers check whether the shares are consistent across helpers
      3. The helpers delete all events with decryption failures and inconsistent shares
  4. Enforcing Session Bound (bounding amount of events per “session”):
      1. Each helper groups events by shares, i.e. events with the same shares are identified as within the same session. 
      2. The helper coordinate to delete events of each session such that the amount of events per session is Ns. 

## Second Stage, Fake Event Integration
The MPC helper server do the following:
  1. Generating Fake events:
     1. Each pair of helper servers `[i,j]` in `([1,2],[1,3],[2,3])` generate for each `k` in `(1,...,N_s*U_s )`:
        1. noise `e_(i,j,k)`, sampled from DP noise distribution parameterized with sensitivity 1
        2. For each `m` in `(1,..., e_(i,j,k))`:
           1. pick a random match key from the entire match key space (pick a random share `shi,j`) and generate `k` fake events for this match key. We can use identical shares for all of these events (the shuffle operation that will follow later will randomize them). 
     2. Each pair informs the other helper how many fake events have been generated in total, i.e. `N_(i,j) = SUM_(k=1)^(N_sU_s) k*e_(i,j,k)`. Afterwards, this helper generates `N_(i,j)` events and initializes its shares with `0`. 
      
  3. Run an MPC shuffle protocol to shuffle all events including fake events. The total amount of events is `N_t = N + N_(1,2) + N_(1,3) + N_(2,3)`.

     
The MPC helper learn a histogram. The bins are the number of events. The value for each bin indicates how many match keys (including fake match keys) exist that have this amount of events.

## Third Stage, OPRF Evaluation and Grouping by User
The MPC helper server do the following:
  1. For each event `k` in `(1,...,N_t)`:
     1. Evaluate the OPRF on the match key shares using the OPRF MPC protocol. The OPRF MPC protocol reveals the OPRF evaluation on the match key to all helper servers. We denote this OPRF evaluation as the match key pseudonym (which changes for a match key across different IPA queries).
  2. Group the events by match key pseudonym (e.g. by sorting in the clear). After the events are grouped by match key pseudonym, we delete the match key pseudonym of each event.
  3.  Check whether any group has more than `N_s*U_s` events. If this is the case, there is a **privacy violation** since there is no group of fake events for groups with more than `N_s*U_s` events.


 
## Fourth Stage, “Per Match Key” Attribution
The MPC helper server do the following:
  1. For every group of events (i.e., events with the same match key pseudonym),
     1. run an MPC sorting protocol to sort the events within the group based on timestamp
     2. run an MPC attribution protocol that assigns breakdown keys to trigger events if there has been a conversion for the trigger event. 

     

## Fifth Stage, Aggregation
The MPC helper server do the following:
  1. [optional:] prune the amount of events in each group (by only keeping a fixed amount of attributed events)
  2. merge the events of all groups
  3. [optional:] prune the total amount of events (by only keeping attributed events)
  4. run an MPC aggregation protocol



## Sixth Stage, Release Aggregated Query Outcome
The MPC helpers send their secret share of the sum of attributed trigger values per breakdown to the report collector who can recombine the shares and learn the sums per breakdown.  
