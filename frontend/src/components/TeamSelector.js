import React, { useState } from 'react';
import { TextField, Button, MenuItem, Typography, Box } from '@mui/material';

const TeamSelector = ({ teams, models, onSimulate }) => {
    const [homeTeam, setHomeTeam] = useState('ATL');
    const [awayTeam, setAwayTeam] = useState('NO');
    const [model, setModel] = useState('proto');
    const [numSimulations , setNumSimulations] = useState(10);

    const handleSimulate = () => {
        if (homeTeam && awayTeam && numSimulations > 0) {
            onSimulate(homeTeam, awayTeam, numSimulations, model);
        }
    }

    return (
        <Box marginBottom={20}>
            <Typography variant="h5" marginBottom={3}>Select Teams, Number of Simulations and Game Model to Run:</Typography>
            <Box display="flex" alignItem="center" marginBottom={10}>
                <TextField
                    label="Home Team"
                    select
                    value={homeTeam}
                    onChange={(e) => setHomeTeam(e.target.value)}
                    style={{ marginRight: 10 }}
                >
                    {teams.map((team) => (
                        <MenuItem key={team} value={team}>{team}</MenuItem>
                    ))}
                </TextField>
                <TextField
                    label="Away Team"
                    select
                    value={awayTeam}
                    onChange={(e) => setAwayTeam(e.target.value)}
                    style={{ marginRight: 10 }}
                >
                    {teams.map((team) => (
                        <MenuItem key={team} value={team}>{team}</MenuItem>
                    ))}
                </TextField>
                <TextField
                    label="Number of Simulations"
                    type="number"
                    value={numSimulations}
                    onChange={(e) => setNumSimulations(e.target.value)}
                    style={{ marginRight: 10 }}
                />
                <TextField
                    label="Model"
                    select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    style={{ marginRight: 10 }}
                >
                    {models.map((curr_model) => (
                        <MenuItem key={curr_model} value={curr_model}>{curr_model}</MenuItem>
                    ))}
                </TextField>
                <Button variant="contained" onClick={handleSimulate}>Run Simulation</Button>
            </Box>
        </Box>
    );
};

export default TeamSelector;