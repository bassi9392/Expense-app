import React, { useEffect, useState } from 'react';
import API from '../services/api';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Dashboard = () => {
    const [summary, setSummary] = useState({ totalExpenses: 0, categoryData: {} });

    useEffect(() => {
        const fetchSummary = async () => {
            const res = await API.get('/transactions/summary');
            setSummary(res.data);
        };
        fetchSummary();
    }, []);

    const chartData = Object.keys(summary.categoryData).map(key => ({
        name: key, value: summary.categoryData[key]
    }));

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

    return (
        <div style={{ padding: '20px' }}>
            <h1>Dashboard</h1>
            <div style={{ background: '#e9ecef', padding: '20px', borderRadius: '10px', marginBottom: '30px' }}>
                <h3>Total Spent: ${summary.totalExpenses.toFixed(2)}</h3>
            </div>

            <div style={{ height: '400px', background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #ddd' }}>
                <h4>Spending by Category</h4>
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                                {chartData.map((entry, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                ) : <p>No data yet.</p>}
            </div>
        </div>
    );
};

export default Dashboard;