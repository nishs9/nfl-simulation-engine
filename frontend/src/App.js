import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AppBar, Toolbar, Typography, LinearProgress, Box, Paper } from '@mui/material';
import TeamSelector from './components/TeamSelector';
import SimulationTable from './components/SimulationTable';
import FeaturedGameSection from './components/FeaturedGameSection';
import logo from './images/site_logo.jpg';

const App = () => {
  useEffect(() => {
    document.title = 'NFL Simulation Engine';
  });

  const teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"];
  const available_models = ["proto", "v1", "v1a", "v1b"]

  const [loading, setLoading] = useState(false);

  const [homeTeamAbbrev, setHomeTeamAbbrev] = useState('');
  const [awayTeamAbbrev, setAwayTeamAbbrev] = useState('');

  const [simulationData, setSimulationData] = useState([]);
  const [resultString, setResultString] = useState(''); 
  const [homeWinPct, setHomeWinPct] = useState(null);
  const [featuredGameHomePassStats, setFeaturedGameHomePassStats] = useState([]);
  const [featuredGameAwayPassStats, setFeaturedGameAwayPassStats] = useState([]);
  const [featuredGameHomeRushStats, setFeaturedGameHomeRushStats] = useState([]);
  const [featuredGameAwayRushStats, setFeaturedGameAwayRushStats] = useState([]);
  const [featuredGameHomeScoringStats, setFeaturedGameHomeScoringStats] = useState([]);
  const [featuredGameAwayScoringStats, setFeaturedGameAwayScoringStats] = useState([]);

  const handleSimulate = async (homeTeam, awayTeam, numSimulations, model) => {
    setLoading(true);
    setResultString('');
    setSimulationData([]);
    setFeaturedGameHomePassStats([]);
    setFeaturedGameAwayPassStats([]);
    setFeaturedGameHomeRushStats([]);
    setFeaturedGameAwayRushStats([]);
    setFeaturedGameHomeScoringStats([]);
    setFeaturedGameAwayScoringStats([]);
    setHomeTeamAbbrev(homeTeam);
    setAwayTeamAbbrev(awayTeam);
    try {
      const response = await axios.post('http://localhost:5000/run-simulation', {
        home_team: homeTeam,
        away_team: awayTeam,
        num_simulations: numSimulations,
        game_model: model
      });

      const response_json = response.data;
      setResultString(response_json["result_string"]);
      setHomeWinPct(response_json["home_win_pct"]);
      setSimulationData(response_json["total_sim_stats"]);
      setFeaturedGameHomePassStats(response_json["featured_game_home_pass_data"]);
      setFeaturedGameAwayPassStats(response_json["featured_game_away_pass_data"]);
      setFeaturedGameHomeRushStats(response_json["featured_game_home_rush_data"]);
      setFeaturedGameAwayRushStats(response_json["featured_game_away_rush_data"]);
      setFeaturedGameHomeScoringStats(response_json["featured_game_home_scoring_data"]);
      setFeaturedGameAwayScoringStats(response_json["featured_game_away_scoring_data"]);
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
      <Box textAlign="center" sx={{ ml: 5, mr: 5, mb: 5 }}>
        {simulationData && !loading && (
          <SimulationTable 
            data={simulationData} 
            homeWinPct={homeWinPct}
          />
        )}

        {!resultString && !loading && (
          <Paper elevation={8} square={false} sx={{ p: 2, mt: 5, mb: 5, backgroundColor: '#bfc3c6' }}>
            <Typography variant="h5">
              Click "Run Simulation" to generate stats and visualizations
            </Typography>
          </Paper>
        )}

        {loading && (
          <Paper elevation={8} square={false} sx={{ p: 2, mt: 5, mb: 5, backgroundColor: '#bfc3c6' }}>
            <Typography variant="h5">
              Results are loading...
            </Typography>
          </Paper>
        )}
        
        {resultString && !loading && (
          <Paper elevation={8} square={false} sx={{ p: 2, mt: 5, mb: 5, backgroundColor: '#bfc3c6' }}>
            <Typography variant="h5">
              {resultString}
            </Typography>
          </Paper>
        )}

        <FeaturedGameSection
          homeTeam={homeTeamAbbrev}
          awayTeam={awayTeamAbbrev}
          featGameHomePassStats={featuredGameHomePassStats}
          featGameAwayPassStats={featuredGameAwayPassStats}
          featGameHomeRushStats={featuredGameHomeRushStats}
          featGameAwayRushStats={featuredGameAwayRushStats}
          featGameHomeScoringStats={featuredGameHomeScoringStats}
          featGameAwayScoringStats={featuredGameAwayScoringStats}
        />
      </Box>
    </div>
  )
}

export default App;