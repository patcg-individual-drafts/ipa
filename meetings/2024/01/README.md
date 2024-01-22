

# IPA Monthly PATCG Individual Drafts Call: Agenda and Minutes


# Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.



*  this week in the IPA call Daniel will present more on the OPRF implementation for scaling IPA.  You can read more here [https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md](https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md)


## **Attendance**
1. Daniel Masny (Meta)
2. Benjamin Case (Meta)
3. Erik Taubeneck (Meta)
4. Martin Thomson (Mozilla)
5. Charlie Harrison (Google)
6. Mariana Raykova (Google)
7. Alex Koshelev(Meta)


## Minutes

Scribe:  Erik Taubeneck

Agenda: [https://github.com/patcg-individual-drafts/ipa/issues/86](https://github.com/patcg-individual-drafts/ipa/issues/86)

**Daniel**: Aim for this to be abstract, not directly how it works in IPA.

Overview of ads measurement. Source events with breakdown key. Trigger events with trigger value. First stage of attribution where we join events based on attribution logic. Aggregation then produces measurement histogram. Could be other settings, but this is focused on histograms.

Aggregation dominates the IPA communication cost. This gets expensive fast, lots of room for improvement.

**Mariana**: Aggregation is more expensive than sorting?

**Martin**: Sorting only happens per user.

**Daniel**: This is the OPRF version. But even with sorted version, aggregation is a significant portion of the cost.

**Mariana**: Sort should be asymptotically more costly.

**Martin**: With sorting, it’s effectively linear in terms of the inputs and linear in terms of the bits. We originally had 40 bits, but with 128, we have ~3x longer than that sorting.

**Mariana**: I thought aggregation would just be a linear scan.

**Daniel**: (moving forward) What is the format of the aggregation stage? One straight forward option could be a per user historgram. Most would be 0, some would not be. Would be a huge histogram, but could just sum them up. Aggregation would essentially be for free, but the histogram would be huge. For 100, it’s pretty big, for 1M it’s way too big.

Another option is a compressed version, by secret sharing the breakdown and the value.

Comparison - per user histogram is easier to aggregate, expensive for more than 6 breakdown keys. Necessary for “straightforward” PRIO.

**Mariana:** Are we talking about malicious servers?

**Daniel:** Compact version requires multiplications, so interactions between the servers, requiring malicious MPC.

**Mariana: **Could use a distributed point function (DPFs.) To compactly secret share a contribution to a particular bucket.

**Daniel: **Potentially an alternative not considered here.

**Mariana:** There is also a way to shift most of the work to the one of the servers, and use the other one for HE decryption.

**Daniel:** Mostly focused on communication cost, so haven’t thought about HE here.

Three approaches we’ve considered. 1. Convert from compact to per user histogram. 2. Add fake events, shuffle, and reveal. 3. Sorting.

Option 1. Limits communication to server to server, not device to server.

**Martin**: this approach works well when some of the breakdown bits come from the trigger and some from the source; we can just combine them and then do the comparison.

**Mariana**: Need to hide what breakdowns people apply to?

**Daniel**: For IPA, for every event, we’d need to do this conversion. If you do this on-device, maybe revealing the breakdown key is ok.

**Martin:** It’s possibly worse in the PAM case if you reveal it to the site or a defecting helper party.

**Charlie:** My understanding of an IPA query is a list of source event match keys with their breakdown along and source events with their value. Why can’t we reveal the breakdown key in general?

**Erik**: Breakdown keys could identify someone, and knowing that it makes it past the attribution stage reveals someone had an attributed conversion.

**Daniel: **Options 2. Add fake events, shuffle, and then reveal. Expensive part is the shuffle.

**Mariana:** Isn’t this the same as the OPRF?

**Daniel: **Some similarities. There we group user events, here it’s on a single user.

**Mariana:** Abstractly, you want to hide the cardinality of these breakdown groups.

**Daniel:** Most trivial distinction is that we don’t have to evaluate an OPRF. You also don’t need to add as many fake events.

**Mariana:** Why is that? How do we compute sensitivity?

**Daniel:** Only need to add a certain amount per bucket. Need to bound the sensitivity.

**Martin: **Any user who contributes more than 15 pairs of source/trigger pairs, looses the rest of theirs.

**Daniel:** One of the biggest difference is that generating fake events with OPRF grows quadratically. Adding noise to the bucket with 100 events, you need to generate a handful of fake users with 100 events. Here, for a given breakdown key, you only have to generate the handful, not the handful * 100.

Ben estimated DP, for ε=0.1 would be about 300 per bucket.

**Ben**: Don’t just want to look at each bin separately, can look at across all bins with a cap of how many a person can be in.

**Daniel: **Some additional leakage, but with a DP bound.

Option 3. Aggregation by sorting. Sort by breakdown, then do a prefix sum. Then you’d “unsort” the list.

**Mariana: **This is different from option 1?

**Daniel: **Yes, it doesn’t require unpacking. It turns out to be more efficient.

**Martin: **Advantage is that there is no leakage relative to 2.

**Daniel:** More difficult to scale sorting, especially to shard it.

**Martin:** Don’t have to do this for everything, just by chunks.

**Erik:** Doesn’t the chunking reveal something?

**Daniel:** Sub results would still be secret shared.

**Martin:** Would only need to chunk by the amount you could fit in memory, if we’re using radix sort.

**Daniel:** Rough comparison: histogram based ~10^19, fakes+shuffle+reveal ~ 2*10^13, sorting ~7*10^14.

**Mariana:** Which stages are happening on the shards?

**Martin: **Each shared would have their shares, which would be sent back to the client to be combined.

**Mariana:** The size of n for each shard would be relatively small.  Shard size may impact which approach is most performant.

**Martin:** That could be workable. Have each shard produce its part of the histogram.

**Erik: **If shards are already limited to what they can fit in memory, then we’d prevent the need for any intra-shard communication.

**Daniel: **Sort relies on a shuffle, so it sorting won’t beat it.

**Mariana:** I don’t think it will beat it, but it may not be that much worse.

**Martin:** At this stage, given the size of 300 for ε=0.1, I don’t think we need to go much smaller.

**Erik:** Does the shuffle cost factor in intra-shard communication for shuffle?

**Daniel:** No, but it should only be a factor of 2/3x.

**Daniel: **Initially, Mariana suggested distributed point functions. May not work for IPA.

**Charlie:** For non IPA use cases, there may be even simpler protocols. But ideally we have something that works for all of them.

**Martin:** We should pick the best one for the scenario.

**Charlie:** We should make sure we’re clear about which protocols will work with which proposals.
