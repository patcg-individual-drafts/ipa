
# June 28, 2023 Virtual Meeting for PATCG/IPA

## Agenda

To add an agenda item, please open Biweekly Meeting Agenda Request Issue on the IPA Proposal GitHub repo.

One main agenda item
* Rust code walk through https://github.com/patcg-individual-drafts/ipa/issues/76









## **Attendance**



1. Benjamin Case (Meta)
2. Alex Koshelev (Meta)
4. Craig Wright (Google)
5. Nick Doty (CDT)
6. Andy Leiserso
7. Andrew Pascoe (NextRoll)
8. Nigel Gay (NTU)




## Minutes

Alex:

Two main modules

* Protocol
* Infrastructure

Standard Rust organization style

Will describe each module

Finite field. Currently use 32bit prime.  Also a Galous field for binary

Secret sharing module to represent secret shares.  Semi-honest and malicious. Malicious needs to carry additional information.  Separate modules for semi-honest malicious

Protocol module. Where IPA lives.  Some primitives used across all.  Reveal, reshare, these are simple sub protocols.



* Attribution
* Modulus conversion
    * Convert formats
* Core IPA
    * Entry point for  IPA.
* PRSS: secret share random number generators
* Sort module
* Step module that provides functionality to uniquely identify each communication that occurs between helpers.

Infrastructure modules



* Helpers –- the front door of Infra.
    * Send and receive functions
    * Data in the buffer gets sent to the network layer, and the receive process is the same. Call infra method to receive for step.

Craig: using raw sockets? Not rpc, or other frameworks

Alex: no we use raw HTTPS,  want fewer layers for latency, want more control. We use our own binary serialization formate. We open a stream for each circuit and whether HTTP2 or 3 and drive data to that stream. For each helper are two streams to the other helpers. We write to till no more to send

Craig:  so two way between all helpers

Alex: yes

Craig: what speedup by removing the framework?

Alex: not a formal analysis, switched early in the stage but

Craig: more a perceived that the framework was adding overheard?

Alex:  IPA serialization is easy, maily small field values.  Pack them into a large array and send down. No custom structs to take advantage of thrift. So complexity of adding thrift we couldn’t justify instead of just raw bytes

Gateway module: front door for sending and receiving.  We use async Rust. write some code, call .await() which will wake up when finished.  Makes easier for multithreading but more complex for networking

src/net:: use HTTP1 and 2 right now, in the future maybe HTTP3.  There is a client module for how to create a query that the report collector calls.  Server module that listens to a port and handles https, and then sends to helper code.  Simple but enough for us right now

Hpke: use to encrypt matchkeys

Query: workflow module, maintains the state of the query

Lots of test modules.

Questions?

Craig: in the way of testing, how approaching? Unit tests? Functional tests?

Alex:  We try to be diligent; unit tests, enforce some level of unit testing, so good coverage there. Also functional testing.  Run IPA end to end. Create a new process for each test, create three helper processes, communicate using TLS, run full IPA end to end. We also have concurrency testing for async Rust.  These are like fuzzy testing - using a randomized scheduler to schedule work in random order and see if anything breaks.  What we don’t have yet but would like is long running tests and this would close the gap on performance testing.

Alex: where we are now



* We are doing a synthetic in-market test.  Fixing issues.  Capable of running up to 1M records but latency not acceptable yet but we know how to fix in the implementation. We’ve run with three helpers at 200Mbps,

Craig: running different countries?

Alex: we have tested on single cloud



* … 200Mbps is not great but we are still working to improve. Looking for countries that are geographically close but

Nick: 9hrs doesn’t seem too bad for Adv?

Alex: mainly a network throughput issue. We can go much faster.  We are also only using one core. So not moving to socket fast. This is also for just 1M records, far from our expected goal of 1B.

Ben: We are still early on optimizing the performance running between actual servers. Expect we’ll get to 10M in 3 hrs next half before turning to focus on scaling through the use of many machines.

Nigel: multi-core timeline?

Alex: we created with async but didn’t make use of parallelism. When we do a step with pin to a core, most CPU work is AES in IPA which is highly parallelizable so most of our protocol waits for AES and waits for I/O.  so we want to create more in parallel to better saturate the buffer

Nigel: Could I use cuda? GPU?

Alex: maybe for multiplication, but we haven’t gone this direction.  Computation isn’t what we expect to be the most expensive, rather I/O.

Amit: where can we find documentation for protocols.

Alex: We have a paper for IPA.

Ben: paper as well as end-to-end doc.  The code also links to papers and has some documentation.  There are some places where the paper is out-of-sync with the code, but the documentation in the code should be closest to what is implemented, though to get a big picture of what is happening the paper or end-to-end doc are good.

 [https://eprint.iacr.org/2023/437](https://eprint.iacr.org/2023/437)

[https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md](https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md)

Craig: AES dominates the computational cost?

Alex: This is for randomness generation.

Craig: beaver triples?

Alex: Not beaver triples but need to generate coordinated random numbers across helpers for the secret sharing

Craig:   infrastructure is running on single VMs? Kuberneties? Multiple pods?

Alex: running on bare metal as docker image.  Don’t use Kuberneties. … we have distributed keys for communication authentication.  Once we start scaling up it will be a question what system we use for that.
