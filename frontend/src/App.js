import React, { useState } from 'react';
import axios from 'axios';
import { Typography, Box } from '@mui/material';
import TeamSelector from './components/TeamSelector';
import SimulationTable from './components/SimulationTable';

const App = () => {
  const [simulationData, setSimulationData] = useState([]);
  const [resultString, setResultString] = useState(''); 
  const teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"];

  const handleSimulate = async (homeTeam, awayTeam, numSimulations) => {
    try {
      const response = await axios.post('http://localhost:5000/run-simulation', {
        home_team: homeTeam,
        away_team: awayTeam,
        num_simulations: numSimulations,
      });

      const { result_string, total_sim_stats } = response.data;
      setResultString(result_string);
      setSimulationData(total_sim_stats);
    } catch (error) {
      console.error("Error running simulation: ", error);
      setResultString('Error running simulation: ' + error.message);
      setSimulationData([]);
    }
  };

  return (
    <Box padding={3}>
      <TeamSelector teams={teams} onSimulate={handleSimulate} />
      {resultString && (
        <Typography variant="h5" style={{ marginBottom: 20 }}>
          {resultString}
        </Typography>
      )}
      <SimulationTable data={simulationData} />
    </Box>
  )
}

export default App;