# The Igloo

Keeps track of rackets and members usage.

## API

The API usage is as follows.

```css
GET /api/test 			| Test your header
GET /api/members 		| Returns stored data in DB
PUT /api/members 		| Updates existing partial entries
POST /api/members/reset         | Takes no data, resets all month to 0
POST /api/members/clean         | Takes no data, removes members no longer in faction
GET /api/rackets 		| Returns stored data in DB
PUT /api/rackets 		| Updates exisiting partial entries
GET /api/warbase		| Returns stored data in DB
PUT /api/warbase		| Updates existings partial entries | mostly used for the 'update' button.
```

Header must include "X-Api-Key"

GET's return valid json.

PUT request must be valid json.

python example; header = {'X-Api-Key': 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}  

sudo systemctl restart igloo

## Structure for members can be found below.

the data can be gathered from; 

`https://api.torn.com/user/{tornid}?selections=profile,personalstats&key={tornkey}`

This can be a single or multiple users.

```python
{
  "502": {
    "rank": "Legendary Booster",
    "level": 96,
    "gender": "Male",
    "property": "Private Island",
    "signup": "2004-11-19 18:11:35",
    "awards": 326,
    "friends": 25,
    "enemies": 21,
    "forum_posts": 39,
    "karma": 0,
    "age": 5423,
    "role": "Civilian",
    "donator": 1,
    "player_id": 502,
    "name": "Mech",
    "property_id": 2333382,
    "life": {
      "current": 7050,
      "maximum": 7050,
      "increment": 423,
      "interval": 300,
      "ticktime": 281,
      "fulltime": 0
    },
    "status": [
      "Okay",
      ""
    ],
    "job": {
      "position": "Employee",
      "company_id": 78694,
      "company_name": "Delivery Cum Quickly"
    },
    "faction": {
      "position": "Member",
      "faction_id": 14821,
      "days_in_faction": 546,
      "faction_name": "The Igloo"
    },
    "married": {
      "spouse_id": 0,
      "spouse_name": "None",
      "duration": 0
    },
    "basicicons": {
      "icon6": "Male",
      "icon3": "Donator",
      "icon27": "Company - Employee of Delivery Cum Quickly (Logistics Management)",
      "icon9": "Faction - Member of The Igloo"
    },
    "states": {
      "hospital_timestamp": 0,
      "jail_timestamp": 0
    },
    "last_action": {
      "timestamp": 1569495576,
      "relative": "1 hour ago"
    },
    "personalstats": {
      "useractivity": 4807869,
      "itemsbought": 37,
      "pointsbought": 11687,
      "itemsboughtabroad": 4480,
      "weaponsbought": 17,
      "trades": 90,
      "itemssent": 192,
      "auctionswon": 26,
      "auctionsells": 7,
      "pointssold": 3650,
      "attackswon": 6503,
      "attackslost": 364,
      "attacksdraw": 21,
      "bestkillstreak": 400,
      "moneymugged": 142636221,
      "attacksstealthed": 4962,
      "attackhits": 17813,
      "attackmisses": 8135,
      "attackdamage": 15390672,
      "attackcriticalhits": 3358,
      "respectforfaction": 15068,
      "onehitkills": 3973,
      "defendswon": 206,
      "defendslost": 1022,
      "defendsstalemated": 4,
      "bestdamage": 8425,
      "roundsfired": 24263,
      "yourunaway": 8,
      "theyrunaway": 3,
      "highestbeaten": 100,
      "peoplebusted": 105,
      "failedbusts": 21,
      "peoplebought": 56,
      "peopleboughtspent": 45255525,
      "virusescoded": 39,
      "cityfinds": 733,
      "traveltimes": 370,
      "bountiesplaced": 42,
      "bountiesreceived": 17,
      "bountiescollected": 696,
      "totalbountyreward": 349881010,
      "revives": 24,
      "revivesreceived": 34,
      "medicalitemsused": 5444,
      "statenhancersused": 42,
      "trainsreceived": 707,
      "totalbountyspent": 17272904,
      "drugsused": 477,
      "overdosed": 13,
      "meritsbought": 47,
      "logins": 29861,
      "personalsplaced": 0,
      "classifiedadsplaced": 33,
      "mailssent": 4162,
      "friendmailssent": 1030,
      "factionmailssent": 1952,
      "companymailssent": 110,
      "spousemailssent": 627,
      "largestmug": 9881586,
      "xantaken": 331,
      "victaken": 145,
      "chahits": 1,
      "heahits": 195,
      "grehits": 27,
      "machits": 13,
      "pishits": 41,
      "rifhits": 12,
      "shohits": 39,
      "smghits": 7,
      "piehits": 2,
      "slahits": 6169,
      "argtravel": 5,
      "mextravel": 14,
      "dubtravel": 16,
      "hawtravel": 17,
      "japtravel": 13,
      "lontravel": 11,
      "soutravel": 51,
      "switravel": 156,
      "chitravel": 35,
      "cantravel": 9,
      "dumpfinds": 85,
      "dumpsearches": 89,
      "itemsdumped": 12,
      "daysbeendonator": 2866,
      "caytravel": 42,
      "jailed": 414,
      "hospital": 1685,
      "bazaarcustomers": 218,
      "bazaarsales": 22733,
      "bazaarprofit": 990082560,
      "networth": 24293541100,
      "missioncreditsearned": 25690,
      "contractscompleted": 691,
      "dukecontractscompleted": 691,
      "axehits": 40,
      "missionscompleted": 1,
      "attacksassisted": 29,
      "bloodwithdrawn": 2,
      "consumablesused": 30,
      "candyused": 19,
      "energydrinkused": 11,
      "organisedcrimes": 105,
      "stockpayouts": 409,
      "booksread": 18,
      "traveltime": 2645580,
      "boostersused": 405,
      "territorytime": 397908,
      "rehabs": 14,
      "rehabcost": 3250000,
      "nerverefills": 1,
      "awards": 326,
      "refills": 173
    }
  }
example: https://haste.discordbots.mundane.nz/okuzugirec.json
```

## Structure for members can be found below.
Coming soon; structure for this is a bit different.

## TO DO
Less API calls on Rackets - no need to call each faction for name if owner hasn't changed.

Add full debugging/logging

Setup 'Settings' page (api key generation, users etc)

Automate discord Oauth
