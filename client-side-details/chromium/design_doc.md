# Chromium Design Doc

**Authors: richaj@meta.com (Richa Jain), btsavage@meta.com (Ben Savage)**

## Summary
Interoperable Private Attribution (IPA) enables privacy-preserving ads measurement or conversion attribution. At a high level, the user agent stores a single, randomly initialized user identifier, but preserves privacy by never disclosing it to any party. Instead, the user-agent randomly secret-shares this identifier, and then encrypts the shares towards three “helper servers” that the user agent vendor only needs to trust to not collude. Helper nodes will receive large batches of these encrypted secret shares, collected across multiple websites. After decrypting their shares, the helper nodes will run a secure multiparty computation to calculate aggregate attribution data. The helpers will ensure this data is differentially private before releasing it. They’ll do so by capping individual user contributions, and by adding random noise. This ensures that these noisy aggregates cannot be used to track individuals across websites.

### Platforms
This is a portable Web platform feature. It will be implemented on all platforms which use Blink. The feature could be present but is currently effectively inert in UAs like the Android WebView due to privacy challenges.

### Team
The IPA team at Meta is developing this feature, in collaboration with our esteemed colleagues in the W3C’s “Private Advertising Technology Community Group”. 

Contact richaj@meta.com (Richa Jain) and btsavage@meta.com (Ben Savage).

### Bug
Chromium Bug [1404067](https://bugs.chromium.org/p/chromium/issues/detail?id=1404067).

### Code affected
- third_party/blink: Add a module to introduce the IPA API to pages on secure origins. WPT test hooks for helper network policy, etc.
- content/browser: Add a Mojo service to implement the `getEncryptedMatchKey` API
- components/interoperable_private_attribution: A cache storage, namely match_keys_cache containing shares of matchkeys, per domain etc. This will also implement a persistent chrome storage to save a 64 bit number. Also, add a service for implementing generate_encrypted_shares and encrypt_matchkey modules etc.
- settings: user settings page to control state of IPA
- Devtools: Add tools for debugging IPA state.

We are proposing two APIs `getEncryptedMatchKey` and `getHelperNetworks`. 

## getEncryptedMatchKey API
This API allows retrieval of an encryption of secret-shares of the matchkey that was previously set. If not found, this API also generates a random value for the matchkey, and stores it.

### Interface
```
dictionary PrivateAttributionHelperShare {
  // This is the identifier for the HPKE key that was used to encrypt. Since the
  // helper party may have multiple keys, this indicates which one to apply.
  octet keyId;

  // Encrypted share along with the associated data including epoch, caller
  // site, report collector and event type.
  ArrayBuffer encryptedShare;
};

dictionary PrivateAttributionEncryptedMatchKey {
  // Map from helper's origin to the encrypted bits they get and additional info
  // used to generate those bits.
  record<DOMString, PrivateAttributionHelperShare> shares;
};

dictionary PrivateAttributionOptions {
  PrivateAttributionEvent eventType;

  // Identifier to indicate which helper party network does report collector
  // want to encrypt towards.
  unsigned long helperNetworkId;

  // TODO(richaj) add more parameters, such as binding to a report collector for
  // partial budget allocation. See:
  // https://github.com/patcg/docs-and-reports/tree/main/threat-model#33-privacy-parameters
};

enum PrivateAttributionEvent {
  "source",
  "trigger",
};
  
// Retrieve an encryption of a secret-sharing of the match key that was
// previously set. This encryption will be specific to the registrable domain
// of the top-level schemeful site at the time when this function is invoked.
Promise<PrivateAttributionEncryptedMatchKey> `getEncryptedMatchKey`(

  // Origin of report collector who is collecting the events
  DOMString reportCollector,

  // Additional information to get appropriate encrypted match keys
  PrivateAttributionOptions options
);
```

### Who sets the matchkey?

In our initial IPA proposal, we proposed that any website could act as a matchkey provider, and could set a value for a matchkey. However, we recently found an [attack](https://github.com/patcg-individual-drafts/ipa/issues/57) which could be waged by a malicious matchkey provider. Until we are able to find a good mitigation to this attack, we propose prototyping a simpler system; Just having a per-profile ([as compared to per-browser](https://github.com/patcg-individual-drafts/ipa/issues/68)), randomly generated matchkey.

#### *Rejected Alternative Options*

**Cross-device same-profile match key**

We had also considered using browser-login to sync this randomly generated matchkey across multiple browsers signed-in to the same account (e.g. Chrome sync). Unfortunately, we realized that such an approach would NOT be extensible to App-to-web attribution.

App-to-web attribution is a very important advertising use–case that many publishers require support for. One path to support this use-case could be to store the per-device randomly generated matchkey at the mobile operating system level, and have browser apps just federate the call to `getEncryptedMatchKey`() to the OS. If mobile apps could access this same OS-provided API, to receive encrypted secret-sharings of the same value, that would support App-to-web and Web-to-app attribution.

This approach might not make sense for Desktop based browsers, and at any rate, such an API is not currently available in mobile operating systems. So for this initial prototyping stage, we propose each browser application generate and store a random matchkey per user profile. 


**Same-device cross-profile match key**

We had also considered sharing the same match key across all user profiles on the same device. You can read more about the discussion in [this](https://github.com/patcg-individual-drafts/ipa/issues/68) issue.

This might have been beneficial in terms of attribution. For example, it might provide better coverage if ads shown on one profile could receive attribution for conversion events generated in another. However, from a privacy perspective it might be strange to share attribution state across [multiple profiles](https://www.chromium.org/user-experience/multi-profiles/). 

Due to this, we propose having a different underlying match key per each user profile even on the same device.

### Implementation Design

#### Renderer

This is the entry point for the API. This component is responsible for accepting the parameters, calling browser functions and returning the results back to the api caller. 
Since the raw matchkey is a sensitive piece of information, the renderer never has any access to it.

#### Browser

This is where the actual functionality is implemented. 

##### Services needed

###### Match keys Cache Storage

Input: Caller site

Output: 3 shares if found

This is a persistent cache which would store (for each site which invoked the `getEncryptedMatchKey` API) 3 secret shares of the matchkey per domain. 

This cache is necessary to support query sharding (necessary for large websites that want to run queries with billions, or even hundreds of billions of reports. See issue filed by the Google Ads team [link](https://github.com/patcg/private-measurement/issues/21)). We have proposed a design for sharding, but to ensure that the number of reports sent to each shard does not leak sensitive information, the shard-sizes need to be made differentially private. To achieve this, we need a sensitivity bound on the number of reports in a query which come from an individual person. 

To read more about the proposed approach to query sharding, see this issue: [link](https://github.com/patcg-individual-drafts/ipa/issues/35).

By utilizing the same exact secret shares across all the records from a given person, from a given site, we can have the helper nodes enforce a sensitivity bound.

*Rejected Alternative Options* 

We considered caching encryptions of matchkeys for the given epoch and returning the same ciphertext for a given combination of user, epoch, caller site and report collector. However, this can lead to potential leakage. As an example, let's say the source site just caches encryptions of matchkeys per domain and sends them to the trigger site, the trigger site will get to learn the distribution of the same users in the other sites data. Please note, this isn't cross site leakage but this could be business sensitive information which is better hidden.
To prevent this leakage, it is better to just cache the shares per domain and create fresh encryptions each time a call is made to the `getEncryptedMatchKey` API.


##### APIs

###### getHelperNetworks

This API has been detailed in a separate section.

##### Modules

###### preprocessing

Input: report collector, event type, preferred helper party network

Output: caller_site to find the encrypted shares for this user

The browser first does some preprocessing needed to fetch appropriate matchkey shares for the current user.

The preprocessing module would execute the following steps:
- Check if this API should be allowed to be accessed in the current setting. This API will not be available for any Android webviews. Here is some discussion about the challenges with webviews: [link](https://github.com/patcg-individual-drafts/ipa/pull/41). It will also be governed by the Permissions Policy. Specifically, this API won’t be available for iframes. We will return an error code in case the API is still somehow called under these conditions.
- Check if the helper party network is on the list of approved helper party networks, the same list which is obtained when calling `getHelperNetworks`
- Calculates current site

###### generate_shares

Input: caller_site

Output: 3 secret shares or, encrypted shares (3 AEAD encrypted blobs)

This is an implementation for getting matchkey shares based on OS support and API disabled status. In the future, we envision an OS-level implementation which would return encrypted shares which could be used for the purpose of IPA. 


- **API disabled**

  The API is automatically disabled in private browsing mode. Also, users can manually disable the API through the settings menu.
  In this scenario, 
  - Random number is used in place of the actual match key. 
  - 3 random secret-shares of matchkey are generated such that
    matchkey = match_key1 XOR match_key2 XOR match_key3
  - The encrypt_matchkey module would be invoked to secret-shares and encrypt this random number before returning it.
- **OS support for `getEncryptedMatchKey`**

  This is out of scope for this initial prototype, but included in this design doc to facilitate discussion. 
  
  In the future, if mobile operating systems were to add support for IPA-style measurement of advertising in mobile apps, we can envision an OS-level `getEncryptedMatchKey` API callable by apps. We can imagine browser-apps on mobile operating systems simply delegating calls to `getEncryptedMatchKey` to this OS-level API. This would make it possible for ads shown in mobile apps to receive attribution for conversions that occur on mobile websites, and vice-versa. 

  These are important advertising use-cases that we would like to find a way to support. In such a scenario, the browser could simply return the value it receives from the OS to the renderer, perhaps also caching it (unless the OS were to also handle caching of ciphertexts).

- **All other OS**

	In this scenario,
  - The browser would lookup for a matchkey on the chrome storage on-device. If not found, it would simply generate a random number to serve as the matchkey, save it in persistent storage on the local device. 
  - 3 secret-shares of matchkey will be generated such that
    matchkey = match_key1 XOR match_key2 XOR match_key3
  - The encrypt_matchkey module would be invoked to secret-shares and encrypt this random number before returning it.

##### encrypt_matchkey

Inputs: 3 secret shares (64 bit numbers), report collector, caller site, epoch, event type, helper party network

Outputs: Encrypted shares (3 AEAD encrypted blobs)

This function takes the unencrypted matchkey secret shares as an argument and returns back encrypted shares, which are bound to authenticated associated data.

Here are the steps it takes.

- Assembles associated data i.e. report collector, event_type, caller_site and epoch
- Calls `getHelperNetworks` API to get the public keys of the helper parties
  - Encrypt each pair of two shares using the public key of one of the helper parties (bound to authenticated associated data). To be clear: 
    - Helper one would receive an encryption of shares 1 and 2
    - Helper two would receive an encryption of shares 2 and 3
    - Helper three would receive an encryption of shares 3 and 1

### Summary of overall implementation flow

Now that we have detailed all different components needed for the API to work, here is the overall flow

- The browser does preprocessing to validate input and calculate appropriate inputs for the next phase.
- The caller_site is then used to perform a lookup in the matchkeys_cache. If found, the 3 secret shares are used to invoke encrypt_matchkey
- If no shares are found in the cache for this site, generate_shares is called which either returns raw secret shares or (longer term) encrypted shares; based on the user settings and request type.
- If raw shares are returned, they are cached in matchkeys_cache
- If the generate_shares function returns raw shares, encrypt_matchkey function is called to encrypt the secret shares of the matchkey.
- Browser returns the encrypted shares back to the renderer.


## getHelperNetworks API

We are still fleshing out the details of this API, and would love to get some feedback about how to implement this effectively in Chromium.

### Interface
```
dictionary PrivateAttributionHelperInfo {
  DOMString origin;

  // Public key of the helper
  DOMString publicKey;
};

[Serializable]
dictionary PrivateAttributionNetwork {
  unsigned long id;
  sequence<PrivateAttributionHelperInfo> helpers;
};

// Get the set of helper networks that the browser is willing to encrypt matchkeys
// towards along with their public keys.
Promise<sequence<PrivateAttributionNetwork>> `getHelperNetworks`();
```

This would return the set of helpers that the browser is willing to encrypt matchkeys towards along with their public key specifications for the current epoch. 

**Browser Approved Helper Parties**

In the IPA design, we expect the browser vendors to trust only a set of helper parties to run multi-party computation for their users. 

**Fetching Public Keys**

This API will also return public keys which are associated with the approved list of helper parties. These public keys will be used to encrypt the secret shares of the match key.

A key aspect of the design is that the UA checks on a regular cadence to see if anything has changed. Consistent public keys need to be maintained so that multiple people get the same answer. 

Practically we expect the set of helper networks to be relatively small. And, key rotation to be slow (months, not hours) with helper parties having to give plenty of notice for a planned key rollover. Due to this, we are considering separately delivering the set of "trusted" helper party networks and the set of keys for the helpers in those networks to Chromium. 

Chromium would then use [Component Updater](https://chromium.googlesource.com/chromium/src/+/lkgr/components/component_updater/README.md) to deliver trusted helper party network origins and public keys in one system to the user agents. We would rely on [TLS](https://chromium.googlesource.com/website.git/+/40cfbbdee67c7010ae103011fe5797858e692a79/site/Home/chromium-security/education/tls/index.md#Certificates) in the browser to provide correctness and consistency.

## Rollout plan

Waterfall (flag gated for now)

## Core principle considerations

### Speed
The generation, storage and fetches of matchkeys should be cheap. Let’s take a look at each module
- Preprocessing: This executes a finite set of steps which are also trivial hence should not be a concern
- Matchkey Cache lookup: For storing the matchkey shares, we will use a persistent cache. For each caller_site, we would be storing 24 bytes of data (3 64 bit numbers representing three secret shares of the match key) per site. Since this data is much smaller than cookie stores and even that is known to be performant, we expect the cache to be very efficient. Matchkey cache hit or miss should be trivial
- Matchkey shares generation: In case of cache miss, matchkey shares will need to be generated. The steps involved differ based on user settings. 
  - Disabled API: Generating random matchkey should be trivial and no concern
  - Federate to OS: We are expecting this to be an async and lightweight implementation provided by OS itself. 
  - Others: The API would hit local on-device storage to search for an already set matchkey. If not found, a 64 bit unique identifier will be set on chrome storage, persistently. We expect this number to be either generated randomly or using a subroutine which should be trivial. 
- Encrypting raw matchkeys: This executes a finite set of steps which are also trivial hence should not be a concern. This module has a dependency on `getHelperNetworks` API which in turn depends on reading a pre-loaded configuration hence should be trivial as well.

### Simplicity
We are just introducing two APIs by this change i.e. `getEncryptedMatchKey` and `getHelperNetworks`. For this initial prototype, there is no UI change planned. In future updates we can imagine a user settings page which gives people the ability to disable the API, and perhaps cool transparency features, such as showing which websites requested encrypted matchkeys, and how many times. 
These APIs will be invoked by advertisers or publishers to generate reports used to measure the outcome of running advertisements. Most of the information about advertising measurement is provided by publishers and advertisers out of band. It is only the encrypted matchkey which needs to be provided by the browser. 

### Security
We expect the renderer process can be compromised. Hence, the design hides sensitive information (i.e. raw matchkeys) from the renderer. The processing on matchkeys is done in the browser which is an isolated environment.
The API does not involve any parsing of untrustworthy input (other than the report collector - an origin).
The APIs are asynchronous which would enable us to mitigate timing attacks
While we cannot think of any potential attacks at this point, once the implementation is complete, we plan to benchmark the implementation to check if there can be any attack.

### Privacy considerations
In the IPA proposal, a user-agent stores a user identifier (the “match key”) and processes it in response to API calls from any secure origin. The ability to access an encrypted secret-sharing of the match key is available to all secure origins. We believe that the restrictions on the use of match keys are sufficient because
The caller sites can never read raw match key
The value returned by the API is a per-origin encryption of shares of the match key per user profile
It would take at least two trusted helper parties (see the “Threat Model” document the PAT-CG has put together for details) to decrypt the shares and then collude with one another to recover the underlying identifier. 
After computing the aggregated attribution data, the helpers ensure that it is differentially private before releasing. They’ll do so by capping individual user contributions, and by adding random noise. This ensures that these noisy aggregates cannot be used to track individuals across websites.

#### Resetting and clearing match key
In future updates, user settings page will be provided which gives people the ability to 
Disable the API as mentioned above.
Reset their match keys
The cached match key shares will also be deleted when users delete site data for the associated top level site.

Overall, the Chromium API does not introduce any new threats. You can also refer to this Security and Privacy Questionnaire for more details on other considerations.

### Testing plan

Each component will ship with unit tests in-tree. IPA will be tested end-to-end via Web Platform Tests, including setting, retrieving and verifying data to ensure expected results. 

Some of the extensions we will implement to support testing are to programmatically set the device match key, implement a sandbox helper network and constructs for debuggability (e.g.  serializable PrivateAttributionNetwork could return helper public keys for debugging purposes, etc).

