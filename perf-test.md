# NFL Simulation Engine Runtime Performance Results

Baseline matchup used for each test: BUF v PHI (home - away)

Below are results from some performance testing I did with the simulation engine. For each of the model types, I ran them at various numbers of iterations with the single and multi-threaded runners. You can see the execution times (in seconds)
in the table below. I also have a graph to visually show the performance of the engine scales.

#### Single-Threaded Runs
--- 

| **Model** | **100** | **500** | **1000** | 2500   | 5000   | 7500   | 10k    |
| --------- | ------- | ------- | -------- | ------ | ------ | ------ | ------ |
| *Proto*   | 0.91    | 4.33    | 8.75     | 22.19  | 45.68  | 69.58  | 94.28  |
| *V1*      | 8.29    | 41.19   | 83.98    | 198.85 | 394.3  | 585.82 | 804.48 |
| *V1a*     | 8.29    | 42.26   | 77.88    | 198.19 | 431.45 | 612.22 | 851.60 |
| *V1b*     | 6.95    | 34.31   | 69.12    | 189.90 | 352.15 | 546.74 | 719.37 |

#### Multi-Threaded Runs (10 threads)
---

| **Model** | **100** | **500** | **1000** | 2500  | 5000   | 7500   | 10k    |
| --------- | ------- | ------- | -------- | ----- | ------ | ------ | ------ |
| *Proto*   | 1.89    | 3.08    | 4.40     | 19.49 | 18.74  | 38.86  | 32.41  |
| *V1*      | 4.67    | 11.16   | 23.13    | 62.26 | 133.16 | 154.31 | 242.64 |
| *V1a*     | 4.65    | 13.42   | 25.96    | 52.76 | 106.55 | 210.49 | 270.38 |
| *V1b*     | 4.31    | 10.77   | 18.22    | 45.38 | 117.77 | 195.27 | 217.42 |

![Screenshot 2024-12-25 121351|500](https://github.com/user-attachments/assets/c0c3aeae-4747-4a03-9fba-b52c8678eabf)
