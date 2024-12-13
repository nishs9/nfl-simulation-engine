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
  const [homeWinPct, setHomeWinPct] = useState(null);
  const [loading, setLoading] = useState(false);
  const teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"];
  const available_models = ["proto", "v1"]

  const handleSimulate = async (homeTeam, awayTeam, numSimulations, model) => {
    setLoading(true);
    setResultString('');
    setSimulationData([]);
    try {
      const response = await axios.post('http://localhost:5000/run-simulation', {
        home_team: homeTeam,
        away_team: awayTeam,
        num_simulations: numSimulations,
        game_model: model
      });

      const { result_string, home_win_pct, total_sim_stats } = response.data;
      setResultString(result_string);
      setHomeWinPct(home_win_pct);
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
    <div alignItems>
      {/* Header Bar */}
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

      {/* Team and Model Selector */}
      <Box marginLeft="5px" marginTop="10px" marginBottom="10px">
        <TeamSelector teams={teams} models={available_models} onSimulate={handleSimulate}/>
      </Box>

      {/* Loading Bar */}
      <Box marginTop="15px">
      {loading && (
          <Box display="flex" justifyContent="center">
            <LinearProgress style={{ width: '50%' }} />
          </Box>
        )}
      </Box>

      {/* Simulation Results */}
      <Box textAlign="center" sx={{ ml: 5, mr: 5, mb: 5}}>
        {simulationData && !loading && (
          <SimulationTable data={simulationData} homeWinPct={homeWinPct}/>
        )}
        {resultString && !loading && (
          <Typography variant="h5" sx={{ mt: 5 }}>
            {resultString}
          </Typography>
        )}
      </Box>
    </div>
  )
}

export default App;