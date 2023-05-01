
# April 12, 2023 Virtual Meeting for PATCG/IPA

# Agenda

1. Changes to Match Key Providers [https://github.com/patcg-individual-drafts/ipa/issues/61](https://github.com/patcg-individual-drafts/ipa/issues/61) 
    1. [Attack by malicious MKP](https://github.com/patcg-individual-drafts/ipa/issues/57)
    2. Mitigations
        1. On-device matchkeys
            1. Possibility of platform syncing 
        2. More restrictions on MKP
        3. Open research item 
2. Standards Position of the Chrome Privacy Sandbox Measurement Team, [https://github.com/patcg-individual-drafts/ipa/issues/62](https://github.com/patcg-individual-drafts/ipa/issues/62) 
    1. Overview
    2. Open concerns to discuss
        1. Trigger breakdowns (didn't get to for time)
        2. Match keys without JavaScript (decided it did not need to be discussed)
        3. Delegates Report Collectors (discussed)
        4. \+ Privacy of Individual Events (added and discussed)


# Notes


### MKP issue

Ben Case: If you have a match key provider, which might be a source site. Assuming that they know the relation between users on their site and the match keys, they can generate reports without interacting with the device. Source queries charge against privacy budget for the site, but they can create fake sites, which they register with the helper party network and then generate events for those fake sites.  They can then run queries using the fake data and get more DP budget out of the system.

… You have to do something about the match key provider. Simplest is to assume no match key provider and do device match keys.  Or restrict who can operate a match key provider, which can be more complicated.  At least for now, we don’t know what the right answer is in the longer term, but we can get a lot of use out of the protocol with a device-provided match key.  Keep in mind that we don’t want to close off the potential to include a match key provider.

… That is what leads us to think about on-device, maybe with cross-device synchronization. In this case we would not synchronize events, but just the match key. If there is a mechanism for establishing shared secrets, we could use that.

Charlie: For this vendor synchronization of keys, I want to tease apart how we think about that vs. a set of vendor-allowed match keys.  This is one case where the vendor sets itself as the only match key provider.  Is this the same in terms of having malicious match key providers.  We should consider whether we are OK with that.  Maybe Google as an ad-tech is incentivized to misbehave.  We need to think about that possibility. How we operate here where we need to have some sort of trust in the MKP.

Ben Case: What we’ve thought about is maybe to have some sort of group key exchange between clients.  The limitation there is that whoever facilitates that exchange can add themselves.  People can detect that, but you need a good UI for that to be really detectable.

Charlie: We had similar problems when we looked at cross device and when we wanted cross-vendor synching. The best you can do is a key exchange and have some way to look at the device and see if you have keys for devices that you don’t own.  That’s a pretty weak version of transparency, which requires a lot of manual and difficult work.  It might pass muster, maybe.  Also, Malicious browsers can do much worse than a bad MKP.  I think that people regard browsers as trustworthy because they are open source and we have tools to see what they are doing.  But when servers are involved, we probably need tools for showing what is going on.  We need to think if having a way to look for bad keys is good enough, compared to just having bad code in the browser that might send data elsewhere.

Nick: Not saying that we should trust browsers (I haven’t checked the source code), but more that the software is already trusted because you used it to visit URLs.  Regarding utility, some people are cautious about logging in to browsers and synching. We don’t need to be a guard against the software running on the device.

Charlie: Agreed. Where the line is drawn is a tiny bit fuzzy. None of us would be comfortable with IPA running on Google’s servers, even though Google could have broken all the Chrome browsers.  Maybe we could draw the line at trusting the browser vendor to run a key exchange.

Ben Savage: How can the end user trust what is happening server side.  Maybe we can use a TEE.  

Martin: This depends on information outside of the algorithm.

Charlie: You can always use TEEs to bootstrap trust, but would need to think about it. From the perspective of sync, but it operates on a different layer that uses trusted hardware enclaves.  If you want to put all your trust on hardware, maybe you could do something simpler and put the key on a server.

Ben Case: Open research question. Fielded this as a question to some academics.


### Chrome Standards Position

Charlie has [slides](https://docs.google.com/presentation/d/1u-nOyFxlSMUdgGBAlHpN-IICjLO_T8qvDL30VW0qtEU/edit?usp=sharing)!

Sidebar on how Zoom is terrible.

Charlie: The hardest problem is the third-party measurement use case.  I’ll give a short intro into problems, without solutions. Maybe I can at least identify challenges and gaps.

… (slide 2) Adoption cost. The way it is currently positioned is that it is very clean, but the advertisers need to host a file that essentially commits to a delegate.  That delegation thing might be a useful tool for setting policy in terms of getting the advertisers to say what they want to get from the system, but the problem is that it feels difficult from an adoption standpoint. Advertisers are not always technically savvy.  Hosting this file might mean that IPA might suffer from less adoption. I worry that low adoption will cause people to regard this as a failure.  Lots of covert tracking and PII is being used by “competitors”.  Publishers are worse, possibly more of them and maybe less capable than advertisers.  If we need both parties to host this file, it might not be tenable for adoption.

Martin: ads.txt adoption might be comparable? How is that?

Charlie: might take that as an AI to find out what that does.

Martin: reason to mention this is that IPA works to the point that you have to delegate, at which point you need to put the file in place.

Charlie: Not sure about advertiser side.

Martin: Only raised as an analogous thing.

Ben Case: comparison to pixel difficulty? 

Charlie: When I hear about this from ad-tech, getting people to change their pixel is a 3-5 year epic. This might work with outreach, but that is very difficult. Usually this only involves copy-paste of a new tag, rather than asking about policy choices.  Only a problem if things are complicated and decisions need to be made. Retagging is really really hard, some sites never get updated.

… in terms of incentives, we should be mindful of the work that needs to happen on the server-side for advertisers/publishers, the incentive would be toward server-side fixes. We might need to ensure that you can CNAME something or have a plugin for common server infrastructure so that delegation is easier. Those carry risks too.

…(slide ¾): These are about budget split. Disjoint means multiple parties observing disjoint events, even if they share one side.  All the source events are coming from the channel where those ads are being placed.  No single party has a comprehensive view. This is the state that I see IPA operating in by default.  Vendors/DSPs will each want to operate their own measurement for the ads they place.  You will need to split budget across these channels, unless you do the complex integration work to introduce a single entity with a comprehensive view (omnipresent).

Ben Savage: If an advertiser buys ads on different channels, they don’t need to split budget.  Because the encrypted match keys don’t reveal user-level information, they can send events to the advertiser (or delegate), so that they receive all events.  Budget splits were for more complex cases than buying ads on multiple channels.

Charlie: I would classify this integration as an instantiation of the last bullet (third party/omnipresent). You would introduce a party that gets all the events, probably not the advertiser, likely a delegate. I don’t think that necessarily is a critical flaw, but it is a challenge.  The simplest solution is that delegate.

Ben S: We have conceived of this as a measurement company. These already exist.  MMP (Mobile Measurement Partner) work like this today. Advertisers want a comprehensive view.  Separate channels might claim credit for the same conversions if they are split.  MMPs allow you to see across all channels. The design in IPA assumes this.  Measurement providers talk about “clean rooms” for doing this, where IPA has technical constraints so that you don’t have as much trust involved.  Budget splits give you worse utility.

Charlie: Not disagreeing anywhere.  I’m leading to the next slide. There are existing measurement providers that do cross-channel attribution.  Omnipresent solves a lot of problems.  It does match with existing practice in some way.  The challenge with this being the default is that there are other parties in the ecosystem that depend on measurement too.  DSPs need to buy ads efficiently.  If the DSP gets zero measurement from advertisers, they are in the dark and have trouble operating effectively.  Measurement providers can provide specializations, where each provides different value to the advertiser.  One might have wider coverage for some inventory, or the ability to extend outside of the web with modeling. Specialization is one reason to work with different providers. Different providers might compete on modeling capabilities. One implication from relying on modeling is that it becomes less trustworthy so there might be more value in double-checking, for instance as a safeguard on errors in models.  Once you introduce more parties, you get into utility problems.  Not unsolveable, but challenges.

Martin: not unsolvable?, what are the ideas?

Charlies: Was another slide here. Tools/sketches for solutions.  One tool here is replaying the same noise over the same data.  Post-processing.  If A queries with events A, then party B can also query over the same inputs, but maybe the same data can address both use cases.  Some people in the industry would be alarmed by this.  This might be more feasible.  You might need a cross-industry standard about what different things mean (like breakdown keys or trigger types).  The less you standardize the better.  Event-level output that is differentially private lets you tag different slices differently.  You don’t need to standardize aggregation keys, you only have to standardize the label (converted/didn’t).  Maybe for bidding we could do randomized response.  Not an ideal solution, but maybe a tool.

Ben C: On the DSP would they run a source fan-out to do calibration?

Charlie: Likely, yes.  Hard to think about this with caching. In general, they look at data across all advertisers.  Or maybe an advertiser query that works across multiple advertisers.  Maybe we can craft a budget so that the budget is made available to them.

Ben C: For Meta, we might make a source query, but DSPs would have multiple sites on both sides.  Many-many isn’t how IPA works.

Charlie: DSPs might like many-many.

Ben S: Agree that this is a source fan-out.  FB has a DSP.  What Facebook does is use data across all of the advertisers.  Then it uses that data to determine how to place ads.  That is a case where you might want to do budget splits.  You do have people selling with multiple DSPs.  That is definitely more complex.  This is more of a bidding-side challenge.

Charlie: Bidding is P0 for us.  We need to solve for this before we would be confident in this solution.

Ben S: Not to say that this is important, but more that this is a different category for me.

Charlie: Do you see event-level as useful?

Ben S: Want to talk about that now?

Ben C: Trigger breakdown keys first?


### Private measurement of single events 

[https://github.com/patcg/docs-and-reports/issues/41](https://github.com/patcg/docs-and-reports/issues/41)

[https://github.com/patcg-individual-drafts/ipa/issues/60](https://github.com/patcg-individual-drafts/ipa/issues/60)

Charlie: Idea is at least from the IPA side and even ARA aggregated, we allow you to query slices that are known to be size 0 or 1.  In IPA you have a breakdown key that is unique per event.  Then every bucket is a single source event.  Data is super noisy.  That can be post-processed in ways that can often produce useful results.  Maybe not as useful as an aggregate, but in some cases especially where post-processing is complicated (e.g., ML training) we can get comparable results.  The idea is to query individual events/users and tune the mechanism so that we maximize privacy-ROI.  This is where we get RR or something.  Similar DP guarantees, but the data is in a shape that is more suited to post processing.  Very flexible because each has an event ID and you can feed that to ML capable of handling noisy labels.  This is not as strong as DP-SGD, where we add noise to the gradients, whereas this adds noise to every parameter.  For sparse models, DP-SGD can add more noise than RR.  0/1 flips get close to state of the art performance.  Larger output space means more noise, which affects performance, but there is lots of research here.

…event-level output is useful for downstream processing.  Might even be amenable to standardization on labels for interoperability (for different consumers of the same data).  Maybe even more than 0/1.

Ben S: Question is if we are OK with a breakdown where each value has a contribution from just one user.  Sounds interesting, particularly the ML training use case.  Might be very noisy output, but the ML pipeline can be tweaked. Interested in what different platform vendors’ opinions are.

Martin: has to think about this more

Charlie: adds it to the agenda of next patcg meeting. It will be difficult to defend a privacy budget, if we try to prevent people from getting size 1 outputs (i.e., about a single user).  Especially in IPA threat model.  Same for ARA.  Some things we could do, but they might not work in all cases.  Maybe not defensible, but

Martin: for large number of people to understand the impact would be difficult. Explainability is weak point. We have to work out what we tell people about this. 

BenS: We might need to understand *how* noisy it might be, with concrete numbers.  In the binary example, what is the flip probability?  Is it 90% flip chance?  Or is it 10%?  That is interesting in terms of what you tell people.

Charlie: In the original post I gave a formula.  k/(k-1 + e^\epsilon).  \epsilon=3 -> 10% ish.  Maybe you can bound posterior based on priors.  3 bounds a 50% prior to between 5-95%.  Can share formulae for this.

Daniel: That is event-level.  We also have global caps, would this involve zeroing global contribution.

Charlie: Yes, you still need to bound sensitivity, maybe by dropping events.

Ben S: For \epsilon = 10 that looks like 0.009% ?

Charlie: For high epsilon, we only protect against an adversary with a very low prior.

Daniel: It also depends on how many events you include.  If you have more events, then the probability combines.

Ben S: The IPA mechanism would cap by setting the true label to 0 for many values.

Charlie: We can set max contribution from a user to 1 for example.  We would need to get sensitivity bounds correct.  We could probably do some sort of learning with reasonable epsilons.  Hope Google can publish research here.  I also want to research more complicated stuff like DP-SGD, which might beat this, but this is a known entity.

Martin: what is Charlie’s idea of a reasonable epsilon

Charlie: maybe 3-5  (insert large caveats here!)? We don’t know and plan on doing research on this. Let's shoot for what we think is maybe reasonable, we can do more complicated approaches if it does not work out.

BenC Next time: plenty of stuff.  R&F.  etc,,,


## **Attendance**



1. Benjamin Case (Meta)
2. Andrew Pascoe (NextRoll)
3. Nick Doty (CDT)
4. Daniel Masny (Meta)
5. Charlie Harrison (Google Chrome)
6. Martin Thomson (Mozilla)
7. Sam Weiler (W3C)
8. Amandeep Aggarwal (Amazon)
9. Richa Jain (Meta)
10. Roberta
11. Ben Savage (Meta)
12. Martin Pal (Google Chrome)
13. Chris Wood (Cloudflare)
14. Alex Koshelev (Meta)
