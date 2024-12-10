import './App.css';
import React, { useState } from 'react';
import axios from 'axios';
import { AppBar, Toolbar, Typography, LinearProgress, Box } from '@mui/material';
import TeamSelector from './components/TeamSelector';
import SimulationTable from './components/SimulationTable';
import logo from './images/site_logo.jpg';

const App = () => {
  const [simulationData, setSimulationData] = useState([]);
  const [resultString, setResultString] = useState(''); 
  const [loading, setLoading] = useState(false);
  const teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"];

  const handleSimulate = async (homeTeam, awayTeam, numSimulations) => {
    setLoading(true);
    setResultString('');
    setSimulationData([]);
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            <img src={logo} alt="Site Logo" style={{ width: 50, height: 50, color:'transparent'}}/>
          </Box>
          <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
            NFL Simulation Engine
          </Typography>
        </Toolbar>
      </AppBar>
      <Box padding={3}>
        <TeamSelector teams={teams} onSimulate={handleSimulate} />
        {loading && (
          <Box display="flex" justifyContent="center" marginBottom={2}>
            <LinearProgress style={{ width: '50%' }} />
          </Box>
        )}
        {resultString && !loading && (
          <Typography variant="h5" style={{ marginBottom: 20 }}>
            {resultString}
          </Typography>
        )}
        {simulationData && !loading && (
          <SimulationTable data={simulationData} />
        )}
      </Box>
    </div>
  )
}

export default App;