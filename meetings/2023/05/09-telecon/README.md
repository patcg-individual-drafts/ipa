
# May 9, 2023 Virtual Meeting for PATCG/IPA

## Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.

Two main agenda items



* **What data is shared with Report Collectors**
    * [Read here with pictures rendered better ](https://github.com/bmcase/patcg-ipa/blob/report_collectors/details/report_collectors.md)
    * PR:  [https://github.com/patcg-individual-drafts/ipa/pull/72](https://github.com/patcg-individual-drafts/ipa/pull/72)
* **Event Labeling Queries with per user DP bound:**
    * [Read here with pictures rendered better: ](https://github.com/bmcase/patcg-ipa/blob/main/IPA-End-to-End.md#event-labeling-queries-with-per-matchkey-dp-bound)
    * Agenda issue: [https://github.com/patcg-individual-drafts/ipa/issues/71](https://github.com/patcg-individual-drafts/ipa/issues/71)
    * PR: [https://github.com/patcg-individual-drafts/ipa/pull/70](https://github.com/patcg-individual-drafts/ipa/pull/70)





## Minutes

Ben Case: two topics to discuss. Event labels and what data iss shared with report collectors.

First topic: Report collectors - what they are and what data can be shared with them. (shares a screen). Term may be new for IPA, they can be large publishers/advertisers. Large publishers conversion flow includes joining impressions and conversion events, i.e. performing attribution. What changes for them in IPA, is that conversion will happen in MPC. Reports however will largely be the same. Data flows in the same manner regardless whether they use IPA or attribution in the clear.

Large advertisers are similar as well as MMP. Report collector role in IPA requires those parties to no longer observe cross-site identifiers. That is the goal of IPA - to prevent cross-site tracking. IPA assumes that source and trigger parties will collude, so its threat model implies protection against such collisions.

IPA source events include timestamp, breakdown key and cross-site linkable identifiers. In contrast with attribution in the clear, IPA requires those values to be secret-shared. Some of those values, for performance reasons, may be visible in the clear. Sorting by timestamp in the clear makes MPC computation significantly cheaper. Breakdown keys are assumed to be sequential (0..range) which poses a challenge for different parties to agree on what they should be.

IPA trigger events include similar information + a trigger value. Trigger values representation may have similar challenges as breakdown keys, i.e. standardization is hard here.

Mariana: a question about the decision to have the encrypted match key rather than all inputs prepared for the client. Every report includes encrypted match key and keeping additional value attached presents a challenge for MPC, because it requires it to be secret--shared. In general, it requires more rounds of interaction.

Martin: Client encrypting the additional information will incur the same cost. It makes it worse.

Ben Case: Is there a reason breakdowns are private to the device?

Philipp: the difference between sharing and encrypting is that shares can be recognized.

Martin: Encryption can be recognized too. That is not a concern. There may be some confusion about how information is propagated through the system. Encrypted match key is accompanied with secret shares. Reshare protocol can make them non-recognizable.

Philipp: Re-randomizable encryption also works in this case.

Martin: We can also create additional encryption around.

Daniel: It is not completely clear what the problem is. If we need to compute PRF to compute the shards, the shuffling is necessary.

Philipp: It is basically about two ways of doing shuffling. Resharing or re-randomizable encryption.

Martin: it is communication versus computational cost. Both things are possible. If one of the ad-tech companies collude with helper parties, that may be a problem.

Daniel: Re-randomizable encryption may not solve the problem, resharing that involves reshuffling does. Timestamps may be used to imply conversions.

Ben Case: The breakdown keys are not used for sharding. Why is it an issue if breakdown keys are coming from an attacker?

Marianna: They have to be carried around. How you do it is the question.

Ben Case: you mean if we had them encrypted, we wouldn’t need to worry about passing them around in MPC.

Marianna: yea, that was in our original design for ARA.

Ben Case: we can follow up on that.

Christina: I am much less familiar with the proposal, what you have described here seems reports are sent in the clear. Is that accurate?

Ben Case: yes, before events are sent, RC has a chance to filter them.

Christina: On the conversion side, if you had duplicates you can filter them out too. The goal is to have a single RC per publisher/advertiser, is that accurate?

Ben Case: it is not in scope for this document. We should have another explainer for it. The site where conversion occurs need to be the one running the query or delegate it.

Christina: If an advertiser runs multiple campaigns, there has to be one person running the query.

Ben Case: for trigger fanout queries, you’re the only one that runs queries that include your trigger events, but you can include other source events.

Charlie: the key thing in IPA is that you need strong security boundaries. The owner should be ok with other parties consuming budgets of that scope. Budget sharing is being discussed currently. But there must be a mechanism that establishes trust.

Martin: I wanted to say the same thing as Charlie just said.

Christina: That helps. We care about what to share with report collector. There are cases where ads may target more than one destination. Brand + retailer, one case we may consider supporting.

Martin: That is easy. Events that happens on this ads we send to both destinations. It will be counted twice in two privacy scopes. Each destination will be spending their own budget. If there are two different outcomes, we would be able to count them independently.

Charlie: we may think about supporting deduplication. There are use-cases where it makes sense, especially small advertisers.

Ben Case: we can do something like that. Lets go to the second topic: event-level queries with DP bound. (presents the doc). To recap: last week we wanted to be able to do event-level attribution. If you’re the source site, you know who you show your ads to. If the source site wants to submit event-labeling queries to MPC, MPC will label them according to the attributions. Privacy will be preserved by applying noise proportional to the total number of source events in this query that are associated with individual users. Charlie proposed capping instead of scaling noise proportionally, but that may leak some information because the lack of label information reveals now many individual events associated with a single user were in the query. Scaling up noise allows capping the information release about an individual user. This types of queries can be allowed in IPA if they use the shared privacy budget with “regular” queries.

Marianna: Is capping coming from the outside? How can we validate that?

Ben Case: There is no capping per person in my proposal. We just increase the amount of noise added for users with more events in the queries. The issue with the cap I still don’t know how to address is whether the random labels will be worst for utility.

Charlie: there are not random, they are zeroes. You flip them with a certain probability. The issue with dynamic noise is that it is biased.  In both cases it causes significant data degradation. If you have some aux information, it may help. Flip probability is a function of epsilon and sensitivity bound. If you have more contributions, they would be truncated to zero. There is a mechanism in IPA that does the capping.

Martin: Yes, it is called the attribution window. If I want the sensitive cap of 3, people with fewer events will be better protected.

Daniel: One challenge is the cost. Generating this noise in MPC may be expensive.

Marianna: We have some hope that it could be solved assuming that prior is not public. We’ve been looking into this.

Martin: Event-level noisy labels may be easier.

Marianna: Why?

Martin: The sensitivity cap will be public. The flip probability can be pre-arranged value.

Marianna: I thought priors are private.

Martin: The labels is the only thing that is private here.

Marianna: These priors, assuming features are public, are public too.

Ben Case: Not sure how would you use prior.

Marianna: In bias randomized response, the flip probability depends on how you would pick prior.

Martin: Charlie’s approach makes flip probability fixed and it is pretty straightforward.

Charlie: prior comes into play when we don’t use binary randomized response, only response in bins. Even in IPA setting, RC and publishers/advs can decide whether features are public or no.

Ben Case: Maybe a related point: for using priors for rare conversions the suspicion curve is lower. From the attacker’s point of view, isn’t my prior is based on whether user have visited both sites?

Charlie: Depending on what attacker is trying to: if conversion is just a page visit and prior is 50%, then yes. Any DP mechanism should give this protection, regardless of what the underlying mechanism is.

Ben Case: What is the priority between binary and k-ary. My understanding is binary gives you most of the unitity already

Charlie: what k-ary gives you: for campaigns with multiple conversions you can get a count. You can also do regression problems with values, i.e. answer the question: what is the value of this conversion. I can’t tell what is the right priority here though. Binary is a great start. We just need to keep an eye on carry mechanisms as they bring some utility to the table.

Ben Case: Any other things to chat about? Conversion optimization when features are private, is there anyone from ad tech with feedback on that? If the features are private not to one site but to multiple sites, DP-SGD assumes features are known.

Charlie: my understanding how it fits into post-third-party-cookie world. Fledge-protected audience world. If you are not in this world, private learning only makes sense if model is not going to the person that supplies those features. It is an open issue how IPA works with Fledge. How we deal that even in reporting case is unknown, for model training it is even less clear.

Christina: is multi-touch in scope for that?

Ben Case: We have looked into multi-touch, I don’t know immediately how it relates to features split between different sites.

Martin: In theory, it would be possible to take features rfom multiple impressions and combine them in some way, but I would prefer to do it later.

Christina: Can there be multiple parties contributing to the features vector?

Martin: It is also out of scope. I like these meetings because they bring to discussion a lot of convoluted cases that exist in real world.

Ben Case: we are trying to get the core functionality up and running.


## **Attendance**

1. Benjamin Case (Meta)
2. Daniel Masny (Meta)
3. Andrew Pascoe (NextRoll)
4. Phillipp Schoppmann (Google)
5. Alex Koshelev (Meta)
6. Christina Ilvento (Google Chrome)
7. Russell Stringham (Adobe)
8. Mariana Raykova (Google)
9. Joey Knightbrook (Snap)
10. Richa Jain (Meta)
11. Martin Thomson (Mozilla)
