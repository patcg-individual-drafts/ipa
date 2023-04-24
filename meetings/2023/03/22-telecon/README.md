# March 22, 2023 Virtual Meeting

## Agenda
IPA Sharding with Sensitivity Bounds (Detailed issue: #35.)
Interfaces for setMatchKey and getEncryptedMatchKey (Detailed issue #52)


## Intro
Brian May: Is this a W3C meeting?

Erik: We are operating under the auspices of the PAT-CG

Sam W: That’s right.

Erik: These aren’t formally endorsed or adopted, but we are working under the auspices of the PAT-CG on something that could become a recommendation in the future.

Sam W: Any concern Brian?

Brian May: No.

Sam W: Everyone please behave.

## Sharding with Sensitivity Bounds

Ben Case: <presenting slides> Issue #35. Start with talking about the problem. Want to run distributed across many machines. This reveals how many records are sent to each machine. We compute some PRF of each record to decide where to send it.

You could have a malicious helper. Goal is to figure out if user A on site A and user B from site B are the same user or not.  Do they wind up on the same shard or not? We don’t know how much noise to add. Need some way to limit the sensitivity on each shard.

Propose browser caches the encryption of a match key per epoch. Each time “getEncryptedMatchKey()” is called, you get the same encryption. Same website repeatedly called “getEncryptedMatchKey()” it’ll keep getting the same thing.

This bound holds for matchkeys coming from a device. We could come to an agreement on an upper bound for this.

If you’re a match key provider - you can generate events that didn’t occur on the device. We can’t bound that. You’ll be able to see - for the match key you’re monitoring which shard it wound up on. But that’s OK. So long as we can bound the unknown match key - we can add non-negative noise and get a strong DP parameters only needing to add a few thousand rows per shard is sufficient.

In order to leverage the fact that we leveraged this encryption, we have a 2-stage approach.

Mariana: muted

Ben Case: To bound the sensitivity of the unknown match keys, we first shard by the ciphertext, and cap the number of rows with a given ciphertext. Then, you compute a PRF and shard based on that. We can decide what the bounds should be.

Charlie Harrison: In the previous slide, the bounds you’re advertising are the lower-bound of the idealized mechanism for adding positive noise only. Can we do that in a malicious MPC, and will you go over that?

Ben Case: Ben provides a mechanism. You generate these random PRF calls.

Ben Savage: stable sharding so that you don’t have to also sort by timestamps, which are expensive.



Mariana: why don’t we enforce it on the client?

Ben Case: To answer, when we have a sensitivity cache, what we are proposing is that we always give you an answer when you call “getEncryptedMatchKey()”, it’ll just give you the same thing. So for stage 1 of the sharding, someone tries to increase the sensitivity by making copies of it. It’s all the same encryption, so we can detect that. We assume the size of that DB is too large, so we shard by ciphertext value so that each shard can fit in memory.

Mariana: But we don’t want to enforce any capping on device?

Ben Case: Doesn’t seem we need to. Just give you the same thing. We could, but it puts more work on the user of the API.

Charlie Harrison: There’s a discussion on the GitHub about it.

Erik: You only need to call “getEncryptedMatchKey()” once per session. You can just generate your own events at will.

Ben: The getEncryptedMatchKey gives a consistent token that you can use for multiple impressions.

Charlie: The alternative is to give out a different encryption every time and enforce “no duplicates” on the server-side. We didn’t see too many benefits.

Erik: Seems unnecessary to engage the browser on every event.

Mariana: Is there any impact on the sensitivity.

Erik: By having it be consistent, we can bound the sensitivity.

Charlie Harrison: There is one other consideration I posted in another issue, might be relevant. There was a proposal to add an “event type” into the match key. I think the initial proposal was just to add “source” vs “trigger”, but if we wanted to embed more policy into the browser about what kind of events can be generated at what time. For example, if you wanted “clicks” and “impressions” to have different policies, or if we invent some kind of “viewability” thing, maybe we would want to give a different policy to these things.

Erik: The issue we run in to, is if you can set the match key, the match key provider can set all of that on their own, pretending to be the user. Here, we are purposely trying to connected the same user. Not a lot of policy we can do in order to stop that inauthentic activity.

Charlie: Isn’t that an extension of the “known match key provider”. You’re still getting protected on sites where the match key provider can’t identify you. I see your point that we protect everything with policy, but still has value.

Ben Case: We are currently talking about the leakage through sharding. Source and trigger are nice to commit to in the browser. I don’t necessarily see a connection to sharding leakage.

Charlie: Agree. This is just a second-order effect.

Nick Doty: Maybe it’s been answered, but let me see if I understand. The attack is mitigated by having the browser cache the encryption. You’re saying the attack continues if the MKP is malicious?

Ben Case: Purely server side, they can generate encrypted match keys. But we can still prevent this attack. The true number, that are from an unknown person, can be protected.

Erik: Just to clarify Nick, the attack is not based on multiple match keys, it’s based on the number of events. Looking at shard sizes. Trying to bound shard sizes.

Nick Doty: Why do we want it to be the case that a server can generate an event without user interaction.

Erik: When we think about the attribution process, all the browser is adding is this linkage. What’s a source or trigger event isn’t up to the browser.

Nick Doty: understand the mitigation, but don’t understand why *no

Ben: Don’t have a feasible way for preventing a malicious match key provider from generating inauthentic events if we enforced it in a user agent.

Brian: You’ve looked into that?

Ben: Charlie has filed an issue around who should be allowed to be a Match Key Provider. Could have a code of conduct. One of the things you could put in there is promising not to generate synthetic match keys.

Ben Case: I think we’ve covered the sensitivity capping.

Mariana: Can we have a detailed presentation on the stable sharding? I heard Ben saying the match keys can be re-used across many impressions. Are these going to be fresh encryptions of the match key.

Ben Case: If done server-side they could be fresh encryptions.

Mariana: For desirable functionality, do you *want* to generate many encryptions. Is this desirable to do.

Ben Savage: Why would it be desireable?

Mariana: Don’t know. Don’t you need it?

Erik: Each site has just one ciphertext per epoch per person, so the helpers can bound the sensitivity by just limiting how many rows there are with the same ciphertext.

Mariana: Let’s move on.

##Interfaces for setMatchKey and getEncryptedMatchKey

Richa: We’ve fleshed out a proposal for these interfaces. Actually 3 APIs. setMatchKey, getEncrytpedMatchKey and getHelperNetworks.

setMatchKey() takes a blob. It’ll infer the match key provider origin and store it under that origin. The blob that’s sent in will be hashed and truncated to 45-bits. The first bit will indicate if it was set by a match key provider or not. 44 bits from the hash.

getHelperNetworks(). Return, what are the helper networks that the browser trusts. Assume this list won’t be too long.

Any questions yet?

Nick Doty: How long is this getHelperNetworks?

Martin Thomson: It’ll be specific to the browser. So if you’re using Chrome, it’ll be the same list every time.

Nick Doty: So it’s not user-specific. You can’t decide to trust or not-trust a helper party network.

Martin Thomson: You can opt-out of IPA in general. Potentially can disable helper network N by making that generate garbage, similarly to how opting out of IPA works.

Erik: Could also just identify the helper party network directly, and have it produce garbage if invalid.

Martin: When we went back and forth on this, we went with a site-ergonomic approach. They don’t have to know what all exists, particularly if this differs per browser.

Richa: getEncryptedMatchKey. Takes origin of the match key provider. It’ll take “event type”, and options. The last argument is basically which helper party network you want to encrypt towards. The way it works: you look up the match key, split it up into 3 shares, add the associated data, and encrypt the shares towards the public keys of the selected helper parties. If there was no match key set by the specified MKP, we can fall back to the “default” match key. The encryption will be cached, so that the same value is returned through the epoch.

Charlie: What happens if you don’t specify a helper party network? I saw that’s optional.

Martin: You’d just get the first one from the list. Haven’t worked through that.

Charlie: Maybe we should make it a required argument.

Erik: I don’t see a good reason not to make it required.

Martin: There is still value in having an “options” argument, but making it mandatory works for me.

Charlie: Options list which includes mandatory parameters? Easier to extend and update over time. Default params are hard to remove without compat issues.

Brian May: On the flip side, it’s more confusing what that field is doing.

Charlie: I’m just saying the design that enables us to be flexible with API design.

Ben: Agree we shouldn’t make it optional. Lead to compt issues. Could be ambiguous. One thing about options that I liked was supporting debugging. In that case, you may want to be able to pick a your own helper party networks. Would need to figure out how to support that. How has Chrome done it?

Charlie: We don’t support supplying your own encryption keys. I don’t see a huge problem having a debugging mode where you have a hook into “Get Helper Party Networks” and everything works smoothly from that. The interface for supporting that could have a bunch of different ways “CLI flag, dev tool”.

Brian: Ben’s approach could be an attack vector.

Ben: Yea, command line change would be more protective.

Charlie: Dev tools is pretty safe.

Martin: There’s a few things I want to point out here. Let’s look at storage first. Storage is keyed by current site and match key provider. You look there first and if it’s there you retrieve that value. This is important to avoid private browsing detection. I think we can build something that doesn’t operate through settings. If you’re the website who sets the match key, maybe there we can let you provide a helper party network. We can do a lot of debugging help with relation to information you already know. Possibly skip some steps.

Erik: I think the intention is not to get users to do things.

Martin: Imagine if a site sets a match key with PII. Process we are considering for set match key is to take the string provided, combined with a variety of things. Even with PII would require a secondary imaging attack.

Richa: Encryption part. Basically the browsers need to know the public keys of the helpers party networks. Could be updated automatically. Public keys can change.

Erik: Is there a way, only suggesting this if its less complicated, can we leverage something from certificate authorities?

Richa: Proposal says you’ll just provide a domain name.

Erik: Does it require downloading? I guess browser already has mechanisms for this.

Charlie: There is a little bit of a layering violation with TLS. In ARA we have a separate endpoint for clients to download from helpers. There are some projects that have done something like this. N-pub project piggybacked on TLS certs.

Martin: I missed the question.

Erik: Can we piggyback on TLS certs? We would rather just download certs at some point?

Martin: Helper parties will have keys that we need to encrypt towards. They don’t have to be in a certificate. They could be configured into browsers via the same mechanism that put the helper party networks into the browser in the first place.

Mariana: It was hard to use certs, as the uses of certs were narrowly specified.

Brian May: Trying to piggyback on anything like that makes complications down the road.

Martin: The server of the helper party can serve *over TLS* the key it wants to use. Consistency.

Erik: Do we worry about key-rotation challenges.

Martin: You do need to worry about it. If you require emergency key rotation we have a different sort of problem. Most browsers have ways of bringing configuration down to users in a rapid period of time.

Brian May: It’s a huge deal to the people that depend on these services.

Martin: Yes, but we are talking about *key compromise*, so you don’t really trust them anymore.

Brian May: We need a rapid fallback.

Charlie: Multiple helper party networks maybe acts as a fallback… might be able to think about alternatives. If there is a key compromise you want to stop encrypting data towards old key and start encrypting towards a new key.  I can share trust tokens approach. We check for new keys at startup and also at a 5-hour cadence. We do support having multiple keys on the client so that you can implement rotation.

Martin: This is the same sort of thing we have in Firefox. 5-hour revocation.

Brian May: Up to 5-hours, right?

Martin: Some trickle-on after that.

Brian May: The mechanism Charlie described is similar to what I had in mind.

Erik: 6 minutes over. Let’s call it.


## Attendance
- Erik Taubeneck (Meta)
- Benjamin Case (Meta)
- Ben Savage (Meta)
- Richa Jain (Meta)
- Alex Koshelev (Meta)
- Brain May (Dstillery)
- Thomas Prieur (Criteo)
- Charlie Harrison (Google Chrome)
- Sam Weiler (W3C)
- Mariana Raykova (Google)
- Christina Ilvento (Google Chrome)
- Michal Kalisz
- Andrew Pascoe (NextRoll)
- Alex Cone (Coir)
- Andy Leiserson (Mozilla)
- Mariana Raykova (Google)
- Nick Doty (CDT)
- Martin Thomson (Mozilla), Late
