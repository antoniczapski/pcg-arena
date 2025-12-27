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

- score using keys (basically do everything using keys)
- fix kill mechanics
- level validation - check if robin agent (top 3) can pass the level
- smarter generator selection (multi-arm-bandid style)
- ability to give tags
- showcase the whole map
- add AI gameplay finish
- login + builder profile
- debug mode
- abuse prevention 
    - scoring alignemnt (every 10 battles give one control battle between best and worst)

- excluding repeated level playing
- pcg audio overview for engagement
- community duty - please play 10 battles while submitting new generator
- add statistics for builders (detailed stats on their generators/levels)