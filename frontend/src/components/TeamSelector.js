import React, { useState } from 'react';
import { TextField, Button, MenuItem, Box } from '@mui/material';

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
        <Box display="flex" flexDirection="column" alignItems="center">
            <Box display="flex" alignItems="center" marginTop="10px">
                <TextField
                    label="Home"
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
                    label="Away"
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