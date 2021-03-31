1. Download apps from play store
  - NFC Tools
  - NFC Tasks
2. Buy NFC stickers (NTAG21x)
  - I'm using NTAG215
3. I'm cheap and POST requests are only available in PRO, so I'm going to add a GET API for submitting unary checkins from NFC
  - /nfc-api/?et_id={}
  - upon request to endpoint, get type. assume boolean, submit True. else, submit 1. I guess.
4. Add base URL as user variable
  - {VAR_CHECKINURL} = "http://192.168.1.2:8081/nfc-api/?et_id="
5. Add a variable for each event type (just needs the first few characters). I'm using the prefix VAR_ETXX... as a convention.
6. Now we can create NFC Tasks as {CHECKINURL}{ETXXTEETH} or whatever. Write task to tag, done.

Open question: is there a way to configure a wearable to be my NFC reader instead of my phone? Like a smart watch or bracelet?