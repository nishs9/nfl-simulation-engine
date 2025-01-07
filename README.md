# NFL Simulation Engine
This is a custom simulation engine built to simulate hypothetical NFL games based on up-to-date real-world stats. It is an end-to-end webapp with a frontend
built using React.js with Material UI. For the backend, I built an API with Flask which is connected to a MySQL DB and a set of Python scripts
which contain the logic for the simulation engine itself.

At the moment, everything is hosted locally but I am actively working on deploying this project to the cloud. In addition, my goal is to also set the
project up such that anyone could clone this repository locally and run the app on their machines directly. 

If you would like to learn more about the implementation details of this project [click here](implementation-details.md)

Below is a demo of the app running locally on my personal laptop:

https://github.com/user-attachments/assets/3a15b24a-615d-485f-8c5e-17a39cd80280

## References
The data that the engine relies on comes from a public repo provided by nflverse. I use the player stats and play-by-play data specifically
but the repo has even more detailed data from current and past seasons. All of this data can be accessed and downloaded from [here](https://github.com/nflverse/nflverse-data/releases)

Here is a link to nflverse's main GitHub page as well: https://github.com/nflverse
