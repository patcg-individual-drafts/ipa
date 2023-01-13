# Interoperable Private Attribution Encryption

Interoperable Private Attribution (IPA) relies on the encryption of data in
order to meet its security and privacy goals.  This document describes how data
is protected by encryption in IPA.


# Communications Security

IPA uses TLS ([RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446)) for the
protection of all network communications.  More concretely, this will involve
the use of HTTPS ([RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110)),
with Web PKI authentication for servers.  Client authentication might be
required in some cases, such as between helpers.

Formally, this HTTPS only applies to those places where specifying
interoperability requirements are specified, which is:

* Between a record collector and the helper party network.

* Between helpers in a helper party network.

The expectation is that HTTPS or equivalent protection is used in some other
interactions, as some privacy or security goals might not be achieved if data is
not adequately protected, but this is out of scope for this document.  Other
documents might specify expectations about how data is handled.


# Match Key Protection

Though TLS is a key component, IPA relies on an IND-CCA secure public key
encryption scheme to protect match keys.  When a site requests an encrypted
match key, the user agent generates three objects that are encrypted toward each
of the three helpers ($P_1$, $P_2$, and $P_3$).

HPKE ([RFC 9180](https://datatracker.ietf.org/doc/html/rfc9180)) is used to
protect match keys.  HPKE provides an IND-CCA2 secure scheme that combines
asymmetric and symmetric cryptography.


## Helper Key Configuration

Each helper party publishes an HPKE key configuration using the format described
in [Section 3 of Oblivious
HTTP](https://ietf-wg-ohai.github.io/oblivious-http/draft-ietf-ohai-ohttp.html#section-3). This
configuration includes a key identifier, an asymmetric key encapsulation method
(KEM) identifier, and a set of acceptable symmetric algorithm identifiers.  Each
symmetric algorithm is identified by a pair of key derivation function (KDF) and
authenticated encryption with associated data (AEAD) identifiers.

User agents will define a process for retriving key configurations from helpers.
As the set of helper networks that are trusted by each user agent is likely
small and finite, with each network comprising three helpers, it might be
possible to periodically retrieve this information.  User agents could instead
retrieve information on demand, but this could create unwanted side channel
information.

This process assumes that a helper advertises just one key configuration at a
time, though multiple configuration can be active during the period of time that
events are aggregated.


## Match Key Encryption Process

A site can request the generation of an encrypted match key.  The inputs to this
process are:

* The origin ([RFC 6454](https://datatracker.ietf.org/doc/html/rfc6454)) of the
  site making the request.

* The current time, specifically the current epoch.


### Obtaining Key Configurations

The user agent then determines which helper party network will receive the
information.  The site either tells the user agent which helper parties it has
committed to for the current epoch, or it identifies a helper party network.
The user agent should already know these parties, so it can obtain information
about the helper party network:

* The identity of the three helper parties in the site's chosen helper party
  network.

* The key configuration for each helper party.

As there a limited number of helper parties that the user agent trusts, it
should be possible to keep copy of this information and refresh it periodically.
Therefore, this should be a simple lookup for the user agent.

Note that the site is required to [commit to a helper party
network](https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md#commitments)
for each epoch.  However, the user agent doesn't need to enforce that.  The helper
party networks (all of them!) are trusted by user agents to check that they are authorized to
receive events in a given epoch for the site.  At the start of each epoch, the
helper parties can check in with each of their customers and take a copy of
their current commitment.  Then, the helper parties can reject any attempt to
provide them with an event if the commitment they saved for the corresponding
epoch does not include them.


### Replicated Secret Sharing

The user agent then retrieves a match key.  This process always succeeds, but it
might result in a random value being selected.  The details of this process can
be found in [TODO](about:blank).

From this, it creates three binary sharings ($mk_1$, $mk_2$, $mk_3$) of
the match key by generating two random values (see [RFC
4086](https://datatracker.ietf.org/doc/html/rfc4086)), setting the first two
shares to these values, then setting the third to the exclusive OR of the match
key and the two random values.

```python
mk[1] = random()
mk[2] = random()
mk[3] = mk[1] ^ mk[2] ^ match_key
```

The user agent then allocates two of the three shares to each helper, such that
each share is sent to two different helpers.  For example, $P_1$ receives $mk_1$
and $mk_2$, $P_2$ receives $mk_2$ and $mk_3$, and $P_3$ receives $mk_3$ and
$mk_1$.  This is a particular form of replicated secret sharing that lends
itself to efficient computation in an honest majority setting.

<aside>

A note on notation here.  In a few places, it is necessary to describe helpers
or shares relative to a current helper.  In this case, we will use $P_i$ to
refer to the current helper and $mk_i$ to refer to the corresponding share.
Helpers are formed into a ring, with higher-numbered helpers to the right of the
helper immediately preceding them.  Thus, the helper to the right of the current
helper is identified as $P_{i+1}$.  As this is a ring, the helper to the right
of $P_3$ is not $P_4$, but $P_1$.  Similarly, the previous helper is identified
as $P_{i-1}$ and the helper to the left of $P_1$ is $P_3$.

In this view, the replicated secret sharing we use has each helper with a share
in common with the helper to its left ($mk_i$) and a share in common with the
helper to its right ($mk_{i+1}$).  While it would be equally valid (and
indistinguishable from this) if we instead used $mk_{i-1}$ and $mk_i$, we use
$mk_i$ and $mk_{i+1}$ throughout.

</aside>


### HPKE Context Creation

The two values destined for each helper are then concatenated and encrypted
toward that helper using HPKE.  The sender and receiver contexts used by HPKE
are constructed using an input that captures critical contextual information.

The `info` input for HPKE shall include a distinguishing sequence that is
composed from:

1. The fixed string "private-attribution", encoded in ASCII, terminated with a
   single zero-valued byte.

2. The [ASCII serialization of the helper party
   origin](https://datatracker.ietf.org/doc/html/rfc6454#section-6.2),
   terminated with a single zero-valued byte.

3. The [ASCII serialization of the current site
   origin](https://datatracker.ietf.org/doc/html/rfc6454#section-6.2),
   terminated with a single zero-valued byte.

4. The single-byte key identifier from the key configuration for the helper
   party.

5. The current epoch, encoded as an two-byte integer in network byte order.

This produces the following process in pseudocode:

```python
def ipa_info(helper_origin, site_origin, key_id, epoch):
    return concat(encode_str("private-attribution"),
              ascii_origin(helper_origin),
              encode(0, 1),
              ascii_origin(site_origin),
              encode(0, 1),
              encode(key_id, 1),
              encode(epoch, 2))
```

### Encryption

The encryption process is applied by the user agent by creating a sender context
that uses the helper public key, the `info` string, and - implicitly - a choice
of KDF and AEAD from the helper configuration.  This context is used to seal a
single message that is the simple concatenation of the two shares for that
helper and empty associated data.  This is concatenated with the encapsulation
key to produce the message for that helper.

This process is applied for each helper, as follows:

```python
info = ipa_info(helper_origin, site_origin, key_id, epoch)
enc, sctxt = SetupBaseS(pkH, info)
ct = sctxt.Seal("", concat(mk[i], mk[i+1]))
enc_mk = concat(enc, ct)
```

If match keys are not a whole multiple of 4 bits in length, the combined match
keys will need to be padded to a whole multiple of 8 bits.

The overall process produces an output that consists of an epoch and three
objects that each comprise an encrypted match key (as a sequences of bytes), the
helper origin, and the helper key identifier.  A site can store this entire
structure in a log, though it might be possible to eliminate some fields as they
will be identical to adjacent items in the log (the helper party origin).

For the remainder of the epoch, the user agent SHOULD provide the exact same
answer to a site that requests an encrypted match key.  The obvious way to
achieve this is to store the encrypted values in site-specific storage, so that
it can be later retrieved.  Alternatively, a user agent could use a pseudorandom
function (PRF) for this purpose, seeding it with the site origin and epoch,
provided that the secret that is used is properly protected.


### Decryption

Helper parties can reverse this process by retrieving the private key that
corresponds to the identified public key and creating a receiver context using
the secret key, the encapsulation key, and the same `info` string.

```python
enc, ct = parse(enc_mk)
info = ipa_info(helper_origin, site_origin, key_id, epoch)
rctxt = SetupBaseR(enc, skR, info)
request, error = rctxt.Open("", ct)
```


## Overhead and Size

With a typical HPKE configuration of "`DHKEM(X25519, HKDF-SHA256)`",
"`HKDF-SHA256`", and any AEAD with a 16-byte tag (such as "`AES-128-GCM`" or
"`ChaCha20Poly1305`"), this process produces 48 bytes of overhead per helper,
per encryption.  This does not include the site origin (variable), key
identifier (1 byte) or epoch (2 bytes), which are repeated across multiple
items, which should mean that their cost can be amortized.  Other information,
like the helper party origin, is expected to be implicit, so it should not
require transmission.

For a 64-bit match key, this means that it is possible to represent each
encrypted match key in just 240 bytes provided that values that are shared
across multiple values are applied to multiple items.

This is larger than typical identifiers used in tracking cookies, which only
need to be long enough to allow for a unique allocation to each person.  These
can therefore be as little as a single match key (less than 8 bytes), but are
typically 16-20 bytes long in practice.


# Query Encryption

A record collector submits queries to a chosen helper party.  This uses HTTPS,
but this is not sufficient because the content of a query is secret shares that
are intended for each of three helper parties.

Each query requires that the record collector provide multiple items or records.
Each record is split into three components, each that is sent to one of the
three helper parties.  Each component includes one part of the encrypted match
key (which does not necessarily require further encryption), information
necessary for decryption (the origin of the site where this match key was
requested, the key identifier used in match key encryption and the epoch), and
supplementary information provided by the record collector: event type (source
or trigger), the trigger value, the breakdown key, and attribution constraint
ID.

Of these fields, the current design only permits the decryption information to
be directly exposed; all other values are secret shared.  Decryption information
is also likely to be stable over time, so using a form of run-length encoding
for these values should make the overall encoding more efficient.


## Query Submission Options

It is necessary to separate the process of creating a query from the process of
uploading records for that query.

The query creation process is not particularly relevant to this discussion.  We
shall assume that the record collector creates a query somehow.  We assume that
there is some entity (or set of entities), likely one of the helper parties,
that is authorized to create a query and able to coordinate the process.

At the highest level, submitting data for a query can follow two basic patterns:

1. Query creation produces a record submission endpoint at each of the involved
   helpers.  The record collector submits records to each of the helper parties
   separately.  This approach is relatively simple as it can rely on the
   protections offered by TLS to ensure that record data is only visible to the
   correct helper party.  However, it requires that helpers all expose a public
   endpoint capable of accepting data for active queries.

2. Record submission all flows through a single entity, which might be a helper
   party.  This might allow record submission to be coupled to query creation,
   which simplifies the query process.  The single entity might be a helper
   (like the [PPM leader
   role](https://dt.ietf.org/doc/html/draft-ietf-ppm-dap#name-system-architecture)).
   However, it means that TLS protection is not sufficient.  Data that is
   destined for helper parties needs to be encrypted so that the receiving
   entity is unable to see it.

We originally intended to adopt the latter model.  Having a single point of
contact allows for an asymmetric deployment of helper parties, where some helper
parties only need to perform basic tasks.  However, there are practical
considerations that push toward separate submissions.

In a model where all records are submitted to the same endpoint, there are
conceptually multiple flows of data, one to each helper party.  These flows
could be delivered sequentially or interleaved.

Note that any architectural decisions might be distinct from business
arrangements.  A single point of contact might be desirable for things like
simplifying billing interactions.  This could be provided with either model.


### Interleaving

Fully sequential delivery is likely to produce some difficulties for helper
processing, because no multi-party computation can occur until all helper
parties have their shares.  A sequential upload delays processing until more
than two thirds of the records are uploaded.  For a large dataset, that is
undesirable.

The question then becomes how to best interleave records.  Interleaving at the
transport layer, by submitting requests as separate flows, provides strong
parallelism and a simpler interface, but might be more error prone.  If the
separate flows do not contain exactly the same set of records in the exact same
order, the output of a query could be spoiled.  All records from the point at
which flows diverge could be spoiled, with the effect being that they contain
values that are effectively random.

There are ways to detect loss of synchronization, but most only detect an error.
Adding cross-check points that span all helper parties, where hashes of the
records thus far are shared with all helpers, which can validate that both their
own and their peers have inputs that hash correctly.

Replicated secret sharing offers a simpler option: helpers can also calculate a
running hash of shares and periodically compare that with their peers.

Interleaving of records for different helper parties in the same stream ensures
that data is more tightly synchronized and might offer less risk of corruption,
but it complicates the data format considerably.  There are also very few
opportunities for size savings.  The only datum that might be shared between the
parallel flows of data to each helper party is the epoch, which is small and
changes only infrequently.


## Proposal

This proposes that the protocol use a separate flow of data for each helper
party.

The simplest design has data sent directly from the record collector to each
helper party.  This requires a three stage query process:

1. In the preparation stage, a query is created.  This first stage establishes
   parameters for the query and provides the record collector with an endpoint
   where data can be submitted to each helper party.

2. In the upload stage, the record collector concurrently submits data to all of
   the helper parties.  The helper parties then execute the MPC protocol, which
   can commence as soon as the first data becomes available.

3. In the final stage, shares of the results are published by each helper and
   retrieved by the record collector.  The record collector combines these to
   obtain the results.

This system only depends on the protections afforded by TLS.

To help manage the risk that separate flows lose synchronization, a system for
exchanging periodic checksums between helper parties will be developed.  Helpers
will need to agree on the hashing algorithm and how often to publish
checkpoints.


### Alternatives

If the goal is to have all flows served by a single helper party, then this is
possible without fundamental changes.  The endpoints for all helpers can be
served by the one entity.

Any flow that is intended for another entity will need to be encrypted toward
its intended recipient with an added layer of protection.

There are no pre-existing encryption schemes that are a perfect fit.  Any scheme
needs to support incremental processing.  An HTTPS CONNECT tunnel might work,
but that means that the single contact point needs to operate as an HTTP
intermediary.  [RFC 8188](https://datatracker.ietf.org/doc/html/rfc8188)
provides for incremental processing, but does not integrate IND-CCA protections;
though [RFC 8291](https://datatracker.ietf.org/doc/html/rfc8291) does, a more
complete design is still needed.

A more modern design based on HPKE might be preferable.  Details for this
additional encryption can be arranged later.
