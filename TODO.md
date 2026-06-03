# EXAMPLES

- [ ] EXAMPLE
- [x] EXAMPLE Done
- [ ] EXAMPLE doing it | name

# Frontend

- [ ] Frontend
  - [ ] One click panic
    - [ ] Make it work
    - [ ] Make it look good
    - [ ] Send REST GET requist to https://gss-panic-api.pixieoflife.co.za/get-loc or any other way to get lat and lan
    - [ ] Send REST POST requist to https://gss-panic-api.pixieoflife.co.za/one-click-panic
    - [ ] Data to send as json , latitude , latitude, user - will add example of it to /examples
    - [ ] make ui for (popups / confirmation help is on the way)
      - [ ] SMS await for webhook status 2xx with message = "success"
      - [ ] Email await for webhook status 2xx with message = "success"
            
  - [ ] Emergancy contact page
    - [ ] Add ui to add view all contacts
      - [ ] send to https://gss-panic-api.pixieoflife.co.za/ec/<uuid>/all
    - [ ] Add ui to add new contacts
      - [ ] send to https://gss-panic-api.pixieoflife.co.za/ec/<uuid>/new POST
    - [ ] Add ui to update contacts
      - [ ] send to https://gss-panic-api.pixieoflife.co.za/ec/<uuid>/<contactid> PUT
    - [ ] Add ui to delete contacts
      - [ ] send to https://gss-panic-api.pixieoflife.co.za/ec/<uuid>/<contactid> DEL
            
  - [ ] Alert History page
    - [ ] Show all alerts
      - [ ]  send to https://gss-panic-api.pixieoflife.co.za/ec/<uuid>/alert/all GET
            
  - [ ] Admin live alert dashboard
    - [ ] Show all alerts
    - [ ] Add fiters by user
    - [ ] Add filers by area
    - [ ] UI to pull atention if new one comes in
  
  - [ ] Mobile-first responsive design (DO THIS LAST OTHERWISE YOU WILL SUFFER)

# Backend

- [ ] Backend
  - [ ] SMS Service
    - [ ] Create api
      - [ ] /usercontatacts PUT GET POST
      - [ ] /sendsos
      - [ ] send to frontend confrimation
  - [ ] Email Service
    - [ ] Create api
      - [ ] /useremails PUT GET POST
      - [ ] /sendsos
      - [ ] /sendloc PUT GET POST
      - [ ] send to frontend confrimation
  - [ ] Alert Service
    - [ ] Create api
      - [ ] /alert POST GET
      - [ ] /alert/all GET
      - [ ] send to frontend
    - [ ] Webhook
      - [ ] live update  
