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