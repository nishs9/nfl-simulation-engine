Assumptions:
- Away team starts with the ball at their own 25 yard line
- All kickoffs result in touchbacks
- All punts go 40 yards and are assumed to be fair caught
- All PATs are successful, no concept of 2-point conversion for now

Missing Offense Data:
- run and pass rates as separate metrics for each team
- get granular turnover rates
- get sack rate for each team and average yards lost per sack
- get field goal success rate for each team
- get average punt length for each team

Defense Data we need:
- yards per rush and yards per pass allowed for each team defense
- granular turnover rates for each team defense
- get sack rate for each team defense and average yards lost per sack


Sample flow:

1st and 10; Away team ball; 0-0; 15:00 1st; yardline=75
- Use run and pass rates to determine what to run next
- do a weighted average of offense yards per play type and defense yards per play type to determine
  yards gained (60:40 Offense to Defense as a reference)
- Factor in the granular turnover rate (sack/receiving fumbles, ints for pass)(rush fumbles for runs)
- Subtract a standard of 25 seconds per play


if turnover:
- ball is given to opposing team at the initial LOS, 1st and 10

otherwise:
- keep running until TD or 4th down

if 4th down:
- kick field goal when yardline <= 60
    - field goals will have 70% chance of making it for now
- otherwise, punt ball 40 yards and change possession