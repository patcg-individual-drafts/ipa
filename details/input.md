# Interoperable Private Attribution wire format


This documents provides clarification on the format IPA parties use to submit queries. 

## Query

IPA query consists of a mix of source and trigger events obtained from one or many source and trigger websites. 
**Query size** is determined by the number of events included within a single query request. 

It is desirable for report collectors to submit large queries as it brings more utility and saves cost, 
therefore it makes sense to optimize the query format on the wire.

The following sections propose the format that is space-optimized at the expense of being more complicated to assemble. 

## Assumptions

* Report collector use HTTP over TLS to send queries to helper party networks.
* Number of events within a single query is between $10^6$ and $10^9$. 
* Number of unique source and trigger websites is significantly lower than total number of events in the input set.


## Format considerations

It is worth to look at a single event first. To be concrete, this assumes match key to be a 40-bit length byte string,
but this does not change the fundamentals. It is described in more details 
[here](https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md#generating-source-and-trigger-reports-by-the-report-collector).

A single event consists of encrypted replicated shares of match key share, replicated shares of event data and additional 
authenticated data. Event data varies depending on whether it is a source or a trigger event. Authenticated data is used
to decrypt the shares of match key.

Two things that consume the most space on the wire are **site registrable domain** and **match key provider origin**. 
Both are ASCII strings, potentially large, that each event must refer to in order for helper parties to correctly obtain 
the plain text shares.

The biggest savings from the custom format come from making each query to carry only one copy of unique site domain
and match key provider origin strings. This proposal suggests building two lookup tables (one for each entity) on the 
caller site


## Proposed format

Each query request must carry the following information: 
```text
[match key][event data][authenticated data][match key][event data][authenticated data]...
```

This proposal suggests splitting query requests into two sections: lookup tables section for match key providers and 
site domains and payload section with encrypted replicated shares of match key and event data. Each encryption is annotated
with a unique id pair that points to site and match key provider strings that are used to authenticate the match key
encryption.

```text
.lookups
[site origin 1][site origin 2]..[site origin N]
[match key provider 1][match key provider 2]..[match key provider M]
.payload
[site origin id][match key provider id][authenticated data][match key][event data]
[site origin id][match key provider id][authenticated data][match key][event data]
...
```

where `id` is the index of site origin or match key provider inside the lookup table.

It is natural to assume $M \ll N$, so fewer bits is required to encode match key provider index. 

The total number of site domain entries inside the lookup table must be less than $2^{32}$.
The total number of match key provider origin entries inside the lookup table must be less than $2^8$. 


### Metadata

Every query request must specify several parameters to the helper parties that impact the size of the payload.
These parameters are sent in the [header](https://www.rfc-editor.org/rfc/rfc9110.html#name-header-fields) of HTTP request.

The list of supported parameters include:

| Header name      | Type                         | Description                            | Accepted values | Default? | Mandatory? |
|------------------|------------------------------|----------------------------------------|-----------------|----------|------------| 
| `x-ipa-field`    | US-ASCII encoded string      | Field type used to secret-share values | `fp32`          | No       | Yes        |
| `x-ipa-query`    | US-ASCII encoded string      | Desired query to run in MPC            | `ipa`           | `ipa`    | No         |
| `x-ipa-version`  | single byte unsigned integer | Version of the request                 | `1`             | No       | Yes        |

### Lookup table

The site origin lookup table consists of RLE unique site domain values and unique match key provider origins, encoded as 
ASCII strings. Each section is terminated with a single zero-valued byte.

For example, a query that has two unique site origins and one match key provider will have the lookup table encoded as 
follows:

```text
15www.example.com7docs.rs\016matchkeyprovider
```

All entries are implicitly zero-indexed and the unique index of each entry is used inside the payload to indicate the
site origin all events within that group are associated with. 

In the example above, `www.example.com` would have index 0 and `docs.rs` would be associated with the index 1. 

### Payload

Payload section carries the match key encryption and event data along with additional authenticated data not included
in the lookup section. It includes one or more event encoded as follows:

1) The unique index of the site origin for this event encoded as four-byte integer in big-endian byte order. 
 This index must be unique inside the payload group and be a valid index from the lookup table.
2) The unique index of the match key provider origin for this event encoded as single-byte integer. 
3) The single-byte key identifier from the key configuration for the helper party.
4) The current epoch, encoded as a two-byte integer in big-endian byte order. 
This index must be unique inside the payload group and be a valid index from the lookup table.
5) The [HPKE](https://datatracker.ietf.org/doc/html/rfc9180) of replicated match key shares:
   1) The 32 byte [encapsulated key](https://datatracker.ietf.org/doc/html/rfc9180#section-4) encoded in big endian byte order.
   2) The PKE of match key shares encoded in big endian order. Using 40 bit match keys will result in 80 bit encryption, etc.
   3) The 16 byte authentication tag encoded in big endian byte order.
6) The timestamp of the event encoded as three-byte integer in big-endian byte order. Timestamp of the event is represented as
number of seconds since the beginning of epoch. 
7) The secret-shared value of the trigger bit, encoded as two [field](#metadata) values in big-endian order.
8) The secret-shared value of the trigger value, encoded as two [field](#metadata) values in big-endian order.
9) The secret-shared value of the breakdown key, encoded as two [field](#metadata) values in big-endian order.

## Simulation

It's worth simulating various distributions of events between unique site origins to estimate potential savings on the wire. 
Intuitively, the biggest gains can be achieved when relatively few site origin have large number of events associated with them. 

Note: The following estimations ignore the TCP/IP/Ethernet frame overhead as it remains the same regardless of the format chosen
by the implementations. 

The following simulation assumes each event to take **112 bytes** on the wire, including encryption overhead 
(see [encryption](.encryption.md)) and site origin to be a random 25-160 byte ASCII string. The overhead of sending
additional authenticated data is ignored except for site domain. The assumption is match key provider set per query
is small and while an additional lookup table is warranted, the relative overhead won't be visible in the simulations.

### 1M input

When input size is 1M events, total size without any optimizations is **194 MiB**. 

| Unique site origins | Optimized size |
| --- | --- |
| 1 M | 194.5 MiB | 
| 500 k | 150.7 MiB | 
| 250 k | 128.7 MiB | 
| 100 k | 115.6 MiB | 
| 50 k | 111.2 MiB | 
| 20 k | 108.6 MiB | 
| 10 k | 107.7 MiB | 

### 1B input

With 1 billion events, 
savings between 10K and 1M unique site origins become marginal. 
Without any optimization, 1B events will take **190 GiB**.

| Unique site origins | Optimized size |
| --- | --- |
| 500 M | 147.2 GiB |
| 100 M | 112.9 GiB |
| 10 M | 105.2 GiB |
| 1 M | 104.4 GiB |
| 500 k | 104.4 GiB |
| 250 k | 104.3 GiB |
| 100 k | 104.3 GiB |
| 50 k | 104.3 GiB |
| 20 k | 104.3 GiB |
| 10 k | 104.3 GiB |


Space gains vary from 30% to 50% assuming the number of unique websites lies between 10% to 30%.


