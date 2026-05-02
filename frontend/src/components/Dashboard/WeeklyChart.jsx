import React, {useState, useEffect} from 'react';
import {getTransactions} from '../../services/api';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from 'recharts';

function WeeklyChart({ selectedDate }) {
    const [weeklyData, setWeeklyData] = useState([]);

    useEffect(() => {
        loadWeekData();
    }, [selectedDate]);

    const loadWeekData = async () => {
        const end = new Date(selectedDate);
        const start = new Date(end);
        start.setDate(start.getDate() -6);

        const startStr = start.toISOString().split('T')[0];
        const endStr = end.toISOString().split('T')[0];

        try {
            const res= await getTransactions(startStr, endStr);
            const transactions = res.data || [];

            //расходы по дням
            const dailyTotals = {};
            for (let i = 0; i < 7; i++) {
                const d = new Date(start);
                d.setDate(d.getDate() +i);
                const key =d.toISOString().split('T')[0];
                dailyTotals[key] = 0;
            }

            transactions.forEach(t=> {
                if (t.amount < 0 && dailyTotals[t.date] !== undefined) {
                    dailyTotals[t.date] += Math.abs(t.amount);
                }
            });

            const chartData = Object.entries(dailyTotals).map(([date, amount]) => ({
                date: new Date(date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short'}),
                amount: Math.round(amount),
                fullDate: date
            }));

            setWeeklyData(chartData);
        } catch (error) {
            console.error('Ощ=шибка загрузки данных за неделю:', error);
        }
    };

    return (
        <div style={{ background: '#fff', padding: 20, borderRadius: 10, boxShadow: '0 2px 4px rgba(0,0,0,0.1)', margin: '20px 0' }}>
            <h3>Расходы за неделю</h3>
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value} ₽`} />
                        <Bar dataKey="amount" fill="#2196f3" radius={[8,8,0,0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

export default WeeklyChart;