# April 26, 2023 Virtual Meeting for PATCG/IPA

# Agenda


**Multi-touch attribution algorithms**



* Agenda request [here ](https://github.com/patcg-individual-drafts/ipa/issues/13#issuecomment-1517258198)to talk more about this and get publisher input on what MTA algorithms would be desired in the in-market test of IPA

**on-device matchkeys -- short and long term plans**



* In the long term with on-device matchkeys we would like different browsers (and apps) to be able to access the same per-device matchkey; in the near term in the Chromium design what we can do is implement a browser specific matchkey.

**Sharding**



1. We can give a short update on the design for [caching matchkey shares instead of ciphertext](https://github.com/patcg-individual-drafts/ipa/issues/35#issuecomment-1514547336)
2. We should follow up on [discussion ](https://github.com/patcg-individual-drafts/ipa/issues/57#issuecomment-1496521137)of whether webviews would impact sensitivity of matchkey cardinality
    1. For related context on webviews see this [section ](https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md#web-views-and-embedded-browsers)of end-to-end doc

**Trigger side-breakdowns**



* [@csharrison](https://github.com/csharrison) has a couple slides on [trigger side-breakdowns](https://github.com/patcg-individual-drafts/ipa/issues/55) we didn't get to last meeting.


## Notes

**Trigger side-breakdowns ([slides](https://docs.google.com/presentation/d/1u-nOyFxlSMUdgGBAlHpN-IICjLO_T8qvDL30VW0qtEU/edit#slide=id.g22d0709a120_0_23))**

Charlie - filed an issue. High level; currently IPA only supports source-side breakdown and trigger value. Lots of use-cases. In ARA we have two kinds of API outputs, one supports a course enum for trigger side breakdown. Use-case is advertisers set up categories for conversions (e.g. add-to-cart, or signup, or purchase). Usually not too many. In some cases, even the trigger breakdown can have a high cardinality. Advertisers may want to look at purchase categories. Can be detailed. Core use-case is coarse-grained enum. Seems like MVP could be supporting coarse-grained enum and just do breakdown on cross-product of source and trigger value. Lots of challenges, as the join is potentially sensitive. We would have to be careful. Simplest is cartesian product, but might have lots of things with no conversions. Lots of techniques in privacy literature. 

Ben Case: In the circuit, is this exclusively used for the cartesian product? Any other use-case? 

Charlie: Just obliviously join with source breakdown and breakdown by both. Techniques to compress both. Source x trigger breakdown makes a high cardinality, but maybe you’re only looking for a few “classes” of things. Compressing the domain down gives you better privacy and efficiency. Google product “selective optimization”, “biddable optimization” vs “non-biddable optimization”. This might be a more complex circuit, but this is a use-case. Unclear how big of a priority it is. This is supported by ARA through this declarative language that has access to source breakdown.

Martin Thomson: sounds like this could get arbitrarily complex. Seems like ARA design has drawn the line in a pretty easy case to manage. If we have a finite set of breakdowns on each side and just use both, I think that’s basically no work. I think we can get a long way with that. The dividing the space into two for this biddable / non-biddable thing would require more communication costs. I prefer to avoid doing that until it’s very urgent. But value in doing the very easy thing. 

Charlie: We can do these things in an extensible way. I don’t see any one-way door. Even for ARA, might seek to simplify our approach. Happy to share the research we are doing. 

Ben Case: Good starting point. Let’s move one to next topic.

**on-device matchkeys -- short and long term plans**

Ben Case: What’s possible is OS support so that different apps can leverage this. But as we work on the Chromium design, it’s browser instance specific. That’s what is possible in the short term. 

Mariana: Why can’t the match key work across browsers?

Ben Case: It’s more, what can we do with Chromium updates vs where do we need OS support. Long-term no reason we can’t do a device level match key. 

Charlie: Are we planning on using the same match key even across different browsing profiles within Chrome? 

Ben Case: Haven’t thought about this. 

Martin: Webviews also affects this. A number of places where the default browser is embedded. If you let them use the same approach, in situations where they let you correlate activity across apps (outside of the MPC). 

Charlie: Is this due to the caching layer? Can we just fix that?

Martin: As I thought about webviews, I realized that if the app can modify the webview you need to think of that like separate browsers.

Ben Case: As Martin says, if the app has unfettered access to the webview, we don’t know if they are requesting match keys for sites the user isn’t even visiting. 

Charlie: What’s the specific attack vector?

Ben Case: Similar to malicious match key provider. The event can be bound as if it occurred on any number of sites, and I can put it into multiple source fanout queries. 

Charlie: We don’t have a strong security boundary on the event provenance.

Martin: The app retrieving encrypted match keys can access the match keys, but lie about which website is being visited.

Charlie: Within the security model of Android Webview, if the raw match key is within memory, you could just extract it. 

Ben Case: For an app SDK, the OS can validate which app is calling it. 

Charlie: Have you decided on a path forward?

Richa: Yes, we will not support webviews for now.

Charlie: That sounds reasonable.

**Sharding**

Ben Case: You leak to the report collector, information about the distribution of ads. We considered using multiple layers of encryption, but we realized there is a more efficient approach, which is to cache the shares, and use a different encryption each time. Compute the PRF based on the shares. Not a huge change, but this is an update on our design with the sharding. 

Ben Savage: Each separate site gets match keys regarding interactions on that site.  Multiple parties need to get these separate events together.  We realized that one side sends the information about impressions (say), then a cached match key encryption reveals cardinality about ad load and number of users.  It’s not cross-site information, but it might be commercially sensitive.  It would be better if we could prevent that leak. The goal of this piece is to let the helper nodes know that the events came from the same person, but not reveal that to anyone else.

…: If the helpers need to bound sensitivity (for cardinality), then they need to know that.  There are two big approaches: either refuse to give out more match keys (or encrypt garbage), with lots of downsides, like leaking or losing functionality; or, you can get as many encryptions as you like, but you would set a query parameter to cap the number of events per user.

Charlie: Bounding sensitivity on the client can limit what you can do.  I don’t see any problems with the IPA design here.

Ben S: The Chromium design we’re working on does some of this already, but instead of caching ciphertexts, it would be caching shares.

Charlie: Caching shares seems better overall.

Ben S: You don’t need to reconstruct the match key to do sensitivity capping.  Each helper has two shares and count those that are the same.  The odds of a collision with 64-bit match keys is astronomically/comically small.

Mariana: Do you need to create dummy records in this system?

Ben S: The dummy records do not need to be the same as any real user.  ?

Mariana: Is this a PRF on the match key?

Ben S: Yes.  The PRF needs to be a function of the match key.

Ben C: Yes, for sharding, we need a PRF on the (reconstructed) match key.

Ben S: We need to evaluate the PRF in MPC.

Mariana: The PRF we suggested was homomorphic instead, not MPC.

Ben C: That was semi-honest.

Mariana: We have a variant that gets to malicious security [details?].

Ben C: That’s an option too. You can encrypt on the device twice. First you use a maliciously secure PRF. That’s definitely an option. So far we’ve assumed just one was simpler, but you could definitely have a separate PRF just for the shard.

Mariana: So you were suggesting computing the PRF in the circuit?

Ben C: Yes, but we haven’t implemented any of these approaches.

Mariana: I think we have an implementation of the maliciously secure PRF.

Phillipp: Actual question was, what do the helpers do in the case they discover a match key that exceeds the sensitivity bound.

Ben C: Drop records.

Ben S: You can configure at what point you start dropping if you do it in the helpers.

Ben C: Sometimes you know something about the distribution of what you expect.

Charlie: This is in general one of the reasons why sensitivity bounding off device is more powerful. You just have this knob of how much noise/cost you can tolerate vs the truncation you get with dropping. I had a more basic question. When we implement this, do we have something more formal about what the MPC is aside from the End-to-End doc? If we are implementing something towards a particular protocol it would be great if the protocol was written down. I think anonymous partitioning is written down. I know you have code, but 

Ben C: We have a [pre-print on eprint.](https://eprint.iacr.org/2023/437) But there are things that are not entirely in-sync with the code. We need a much clearer spec.

Charlie: Discrepancies in the code are find if those are just bugs and the thing written down is the source of truth.

Martin: It was my intent to write down a spec once things stop moving. Just the spec for multiplication is non-trivial. It hurts my head. We will start working on that. We need to not only describe the protocols in an abstract sense, but also in a way that can be integrated into a system. Clients do that to submit queries, and MPC helper nodes do to communicate with one another. 

Mariana: That’ll be big.

Martin: a couple thousand pages. Starting with Pseudo-random secret-sharing and then multiplication, etc. The more variations Charlie adds the worse it gets.

Christina: Some concerns about what is visible to a report collector. Do we have a sense of what is “appropriate” and what is “inappropriate” data flow? Writing that down would be helpful. Understanding how much a report collector should be trusted would be helpful.

Martin: That, and the leakage in the protocol itself, like this leaking of cardinality to the helper nodes. It’s not great, but we need to do it.

Philip: The end-to-end functionality would be a great step.

Christina: Do we have product requirements, what would publishers consider acceptable to leak. Just having those requirements. That would be a useful input. 

Charlie: I think what Christina is getting at is “with respect to whom?”. That’s with respect to the user’s privacy. But if there are other things, like what you talked about, let’s write that down too. We can bring this to the broader threat model doc as well. “Chained report collectors”. That could be a good place to put any of these general findings.

Martin: Our discussion have focused on commercially sensitive information. We have options, but they affect the submission process. It’s just more computation. Computation is cheap.

**Multi-touch attribution algorithms**

Joey: In general we like whatever our advertiser’s like. Ben, I think you said the “equal credit last N” is possible to implement. That sounds interesting. 

BenS: in design have limited privacy budget for reporting.  But if you have to use it across all the sites you buy ads then you get better dp if you do on big query.  All source in a query.  Might as well do cross pub attribution.  Specifics of algorithm unlikely to have privacy impact.   Let the Adv choose.   Open to having different MTA algorithms.  Equal credit to last 3 … but tricky if only 1 in which case want to give it all the credit.  First touch, last touch easy,  

Charlie: suggestion: match MTA in ARA – [priority bit](https://github.com/WICG/attribution-reporting-api/blob/main/EVENT.md#trigger-attribution-algorithm), sort based on that; first touch, last touch, probabilistic linear, seems not too hard.  Question: scope of where you see going?  For chrome would like to do data driven attribution, not just any other path but aggregates of all paths in the query,  more complex credit assignment.  Doesn’t have to be in scope for IPA but much more useful for us. 

BenS: would be nice, data driven attribution would be nice to support.  Happy to have others help contribute to the code.  Can be an enum based on what adv wants to query. 

Thomas: measurement companies will all come up with different models.  Start simple makes more sense.  Question: MTA usually means across different channels – how to assign across changes ?  possible with IPA?

BenS: yes can do cross channel 

Thomas: let companies develop their different approaches 

Martin: specification needs to determine certain things; slowest moving target is interface with UA.  Then interface with RC - enable different attribution models.  Data could be the same for submission; just change parameters on query.  

BenS: priority bit sounds good.  One byte?

Charlie: [more than a byte](https://wicg.github.io/attribution-reporting-api/#attribution-source-priority), would need to standardize

Charlie: whoever issues the query can specify by how they have annotated.  Needs to algin to downstream.  Cross channels may have trust issues, but can probably handle.

BenS: delegation to measurement company; publishers send encrypted source and annotations.  Priorities would let value clicks over impressions.  If you’re okay to share with delegated RC.  and timestamps.  Could let measurement company update

Charlie: higher priority clicks over views. 

Daniel: priority bits may be hard in MPC.  timestamp sorting is also used to ensure you can't attribute a conversion to an event that happened later than it.  may need to do attribution for each priority… 

Charlie: can guarantee source all come first and then sort by timestamp? 

Daniel: if all triggers first may get all value.



## **Attendance**



1. Benjamin Case (Meta)
2. Andrew Pascoe (NextRoll)
3. Daniel Masny (Meta)
4. Alex Koshelev (Meta)
5. Thomas Prieur (Criteo)
6. Christina Ilvento (Google Chrome)
7. Charlie Harrison (Google Chrome)
8. Phillipp Schoppmann (Google)
9. Michael Kleber (Google Chrome)
10. Joey Knightbrook (Snap)
11. Mariana Raykova (Google)
12. Ben Savage (Meta)
13. Martin Thomson (Mozilla)
