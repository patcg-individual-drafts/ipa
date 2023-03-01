# Security and Privacy Questionnaire

This contains brief answers to a bunch of standard security and privacy
questions as it relates to [IPA](./IPA-End-to-End.md).  However, this is a case
where the answers to these standard questions are largely unsatisfactory.  IPA
is specifically designed to provide cross-site information in more or less
direct contravention of accepted practice.

It is best to summarize IPA from the relevant perspective first.  This summary
brings out important details from the explainer, as well as acting as a short
primer.


## IPA Summary

The proposed IPA API (palindrome, whoa!) provides sites with the ability to
request an encrypted match key.

A match key is an identifier that is intended to uniquely identify a person,
though it could - depending on implementation choices in user agents - only
identify a user agent.

IPA allows any site to set a match key: the idea is that a site can provide a
match key using knowledge they have that can connect a user to multiple user
agents.  Sites can request that the user agent use the match key provided by any
other site.  The user agent provides a fallback value if no value has been set.

An encrypted match key is secret-shared version of a match key that is encrypted
toward each of the three entities that form a selected helper party network.

Provided that two of the three parties that form the helper party network do not
reveal the values they receive to each other and they faithfully execute the
defined MPC protocol, the value of the match key is never revealed to any
entity.

IPA defines an MPC protocol that provides sites with an aggregated report that
can be used for attribution.  The MPC system chosen guarantees *malicious
security* in the *two out of three honest majority* setting.  In this setting,
both privacy for inputs and security against tampering are guaranteed as long as
two of the three helper parties faithfully executes the protocol.  It takes two
corrupted or malicious helpers that actively work together to access the input
data provided about users or to spoil the output of the computation.

User agent implementers, on behalf of their users, need to select helper parties
that can be trusted to correctly execute the protocol and to only reveal the
output of any processing they perform.  In addition to the cryptographic
protections built into the MPC protocol design, the specification recommends
that helper parties be bound by contractual terms with user agent
implementations to execute the protocol correctly.

Each top-level browsing context receives a unique encryption and secret-sharing
of the chosen match key, which ensures that the information visible to the site
or individual helper parties does not reveal any correlation between users.  A
top-level context can make its value available to nested contexts; nested
contexts do not receive a different value.  This value is retained by the user
agent in site-specific storage; subsequent requests result in the same value
being returned.


## Key Challenges

There two major components to this work that require special attention from a
privacy perspective:

1. This proposal uses information - match keys - that might be used to perform
   cross-site tracking.  The API allows any web site to request and receive this
   information from user agents.  The proposal includes a number of measures
   that are designed to protect this information.

2. The aggregated information that is provided to sites is based on the the use
   of match keys.  The use of differential privacy ensures that there is some
   protection for the contribution of individual users.  With no limit to the
   time over which queries can be made, the privacy loss experienced by
   participating users is similarly unbounded.  The design only limits the rate
   at which sites gain this information.

Any conclusions about the privacy properties of the API will depend on an
assessment of the adequacy of both of these protections.


## Standard Questions

### What information might this feature expose to Web sites or other parties,
    and for what purposes is that exposure necessary?

The IPA API provides top-level browsing contexts with an encrypted,
secret-shared match key.  Fundamentally, this contains information that can link
activity by the same user across different sites.  The design of the MPC
protocol where that value is used ensures that - provided that the MPC is
executed correctly by 2 of 3 parties - this value is never revealed to anyone.

### Do features in your specification expose the minimum amount of information
    necessary to enable their intended uses?

That's a difficult question to answer simply.  There are a great many trade-offs
to make in this space.

We believe that this particular point in the design space offers a very good
return in terms of utility for advertising use cases.

If the system operates correctly, or if only one helper party is dishonest, no
information is *directly* revealed through the use of the API.  However, there
is a risk of much greater exposure if the system fails.  We consider this to be
an acceptable risk given the safeguards in the design.

In use, the attribution algorithms executed by the MPC system provide aggregated
information.  The results are intended to contain contributions from multiple
users, but sites are able to limit their queries to a single user if they are
willing to exhaust their privacy budget.  This is not rational behaviour on the
part of a site as queries are limited and cost more money than the information
attained is likely worth, but we have to consider that possibility.

To protect individual users, differential privacy is used as that provides us
both a rigorous analytic framework and techniques that can provide strong
protections for the contributions of individual users toward an aggregate.

The differential privacy protections will ultimately depend on finding an
acceptable mechanism.  Differential privacy mechanisms also require choosing
$\epsilon$ and maybe $\delta$ values.  These values determine the amount of
noise that is added and the rate at which sites are able to accumulate
information.  No firm conclusions have been reached on this point, though we
have a tentative design that would allow different user agents to set different
values for these parameters.

Even with differential privacy, sites might gain more information about users
over longer periods.  We believe this to be a tolerable privacy loss as it is
only sites that have long term relationships with users that are able to obtain
additional information in this way.  A strict cap on information release would
render the system completely useless for attribution purposes.  The only
recourse we are aware of is to choose parameters that are more conservative to
reduce the overall rate at which sites can obtain this information.  This needs
to be balanced against the potential adverse effect that added noise has on how
useful the information is for performing attribution.

We are seeking to gather more information before making decisions regarding
differential privacy mechanisms and parameters.

### How do the features in your specification deal with personal information,
    personally-identifiable information (PII), or information derived from them?

The IPA API provides pseudo-identifiers for individuals and makes those
identifiers available for use in an MPC system.  These identifiers are protected
by secret sharing, encryption, and a system of contracts that prevent even the
MPC operators from accessing values.

### How do the features in your specification deal with sensitive information?

See previous answers.

### Do the features in your specification introduce new state for an origin that
    persists across browsing sessions?

Yes.  Though the explainer does not deal with this in great detail, our intent
is to ensure that state clearing events, such as clearing cookies, will result
in the corresponding state being cleared.

Two factors complicate this.  The API provides information that is inherently
cross-site and the epoch design relies on values that are stable for an entire
epoch (a week).  This makes state-clearing events, particularly those that are
narrowly targeted, somewhat challenging to reason about.  We haven't worked
through all of the requirements and constraints in this area, such that we might
infer the correct design.

### Do the features in your specification expose information about the
    underlying platform to origins?

No.  However, if a compatible system is developed in the underlying platform for
the management of match keys, user agent implementations might move to unify the
two sources of match keys.  This would enable attribution that crosses from the
web into applications.  No such mechanism currently exists.

### Does this specification allow an origin to send data to the underlying platform?

No.

### Do features in this specification enable access to device sensors?

No.

### Do features in this specification enable new script execution/loading
    mechanisms?

No.

### Do features in this specification allow an origin to access other devices?

No.

### Do features in this specification allow an origin some measure of control
    over a user agent’s native UI?

No.

### What temporary identifiers do the features in this specification create or
    expose to the web?

The match key itself is not exposed to the web, so this question does not apply.

The ciphertext of the encrypted match key provided to sites is stable over a set
period.  This might be used as an identifier.  However, the lifetime of this
value is bound to the storage lifetime for the site that receives it.  A fresh,
unlinkable encryption is generated if site storage is cleared (and the
underlying value might also need to be randomized too, though this question
still hasn't been completely resolved; see above).

### How does this specification distinguish between behavior in first-party and
    third-party contexts?

Information provided by the API is only provided to the top-level browsing
context (a.k.a., the "first-party context").  Other sites that contribute to the
content of a web page only receive a copy of the value provided to the top-level
site, but only if the top-level site permits it.

### How do the features in this specification work in the context of a browser’s
    Private Browsing or Incognito mode?

This question is not entirely resolved.  User agents that want maximum privacy
protection - which seems likely in this particular case - can randomize the
match key that is provided to sites.  This ensures that attribution is not
possible based on the information that is provided.  This behaviour is
indistinguishable to a site from use of a real match key and so does not offer
sites a reason to discriminate against users.

The same strategy can be employed for users who opt out of use of the API.

### Does this specification have both "Security Considerations" and "Privacy
    Considerations" sections?

It's a primarily functional explainer right now, with a strong emphasis on these
aspects throughout.  We expect that security and privacy will similarly feature
heavily in any final specification also.

PATCG are actively working on a [threat model
document](https://github.com/patcg/docs-and-reports/tree/main/threat-model).
That document will be the basis for further analysis of this proposal (if the
group chooses this specific design to continue with).

### Do features in your specification enable origins to downgrade default
    security protections?

No.

### How does your feature handle non-"fully active" documents?

This question is not applicable to this proposal.

### What should this questionnaire have asked?

Yes, likely many.

Q: If a user opts to disable this feature, is their choice visible to sites?

A: No.  As noted, disabling this feature for any reason is not detectable to a
site.  This prevents sites from discriminating against users who opt out.

Q: If your design includes cryptographic technology, have you provided for ways
to introduce stronger alternatives to crytographic components in the case that
advances in cryptanalytic techniques reveal those components to be weak?

A: No, we haven't currently, but it's a good question.  Our prototype design
does not offer cryptographic agility in any way, but a final design might need
to consider it.

Much of the design provides information theoretic protection for information,
which is inherently not vulnerable to the sort of cryptanalysis that makes it
necessary to replace other primitives.  For these parts, we only need to
consider the size of fields (or rings) we use as that affects the probability of
a successful attack.

Some analysis will be necessary to inform our choices.  Based on that analysis,
we might be able to offer a choice of parameters or decide on a fixed value that
represents an acceptable balance of our security and performance goals.

We do rely on some primitives for which we do need to consider the possibility
of replacement.  Some of these are in TLS, which manages transitions pretty well
already.  We also use HPKE, which offers configurability.  Our prototype uses a
specific PRF design that might need further security analysis.

Q: What recourse does a user have if they make a choice to enable a feature and
they later have second thoughts?

Another excellent question, in a very non-facetious way.  Like with many APIs,
the release of information in IPA is hard to retract.

This is probably a better question when it comes to APIs that grant capabilities
rather than information.

This question does relate in some way to sites being accountable - to users -
for how they use the information and capabilities that they are granted.  In a
way, we might think about this as a question of accountability.

We have thought long and carefully about what sort of accountability might be
built into a system like IPA.  For instance, requiring a public record of
queries made by sites might offer some insight into the sorts of things sites
are requesting.  Given the nature of the API, the opaque nature of the values
that a site might associate with queries, and the often commercially-sensitive
nature of that information, it is not clear that a transparency regime is
compatible with the IPA design.
