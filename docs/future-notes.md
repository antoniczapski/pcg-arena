- each level should be validated before uploaded to the database - run Robin agent and check if it is passable
- once the user losses, the Robin agent should continue the game to showcase the rest of the map (transition should be very smooth to be UX friendly
- Calibration battles
- TrueSkill/Bradley–Terry preference model
- Stronger level validation (pipes, solvability)
- Hosted deployment with Postgres/managed storage
- Accounts and anti-abuse at scale)



DB hard reset:
```
# Delete database
docker compose down
Remove-Item db\local\arena.sqlite

# Recreate everything from scratch
docker compose up --build
```

```
cd client-java
./gradlew run --args="--base-url http://34.116.232.204:8080"     
```


# tech debt

+ showcase the whole map
+ login + builder profile
+ fix kill mechanics
- smarter generator selection (multi-arm-bandid style)
- score using keys (basically do everything using keys)
- level validation - check if robin agent (top 3) can pass the level
- ability to give tags
- replay option (if you want to repeate level)
- add AI gameplay finish
- debug mode
- abuse prevention 
    - scoring alignemnt (every 10 battles give one control battle between best and worst)

- excluding repeated level playing
- pcg audio overview for engagement
- community duty - please play 10 battles while submitting new generator
- add statistics for builders (detailed stats on their generators/levels)
- prepare oauth for >100 users (1-2 weeks processing)

Known bugs
- internal error occured while I tried to submit generator with two letter id
- while opening site for the first time it asks to give permission to network devices - starge, it shouldn't be required