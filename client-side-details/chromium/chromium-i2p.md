# Subject of email
[Intent to Prototype] Interoperable Private Attribution sent to blink-dev@chromium.com

# Contact emails
richaj@meta.com (Richa Jain, Meta)
btsavage@meta.com (Ben Savage, Meta)

# Explainer
https://github.com/patcg-individual-drafts/ipa/blob/main/IPA-End-to-End.md

# Specification
Under development at https://github.com/patcg-individual-drafts/ipa

# Design Doc One-Pager
https://docs.google.com/document/d/1LBv-Sg84jyq3Em474kgEbOaJ1GY6XsQKj6TlAlnIkyw

# Summary
Interoperable Private Attribution (IPA) is an API for privacy-preserving advertising attribution. Attribution means counting the number of "conversions", for example purchases, that follow an ad interaction, for example viewing an ad. IPA preserves privacy by using cryptography and a network of helper parties who are trusted not to collude or be collectively coerced. See https://github.com/patcg-individual-drafts/ipa

# Blink component
Blink > Attribution

# Motivation
Advertising provides critical support for the web. Interoperable Private Attribution (IPA) enables advertisers to measure how their advertising campaigns are performing without relying on signals which identify specific individuals. In IPA, the user agent protects user identity using cryptography which is split across a network of helper parties. The helper parties are trusted not to collude or be collectively coerced. See also 
https://blog.mozilla.org/en/mozilla/privacy-preserving-attribution-for-advertising/

One of the things we hope to learn by prototyping and conducting experiments, is how much the advertising industry is able to work with noisy data. Most ad reporting systems today do not add random noise to ensure a differential privacy guarantee, or limit the number of breakdowns according to a “privacy budget”. This will likely be a difficult transition. We hope to collect feedback to help us iterate on the techniques for adding random noise, to try to find an optimal balance of privacy and utility.

# Initial public proposal
https://docs.google.com/document/d/1KpdSKD8-Rn0bWPTu4UtK54ks0yv2j22pA5SrAD9av4s/edit

# TAG review
Pending. Issue can be found [here](https://github.com/w3ctag/design-reviews/issues/823)

## TAG review status
Pending

# Risks
In the IPA proposal, a user-agent stores a user identifier (the “match key”) and processes it in response to API calls from any secure origin, including cross-site origins. Match keys do not follow the modern patterns of site isolation in web browsers, because while write permissions are partitioned by site, the ability to access an encrypted secret-sharing of the match key is available to all secure origins. We believe that the restrictions on the use of match keys are sufficient because the value returned by the API is a per-origin encryption of shares of the match key.  It would take at least two trusted helper parties (see the “[Threat Model](https://github.com/patcg/docs-and-reports/tree/main/threat-model)” document the PAT-CG has put together for details) to decrypt the shares and then collude with one another to recover the underlying identifier.

In our initial prototyping, we intend to make this feature off by default. Developers can turn it on manually for testing.


# Interoperability and Compatibility
IPA has two fundamental operations: setMatchKey, which sets a user identifier, and getEncryptedMatchKey, which retrieves an encrypted match key. To preserve user privacy, the side effects of setting a match key are unobservable to sites except in aggregate. This means the API could be effectively disabled, even on a per-person basis, by making setMatchKey a no-op. In addition, getEncryptedMatchKey uses a lazily resolved Promise so the API could be disabled, or return random data, with no compatibility impact for sites.

Gecko: Pending. Issue can be found [here](https://github.com/mozilla/standards-positions/issues/753)

WebKit: Pending. Issue can be found [here](https://github.com/WebKit/standards-positions/issues/142)

Web developers: IPA has been covered by several blog posts and websites e.g. [here](https://www.adweek.com/programmatic/ipa-the-meta-and-mozilla-attribution-framework-gains-traction-at-the-w3c-conference/) and [here](https://stratechery.com/2022/an-interview-with-eric-seufert-about-the-post-att-landscape/). An anonymous survey of participants in the “Private Advertising Technology Community Group” ([link](https://docs.google.com/document/d/1bydwuN0_K2anOZV41xNJn1Kt0vt9WPOkf56ESnmQ5_A/edit?usp=sharing)) shows strong preference for the architectural decisions and capabilities of IPA. Let us know if we need to provide more signals to showcase the support.

# WebView application risks
There may be changes to WebView behavior. We are still discussing the issue [here](https://github.com/patcg-individual-drafts/ipa/pull/41).

# Debuggability
We plan to extend DevTools’ storage model to indicate whether an identity provider has a match key set and let developers clear a match key without clearing all site data; to inspect helper networks, their keys, and the epoch clock. These are useful when developing and debugging IPA.

# Is this feature fully tested by [web-platform-tests](https://chromium.googlesource.com/chromium/src/+/main/docs/testing/web_platform_tests.md)?
No, but we plan to submit tests to WPT. We might need to extend WPT browser hooks to interact with IPA storage.

# Flag name
Blink feature, interoperable-private-attribution.

# Requires code in //chrome?
True

# Tracking bug
https://bugs.chromium.org/p/chromium/issues/detail?id=1404067

# Estimated milestones
No milestones specified

# Link to entry on the Chrome Platform Status
This intent message was generated by [Chrome Platform Status](https://chromestatus.com/feature/4855434349903872).
