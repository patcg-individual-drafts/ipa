# Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.

*  this week in the IPA call Daniel will present more on the OPRF implementation for scaling IPA.  You can read more here [https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md](https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md)


## **Attendance**

1. Benjamin Case (Meta)
2. Daniel Masny (Meta)
3. Erik Taubeneck (Meta)
4. Martin Thomson (Mozilla)
5. Alex Koshelev (Meta)
6. Artem Ignatiev (Meta)
7. Aram Zucker-Scharff (The Washington Post)
8. Daniel Masny (Meta)
9. Phillipp Schoppmann (Google)
10. Miguel Morales
11. Mariana Raykova (Google)
12. Andy Leiserson (Mozilla)


## Minutes 	

Scribe:  Ben Case

Erik: removing unknow and unresponsive zoom participant “Joo’s OtterPilot”

Daniel: slide based presentation for IPA [PRF-based Approach](https://github.com/patcg-individual-drafts/ipa/blob/main/3IPA.md). New approach to make IPA more scalable.  Some leakage but we can handle with DP. 

We have overall structure worked out which we’ll present

7 steps

* Query format: 
* Peparaating MPC
* Fake event integration
* PRF eval and grouping
* Per matchkey attribution 
* Aggregation
* Release Query Result

Maily will talk about fake event integration and PRF eval

Query format



* How much DP budget to spend, dp cap, bound of number of events per session and bound on sessions per user.  We can identify at helpers if events generated in same session, could have many. Bound on number of sessions is harder to enforce, could do on device, a bit more heuristic where this could have some drawbacks. But we can control well number of events per session, 
* Amount of events
* Event formant
    * Mathckey which is secret shares arithmetic, others boolean.  Open to suggestions 
    * Timestamp
    * Trigger bit
    * Breakdown key

Prepare MPC



* Invalide ciphertexts need filtered out
* Make sure shares are consistent, each helper receives two shares out of three.  Need to make sure share 3 is the same on two of the helpers.
* Delete events where decryption fails or inconsistent. Could lead to an attack vector from malicious helper to arbitarily delete reports, but we’re not too concerned right now about this
* Enforce a session bound.  In IPA first secret share and then encrypt.   We cache the secret shares but do fresh encryptions in same session but when you send to helpers they are able to identify these are the same secret shares and detect they are the same session.  So we can enforce bound – delete if there are two many submitted to meet teh bound. 

Fake event generation 



* DP leakage will need to be covered by fake events.  Generated at this step but needed later.
* Create fake matchkeys, every pair of helpers generate fake events.  Not clear if we take from the total budget or use other level we are comfortable with. 
* Create e fake matchkeys with k fake events.  Each pair of helpers generate. Let other helper know how many generated so they can initialize theirs to zero. 
* Run shuffle protocol. Total amount of events, + fake events.  To hide which are which we run mpc shuffle. We used share based shuffle “Secure graph analysis at scale” paper.   
    * Each two parties pick and apply permutation in the clear. 
    * Seems easy to shared as permutation is applied in the clear. 

Sharding



* Need a perfect shuffle.  Iterate over the list and assign to a random remaining open spot.  Each chosen with prob 1/n
* Question is how to shard.  Pretty simple, just assign each element to a shard and position within it.  Probability of a shard is proportional to remaining open slots in the shard.  Within the shard run previous algorithm where assign each with 

Phillipp: do we need a hard bound on the number of slots per bound?  Or just an average expected number? 

Erik: i think if you don’t have hard bound you don’t get a uniform shuffle. Don’t prevent the case all appear on only one shard. So 

Phillipp: could have a bound with high probability 

Daniel: if we say each pick uniformly the shard without considering how many remaining open slots, creates a bias. 

Phillipp: in which slot in a shard doesn’t matter. Since shuffle within.  That should be a uniform shuffle if unbounded shard size. 

Erik: ith’s spot goes to p(i)th slot.  Decompose into shard and slot on shard.  First shard is …

Phillipp: still not clear details 

Mariana: do you have analysis, still not obvious to me uniform shuffle

Daniel: yes, can share a proof.  Probabilities multiple and you get s_j to cancel and you get same probability as perfect shuffle

Phillipp: how to communicate number of free slots

Daniel: some load balancer to keep track of where they have been assigned

Martin: should be relatively easy to implement even if not all done ini one place.  Confident works for small numbers would be good to verify. Large number case may not be the same as small.  Doing this in the clear makes easier. 

Daniel: to Mariana’s question on which part

Martin: first one is “fisher-gates” – second one is too if you think of it as two dimensional space,  still drawing number between 1 and i

Daniel: moving on

PRF eval on each matchkey



* What we have gained is pesudonymn changes between IPA queries.  Could still argue unique per user. Revealing the PRF in the clear need to be careful – can count how many events exist per pseudonym but since we added fake events you only get a noisy version of this information. 
* Add fake events up to N_s * U_s but if there were a user with more than this bound on number of events. Helpers can detect but once it occurs some information is revealed. Could be hard to enforce on device for usability. 

PRF - DY  (see slide)



* G is EC generator.  PRF(k,x) = 1/(x+k))*g
* Generate random r_i, r_{i+1},  move to exponent 
* Compute shares of z = r(x+k)
* Reveal R and reconstruct z
* Haven’t done proof but should be secure in generic group model
* Reveal R and need to make sure reveals nothing about r
* Marian: distributed DY, we need to add a random mask in addition to multiplicative mask
* Phillipp: but on shares probably don’t need
* Phillipp: paper on how proving in generic group model.
* Daniel: we get malicious secure if malicious reveal and multiply. Don’t need any zk proof

Per matchkey attribution 



* Group by each user,
* Sort in MPC by timestamp
* Run attribution in MPC – different from previous IPA algorithm for attribution since per user
* aggregation  – could prun by fixing amount of attributed events per user
* Release query result. 

Ben: also attribution would also have sensitivity capping so DP noise added is correct amount

Daniel: other questions. 

Phillipp: bottleneck no longer on shuffling? Do you have experiment for this?

Daniel: main complexity is when apply permutation. What is done per element is pretty simple. Main concern was keeping it all in memory.  

Phillipp: and 2 rounds in total.  Happy this seems to work out 

Erik: biggest concern is adding now many events

Erik: depends how sparse and how far you go. 

Ben: each bin needs around 30-40 dummies. Probably 1M or so fixed cost

Daniel: malicious attacks to be prevented on device could have draw back on usability. Enforcing the cap absolutely on device might have drawbacks. 

Daniel:  other topics
