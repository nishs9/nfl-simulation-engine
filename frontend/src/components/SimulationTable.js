import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

const SimulationTable = ({ data }) => {
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

    return (
        <TableContainer component={Paper}>
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
    );
};

export default SimulationTable;