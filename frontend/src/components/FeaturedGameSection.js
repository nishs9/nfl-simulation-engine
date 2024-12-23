import React from 'react';
import { Box } from '@mui/material';
import Plot from 'react-plotly.js';

const FeaturedGameSection = ({ homeTeam, awayTeam, 
                            featGameHomePassStats, featGameAwayPassStats,
                            featGameHomeRushStats, featGameAwayRushStats,
                            featGameHomeScoringStats, featGameAwayScoringStats }) => {

    if (!featGameHomePassStats.length || !featGameAwayPassStats.length
        || !featGameHomeRushStats.length || !featGameAwayRushStats.length
        || !featGameHomeScoringStats.length || !featGameAwayScoringStats.length
    ) {
        console.error("Unable to retrieve some or all of the featured game stats");
        return null;
    }

    const lineData = [
        {
            x: featGameHomePassStats.map((row) => row["game_time_elapsed"]),
            y: featGameHomePassStats.map((row) => row["agg_pass_yards"]),
            type: 'scatter',
            name: homeTeam,
            mode:'lines+markers',
            marker: { color: 'red' },
            line: { shape: 'spline', width: 2},
            visible: true
        },
        {
            x: featGameAwayPassStats.map((row) => row["game_time_elapsed"]),
            y: featGameAwayPassStats.map((row) => row["agg_pass_yards"]),
            name: awayTeam,
            type: 'scatter',
            mode:'lines+markers',
            marker: { color: 'blue' },
            line: { shape: 'spline', width: 2},
            visible: true
        },
        {
            x: featGameHomeRushStats.map((row) => row["game_time_elapsed"]),
            y: featGameHomeRushStats.map((row) => row["agg_rush_yards"]),
            name: homeTeam,
            type: 'scatter',
            mode:'lines+markers',
            marker: { color: 'green' },
            line: { shape: 'spline', width: 2},
            visible: false
        },
        {
            x: featGameAwayRushStats.map((row) => row["game_time_elapsed"]),
            y: featGameAwayRushStats.map((row) => row["agg_rush_yards"]),
            name: awayTeam,
            type: 'scatter',
            mode:'lines+markers',
            marker: { color: 'orange' },
            line: { shape: 'spline', width: 2},
            visible: false
        },
        {
            x: featGameHomeScoringStats.map((row) => row["game_time_elapsed"]),
            y: featGameHomeScoringStats.map((row) => row["posteam_score"]),
            name: homeTeam,
            type: 'scatter',
            mode:'lines+markers',
            marker: { color: 'purple' },
            line: { shape: 'spline', width: 2},
            visible: false
        },
        {
            x: featGameAwayScoringStats.map((row) => row["game_time_elapsed"]),
            y: featGameAwayScoringStats.map((row) => row["posteam_score"]),
            name: awayTeam,
            type: 'scatter',
            mode:'lines+markers',
            marker: { color: 'black' },
            line: { shape: 'spline', width: 2},
            visible: false
        }
    ];

    const lineLayout = {
        title: `Random Simulation of ${homeTeam} vs ${awayTeam}`,
        paper_bgcolor: '#99b8cd', // Outer area background
        plot_bgcolor: '#ffffff',  // Plot area background
        xaxis: { 
            title: "Time Elapsed (seconds)",
            range: [0, 3600] 
        },
        updatemenus: [
            {
                x: 0.5,
                y: 1.15,
                xanchor:'center',
                showactive: true,
                direction:'down',
                buttons: [
                    {
                        method: `update`,
                        label: `Passing Yards`,
                        args: [
                            { visible: [true, true, false, false, false, false] }
                        ]
                    },
                    {
                        method: `update`,
                        label: `Rushing Yards`,
                        args: [
                            { visible: [false, false, true, true, false, false] }
                        ]
                    },
                    {
                        method: `update`,
                        label: `Scoring`,
                        args: [
                            { visible: [false, false, false, false, true, true] }
                        ]
                    }
                ]
            }
        ]
    }

    return (
        <Box textAlign="center">
            <Plot
                data={lineData}
                layout={lineLayout}
                config={{ responsive: true }}
                margin={{ t: 10, b: 10, l: 10, r: 10 }}
            />
        </Box>
    );
};

export default FeaturedGameSection;