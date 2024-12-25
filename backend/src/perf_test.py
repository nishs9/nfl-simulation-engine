from time import time
import GameModels as gm
import game_simulator
import csv

default_perf_test_results_file = "perf_test_results"

def perf_test_model_results(model):
    print(f"\nBeginning results test for {model.get_model_code()}")
    home_team = "BUF"
    away_team = "PHI"

    num_sim_list = [100, 250, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    results = {
        100: None,
        250: None,
        500: None,
        750: None,
        1000: None,
        2000: None,
        3000: None,
        4000: None,
        5000: None
    }
    for num_sim in num_sim_list:
        result_dict = game_simulator.run_multiple_simulations_multi_threaded(home_team, away_team, num_sim, model)
        results[num_sim] = result_dict["average_score_diff"]

    with open(f"results_perf_test.csv", "a", newline='') as csvfile:
        fieldnames = ['model_code', 'iterations', 'average_score_diff']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data
        for num_sim in results.keys():
            writer.writerow({'model_code': model.get_model_code(), 'iterations': num_sim, 'average_score_diff': results[num_sim]})

def perf_test_model_execution_time(model, use_multi_threading=True, file_name=default_perf_test_results_file):
    print(f"\nBeginning runtime perf test for {model.get_model_code()}")
    home_team = "BUF"
    away_team = "PHI"

    num_sim_list = [100, 500, 1000, 2500, 5000, 7500, 10000]
    results = {
        100: None,
        500: None,
        1000: None,
        2500: None,
        5000: None,
        7500: None,
        10000: None
    }
    for num_sim in num_sim_list:
        curr_run_start = time()
        if use_multi_threading:
            game_simulator.run_multiple_simulations_multi_threaded(home_team, away_team, num_sim, model)
        else:
            game_simulator.run_multiple_simulations_with_statistics(home_team, away_team, num_sim, model)
        curr_run_end = time()
        curr_run_time = curr_run_end - curr_run_start
        results[num_sim] = curr_run_time

    with open(f"{file_name}.csv", "a", newline='') as csvfile:
        fieldnames = ['model_code', 'iterations', 'execution_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data
        for num_sim in results.keys():
            writer.writerow({'model_code': model.get_model_code(), 'iterations': num_sim, 'execution_time': results[num_sim]})



if __name__ == "__main__":
    # single_threaded_perf_result_file = "single_threaded_perf_test_results"
    # perf_test_model(gm.PrototypeGameModel(), use_multi_threading=False, file_name=single_threaded_perf_result_file)
    # perf_test_model(gm.GameModel_V1(), use_multi_threading=False, file_name=single_threaded_perf_result_file)
    # perf_test_model(gm.GameModel_V1a(), use_multi_threading=False, file_name=single_threaded_perf_result_file)
    # perf_test_model(gm.GameModel_V1b(), use_multi_threading=False, file_name=single_threaded_perf_result_file)

    # multi_threaded_perf_result_file = "multi_threaded_perf_test_results"
    # perf_test_model_execution_time(gm.PrototypeGameModel(), use_multi_threading=True, file_name=multi_threaded_perf_result_file)
    # perf_test_model_execution_time(gm.GameModel_V1(), use_multi_threading=True, file_name=multi_threaded_perf_result_file)
    # perf_test_model_execution_time(gm.GameModel_V1a(), use_multi_threading=True, file_name=multi_threaded_perf_result_file)
    # perf_test_model_execution_time(gm.GameModel_V1b(), use_multi_threading=True, file_name=multi_threaded_perf_result_file)

    # perf_test_model_results(gm.PrototypeGameModel())
     #perf_test_model_results(gm.GameModel_V1())
     #perf_test_model_results(gm.GameModel_V1a())
     perf_test_model_results(gm.GameModel_V1b())