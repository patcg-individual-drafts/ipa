# Agenda

To add an agenda item, please open _[Biweekly Meeting Agenda Request Issue](https://github.com/patcg-individual-drafts/ipa/issues/new/choose)_ on the IPA Proposal GitHub repo.

* We will plan to have a working session with whoever wants to join on the steelmaning the comparison doc from TPAC with a focus on the IPA column.  Particularly there was some feedback to break out the security section into more cases. Links:
1. original comparison doc [https://docs.google.com/document/d/1oMe3Q7DMG3xzl-peIdq6voVD4PKD822-W4nf4ak7s2E/edit](https://docs.google.com/document/d/1oMe3Q7DMG3xzl-peIdq6voVD4PKD822-W4nf4ak7s2E/edit)
2. steelman version [https://docs.google.com/document/d/127HgUw8j5G59zOd0PmMZNXmhIETXHPu_Ub0_JIv0YV8/edit](https://docs.google.com/document/d/127HgUw8j5G59zOd0PmMZNXmhIETXHPu_Ub0_JIv0YV8/edit)
* 


## **Attendance**

1. Benjamin Case (Meta)
2. Erik
3. Daniel
4. Phillipp
5. Mariana
6. Martin
7. Alex
8. Andy


## Minutes 	

Scribe: Erik and Ben 

[Note: switching gears to the OPRF topic given attendees]


1. Daniel: 
    1. [sharing a doc, will publish before the next meeting]
    2. At the start of the MPC, helper parties decrypt events, and check for consistency across helpers.
2. Erik: event clean up happens in either approach
3. Daniel: unclear if this is needed in Mariana and Phillipp’s version.
4. Mariana: There isn’t clean up to do for that version.
5. Daniel: 
    3. Then we generate fake events. When we reveal the OPRF of the match key, we reveal how many users there are with 1 event, 2 events, etc.
6. Mariana:
    4. Yes, a DP histogram.
7. Daniel:
    5. Generate random events for each of these buckets.
    6. Here it’s crucial that we have an upper bound, otherwise we can’t create fake events for an unbounded number of events.
    7. We have to values: number of events within a session (easier to bound) and number of sessions per user (hard to estimate)
    8. If we fail to estimate that, we may result in leakage.
8. Mariana:
    9. Assuming we can compute that sensitivity in the MPC with the current approach?
9. Daniel:
    10. We don’t leak this histogram in the current approach, so it’s not needed.
    11. Once we’ve generated the fake events, we need to shuffle.
    12. After we’ve shuffled, we reveal the OPRF, and then can group by users.
    13. If there is any group with N<sub>s</sub> * U<sub>s</sub> we can report a privacy violation, but we can’t revert that leakage.
    14. In order to evaluate the OPRF, we can do something like g^{1/(mk + k)}
    15. Some details on what is sent…g^r and something times the share…
10. Mariana: does it take advantage of honest majority?
11. Daniel: use three party protocol; could do in two party setting, one party for g^r and another g^{r+k}
12. Mariana: will do proofs or use honest majority to avoid?
13. Daniel: for multiplication use malicious, proof for same r in g^r and multiplied by shares 
14. Philipp: Question on privacy violation event. Does it mean one of the servers cheated?
15. Daniel: Could just be that the heuristic failed. You know how many event you have per session, but not how many sessions per user
16. Martin: sessions could be capped on device, but if we cap to 100 per device, but a person has many devices then would be more.
17. Phillipp: cross-device
18. Martin: even in single device case, then refresh the matchkey.  If same device then we can cap, 
19. Phillipp: if we could sync matchkeys we can sync session counts.
20. Martin: yeah, but more chatty 
21. Daniel: MKP was an issue to bounding events per user
22. Erik: shuffle step – we want to do OPRF because we want to scale horizontally, need to shuffle in this setting as well. Could cause weakened security.  We can chat more about this in a bit
23. Mariana: shuffle was a big motivation for our earlier proposal 
24. Daniel: finishing this doc first.  Do aggregation but still need to sort by timestamp. 
25. Mariana: doing this per user may not be that bad
26. Daniel: Some tradeoffs to consider, but yea, events per user will be a smaller set. Not sure if it saves a lot on communication complexity.
27. Phillipp: Yes, and they can be done in parallel.
28. Daniel: 
    16. Then you run aggregation, and that’s simpler as well. Not too different but a little optimized. Boolean shares seem to be better because it’s easier to cap them.
    17. Biggest bottleneck is shuffling. Currently doing it in honest majority setting, can have two parties pick a permutation, and you iterate that three times so that each party only knows one of the three permutations.
    18. Issue with this is that you need to keep all events in memory. 
29. Martin:
    19. Current bottleneck is on the order of a million events.
30. Mariana: why need in memory? Not trying to prevent hiding access patterns
31. Martin: are we leaking through timing?
32. Mariana: three parties – each party has nothing to hide as they know what shuffle they are applying.
33. Martin: right, we haven’t experimented with putting on disk, concerned about time
34. Erik: also nothing leaked by sharding across machines when shuffle is know
35. Daniel: as long as not doing per shard shuffle
36. Erik: two stage random assignment
37. Phillipp: may not get uniform permutation doing it that way
38. Ben
39. Mariana: doesn’t get uniform shuffle but done
40. Martin: If you have two groups, there’s some chance that everything ends up on one shard. Do you need to add noise twice?
41. Erik: not sure why all on one shard a problem
42. Martin: 
43. Erik: three helpers each applying a random shard, then stream out of those, my intuition is you get all permutations, but would need to check
44. Mariana: goal is to parallelize the shuffling
45. Eirk: goal of all is horizontal scale, map-reduce style 
46. Mariana: not sure about uniform shuffle, but not sure you need it either
47. Erik: suppose 1B events with 1k shards so 1M each.  All helpers know mapping.  Event count to shard. 
    20. Shuffle each shard
    21. Same as one query with 1M events, 1k queries with 1M events?
48. Daniel: depends on DP mechanism to cover imperfect shuffle.  Add fake events inside buckets may not work,
49. Mariana: eventually doing sharding so we can release PRF values, if you see all the values are on same shard but know where things went before shuffle may violate 
50. Mariana: goal is to assign to shards based on OPRF value
51. Erik: would reveal OPRF after we’ve added dummies, then reveal OPRF, might be on different shards at begining but then go to correct shard
52. Mariana: yes, but not sure the construction will be DP
53. Daniel: probably not enough to add fake events initially, may need to randomly assign to shards and create more dummy events 
54. Erik: some HW to figure out 
55. Mariana: question if is a DP mech, will need to look at new papers that can do without full shuffle. Sent in slack [https://arxiv.org/abs/2305.10867](https://arxiv.org/abs/2305.10867)
56. Daniel: 
57. Erik: impact on sensitivity?
58. Mariana: will have to check. Main different with ours is if you share index or encrypt. Need to encrypt shares anyway so need to rerandomize, shares doesn’t save you so much.  Do distributed evaluation. 
59. Daniel: we wanted SS to save on PK operations, shuffle of ciphertexts, want to have a non-maliable matchkey so can’t split a user into two so can’t violate per user sensitivity cap.
60. Mariana: at what stage?
61. Daniel: if mk with rerandomizable encryption, RC could just add 1 to mk underlying, 
62. Mariana: but encrypted to helpers with another layer? 
63. Daniel: probably non-maliable on device and then rerandomizable, but can’t do hybrid encryption with AES, need whole ciphertext with 
64. Mariana: can’t encrypt shares with AES eithere
65. Daniel, no but everything SS, no rerandomizing ciphertext. 
66. Mariana: so maybe this shuffle in MPC is more complicated. 
67. Daniel: yeah need to be careful to get malicious
68. Phillipp: shuffle also works on shares 
69. Daniel: paper that uses set equality check. Different malicious secure shuffles in honest majority, not bad. Can send papers
70. Daniel: we were concerned about pk encryption and how expensive.
71. Mariana: protocol not clear without seeing details of shuffle on shares. 
72. Phillipp: reranomizable large messages, use LWE
73. Ben: not large messages per user, 
74. Phillipp: then can use EG
75. Daniel: 
76. Mariana: why large message
77. Daniel: encrypt non-maliable then encrypt
78. Mariana: i thought other way around
79. Mariana:
80. Phillipp: issue of exphiltrating and using over in a different query. 
81. Daniel: open to other ideas 
