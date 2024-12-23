import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import Plot from 'react-plotly.js';

const SimulationTable = ({ data, homeWinPct }) => {
    if (!data.length) {
        return null;
    }

    const styles = {
        headerRow: {
            backgroundColor: '#bfc3c6',
        },
        headerCell: {
            color: '#fff',
            fontWeight: 'bold',
        },
        dataRow: {
            backgroundColor: '#f5f5f5',
        },
        hoverRow: {
            '&:hover': {
                backgroundColor: '#e0f7fa',
            },
        },
    };

    const statsColumns = ["team","score","run_rate","pass_rate","pass_cmp_rate",
        "pass_yards","passing_tds","sacks_allowed","pass_yards_per_play",
        "rushing_attempts","rushing_yards","rushing_tds","rush_yards_per_play",
        "total_turnovers","fg_pct"];

    const pieData = [
        {
            values: [homeWinPct, 100-homeWinPct],
            labels: data.map((row) => `${row["team"]}`),
            domain: {column: 0},
            type: 'pie',
            title: 'Win Probability',
            hoverinfo: 'label+percent',
            hole: .5,
        }
    ];

    const pieLayout = {
        paper_bgcolor: '#99b8cd',
        title: `${data[0]["team"]} vs ${data[1]["team"]} Simulation Results`
    };

    return (
        <>
            <Plot data={pieData} layout={pieLayout}/>
            <TableContainer component={Paper} sx={{mt:5, mb:5}}>
                <Table>
                    <TableHead>
                        <TableRow sx={styles.headerRow}>
                            {statsColumns.map((key) => (
                                <TableCell key={key}>{key}</TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data.map((row, index) => (
                            <TableRow key={index} sx={styles.dataRow}>
                                {statsColumns.map((key) => (
                                    <TableCell key={key}>{row[key]}</TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
};

export default SimulationTable;