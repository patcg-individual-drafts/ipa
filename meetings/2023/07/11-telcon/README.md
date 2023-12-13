

# Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.

Two agenda items:

* [First 45min]  Privacy Budgets in IPA for Ad Networks 
    * [https://github.com/patcg-individual-drafts/ipa/issues/80#issue-1797341122](https://github.com/patcg-individual-drafts/ipa/issues/80#issue-1797341122) 
    * [https://github.com/patcg-individual-drafts/ipa/issues/78#issuecomment-1622524556](https://github.com/patcg-individual-drafts/ipa/issues/78#issuecomment-1622524556) 
* [Last 15min]   Continue discussion on alternative sharding by matchkey designs. 
    * [https://github.com/patcg-individual-drafts/ipa/issues/75#issuecomment-1629545874](https://github.com/patcg-individual-drafts/ipa/issues/75#issuecomment-1629545874) 


## **Attendance**

1. Benjamin Case (Meta)
2. Charlie Harrison (Google)
3. Nick Doty (CDT)
4. Tammy Greasby (Anonym)
5. Phillipp Schoppmann (Google)
6. Mariana Raykova (Google)
7. Christine Runnegar (PING co-chair)
8. Alex Cone (Google)



## “Whiteboard”

Questions: 


1. What types of queries do different parties currently run? 
2. Do they really need to run their own queries or is it enough to learn results from other parties?
3. How can we in IPA’s privacy budget framework support the necessary queries? 


### Buy side:

* **Advertisers**
    * Able to run their own trigger fan-out queries 
* **Ad Agencies** (advertiser likely use more than one)
* **Ad Servers**
    * Considered source of truth .. .like MMP
    * Make this the central brain for the Advertiser 
        * Would need extra communication than today. 
* **Measurement companies** (e.g., MTA vendors, MMPs)
    * Able to run delegated trigger fan-out 
    * Q: would an Advertiser ever work with multiple?  
* **DSPs**
    * Bid models 
    * Can share event level outputs for them. 
* **Trading desk (independent or the agency’s)**
    * Agency distributes money to trade desks, who work w/ DPSs
    * Multiple traders for the same Adv but want to do different queries
        * Can we have a coordinator overall? But not share outputs 
        * Option 1: each Adv gets budget and gets shared
        * Option 2: each Trader gets a budget 


### Sell side:

* **SSPs**
* **Ad Networks**
* **Publishers**
    * Able to run their own source fan-out queries 
    * Self-attributing publisher is more like a DSP


## Minutes

Scribe: Erik


* Ben: 
    * Hope to collaborate on a table as to the current status of properties of queries.
    * Do we need to add anyone on the Buy side?
* Alex
    * Agency and/or independent trading desk
    * Takes the money and spends the money on the DSP
* Tammy
    * Could we remove the agency then?
* Alex
    * Agency still wants to see the data
    * Traditional role of agency is creative and media, media places budgets.
    * Sometimes agencies pull levers themselves, or pass it off
    * Agency is still judged on performance by advertiser
    * Agency uses advertiser ad server reporting directly, doesn’t rely on trading desk
    * Trading desks pulls out of DSP
* Tammy
    * Lots of programmatic lingo
    * Trading is the person who places budgets
* Alex
    * The person who sets up campaigns, makes sure pixels are there, etc
    * On a daily basis, go in and see if the campaigns are delivering, if delivering then how they are pacing, and if they are pacing, then they go on to look and see if they are performing.
* Ben
    * On behalf of a single advertiser
    * Do they need different queries, or can they use the same ones?
* Tammy
    * Sometimes yes, sometimes no
    * Advertiser with trading desk in house, yes
    * Sometimes advertiser will have multiple agencies
    * Agency can use multiple DSPs
* Charlie
    * The way I see this is that the agency and trader are the “entity”, agency potentially stand in for advertisers
    * Agency wants to see the standard aggregates
    * DSP needs are to make sure their Bid models are working
    * If you have some kind of event level privacy mechanism, via post processing you can share out that event to multiple DSPs without using more budget
        * Maybe a fixed budget for optimization, all DSPs use that.
        * If it’s event level, they can do their own ad hoc thing
    * Tricker side is the trader/agency
        * It would nice to say there’s now a central system, and all agencies look at
        * That would be a clear separation, but today it’s all colluded
        * Right now running queries on DSP and advertiser’s ad server
    * Queries are partitioned by buying strategies
* Alex
    * Make sure it’s clear, the budget can be split across multiple entities pulling levers.
    * Those entities probably shouldn’t be able to see each other’s performance. They don’t today.
    * Advertiser ad server spits out ad creative code / pixel that gets loaded into the DSPs
    * Agency and advertiser can see the whole picture if they have it split up, but those who received only a portion of the budget shouldn’t see each other’s stuff
* Tammy
    * Easiest way is local DP, and then you can partition beyond that.
    * Most often, ad server is source of truth.
    * Empower ad server to send things to DSP, agencies, etc
    * Would be different from today, but would probably be better
* Charlie
    * That seems cleanest to me: make ad server the centralized brain of the privacy budget
    * Next steps for how this could work:
        * How do you handle that? 
        * Who are the traders? 
        * Who get’s what budgets? 
        * Is the ad server capable of dropping a file that would specifies this?
        * Is there a connection between the ad server and the DSP
* Tammy
    * Not exactly our problem
* Charlie and Alex
    * Need some sort of bridge
* Charlie
    * Agree that the way that this life works as a trader:
        * Login to see if you’re a delivering
        * Then, and only then, if you’re pacing
        * Then performance
        * Then try to adjust the campaign to get better performance
    * To do all this, their working on non-source-of-truth data, e.g. DSP data. 
    * There are scraping companies that pull in ad server data to try and join it, etc
    * In a world where we can get source of truth data, that would be great
    * DSP is going to ask for event level data, and they want it quick. Their spending is based on things that update more quickly than what we’re talking about.
    * Assuming a bridge, I just can’t imagine a DSP wanting to be dependent on an advertiser ad server not falling over.
* Tammy
    * If we have event level reports, that could go directly to DSP
    * Only aggregates would not be real time
* Charlie
    * If you don’t do the event level thing, the sharing gets more difficult
    * Label DP is best way we know how to do it
* Ben
    * Moving onto sell side
* Tammy
    * Publisher use cases
* Ben
    * Mostly thinking about publisher optimization
    * Maybe there needs to be some budget spend on “not across publisher” budget to spend
* Charlie
    * Wondering why the publisher needs to do source fanout queries.
    * Is this acting as the SSP? Or is this self attributing publishers?
* Ben
    * Yes, the self attributing publishers.
* Charlie
    * I wonder if the place to slot that is more on the DSP side? It’s roughly trying to do the same thing, but for a single publisher instead of lots of publishers.
    * You could remove source fan outs if you can handle those with the trigger fan outs
    * Either is a one-to-many or a many-to-many
* Tammy
    * One concern is if the advertiser is splitting the budget for open web.
* Erik
    * It’s fixed per site
* Charlie
    * You have small sites on the display network, it’s unclear what type of queries they’d need to run.
    * If only the advertiser can run fanout queries, it simplifies things.

Scribe change: Charlie Harrison w/ Phillipp as backup



* Nick
    * Catching up a little bit on this issue. Why are we talking about splitting budgets? User doesn’t care. Every reason to think callers will collude i.e. share what they learn. Why would there be a split budget?
* Erik
    * You’re on the right track. We need a global budget because we assume everyone is colluding. Budget is 100 unicorns. If there is an advertiser there are different entities that want queries, we need to figure out how that will all work. You can’t give everyone 100.
* Nick: that’s up to you. Work closely with your partners. Is this coming up in the protocol?
* Ben Case: Which party? When someone visits a particular site, we bind the report to that site. If there are multiple agencies, do they need to share the budget with that website? We need to think about the potential attack surface.
    * If the advertiser has a different (independent) budget for each partner, they can amplify privacy loss by creating more partners
    * We presented two options in PATCG, sharing budget vs. ad networks have their own budget, and system keeps a cap on that
* Charlie:
    * Trying to answer the question in a different way. We need to share budget. We need to design a system that is adoptable. Right now, privacy budget is a new thing. The ecosystem wouldn’t know what to do with it. So we need to go through all sorts of use cases to see (1) whether this is feasible at all, and (2) to be able to go to various players and talk about how to use it.
    * In theory it’s easy to describe how to do privacy budget splitting, but we need to make sure we satisfy all the use cases.
* Nick:
    * Why are we talking about different budgets / total budgets (?)
* Charlie:
    * We want to match what’s in IPA right now, but we want to figure out how to instantiate it.
    * IPA has this notion which entities get a fresh budget, and the previous discussion was about whether we need this for all sides.
* Ben: Can we talk about SSPs?
* Alex: the category is changing a little bit. Traditionally the SSP probably wouldn’t have a mechanism on the advertiser’s site (a pixel / SDK) to capture a trigger event, even if the publisher wanted it (which they might). They might want to show that they are performing well for the advertiser. But the ability to put their code on advertiser’s site is not there (unlike the self-attributing pub). That’s the canonical case, they don’t have the trigger data. They have click data as a proxy for performance. That being said, the ecosystem is not static. SSPs are starting to approach agencies / buy-side with tools, particularly in areas like CTV. In those cases they might work w/ advertisers to set stuff up. This gets to Charlie’s point: if we consider this conception as the parties that are currently doing attribution, it’s enough. Focus on the buy-side initially.
* Ben: what about ad networks? Similar category of self attributing publisher
* Alex: There are multiple types of ad networks, crossing both sides or some skewing more buy-side / sell-side. Variance in terms of how they are doing reporting. A lot of them are white-labeled on the DSP, etc. Someone at the ad network might be one of the parties that the agency hands budget out to, along w/ trading desks. There are people that want to see reports that are at ad networks, but it’s a mix of whether they have a system to pull reports or they pull from someone else.
* Ben: Source fanout query. We think ad networks need to pull “many to many” queries for optimization. Similar to self-attributing publisher queries.
* Alex: It’s less clear cut on the ad network side, whether they have their own tech doing optimization. There’s less of that. More so they have their own reporting tech, but some may just be pulling from other systems. Ad networks are more often providing a service on top of other platforms rather than their own tech. There is a slice that does their reporting w/ their own tech, then an even smaller slice doing optimization.
* Tamara: It might be good to stop thinking about companies, since it’s all nebulous. Publisher-centric algorithms
    * **Publisher understanding ad load**
    * **Pricing**
    * Bunch of buying strategies, auctions w/ floor price. Different deals, commit to buy a certain impression at a certain price, you commit that I will win. SSP might help with this. Today not based on ROAS, negotiated.
    * Other than SSP direct to advertiser to cut out the DSP / trading desk, I don’t see a reason why they need the data at all.
* Erik: +1 to that concept. Just getting back to the problems we are trying to solve. Charlie is right we need to figure out how to hoist this on the industry. Two things we are trying to solve
    * Advertiser wants to understand how ads perform
    * Publisher who shows ads from bunch of advertisers, want to know how their site performs. Gets passed around to other companies
    * This is how we came to the two different fanout queries, to answer those questions respectively. It probably wont cleanly map on to existing deployments.
* Erik: doesn’t the ad network need to understand how valuable the site is? If there isn’t a 3P cookie.
* Alex: Yes, the point is that they don’t have the implementation today to grab the trigger events. The buy-side has the setup to grab both. You aren’t wrong, the entities in the middle would be looking to do that, the publisher likes it if they are seen as performing well. The question is more about whether the publisher is even set up to grab those events.
* Erik: Don’t anticipate the publisher setting this up, would assume their display network is receiving trigger events and is optimizing the placement.
* Alex: they are, but that network is using the tech of the buy-side to do that. Networks are typically companies that provide service on top of their own tech or someone else’s tech, aggregating supply and demand. Buy-side tech is the tech that ends up getting dropped on the advertiser site. Reason that is hard to see on the Meta side is that’s not the case for Meta. You built the tech to do the optimization. Advertisers are used to that with you, but not with the rest of the web. That’s not how the rest of the programmatic web works.
* Tamara: it is the same at meta. They are optimizing their site because they are working for the advertiser. A side effect is that they can optimize their site. You can let the advertiser control the budget, data can flow to the publisher for whatever optimization they want to do.
* Ben: it’s interesting to think about. The self-attributing publisher case has the flow in the other direction. Think about a system that can work w/ these different approaches.
* At time, apologies to Mariana / Phillipp.

Sharding



* Ben: we like the idea of OPRF matching, trying to think of if theres a way to bound the sensitivity of the match key. Right now we have every time a user visits a particular domain, another copy of the match key in the query. Every time the user clears state, clears it. Other ideas of bounding the sensitivity on the client.
* Mariana: Bounding the sensitivity, this applies to any type of sharding.
* Ben: Correct, although more of a concern in the OPRF because the shard size are smaller, you have more of them
* Phillipp: biggest difference is that some designs will gracefully degrade whereas in the OPRF approach it doesn’t gracefully degrade.
* Mariana: I’m not sure we know that 100%
* Ben: Maybe even large shards can be attacked by going above the sensitivity bound, but at least you have some aggregation by that point?
* Mariana: Main point was this is an issue in any design
* Ben: We have to make sure we can’t pull budget from different domains
* Ben: can we avoid pulling reports from other sites
* Erik: in probabilistic case 
* Ben: hard to have in context of MKP
* Erik: brainstorming; care about sensitivity because don’t want to know they are in the intersection. Can we reveal by site and check,  
