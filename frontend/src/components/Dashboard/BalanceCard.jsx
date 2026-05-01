import React from 'react';

function BalanceCard({balance, date, income, expense}) {
    return (
        <div style={{ background: '#e8f5e9', padding: 20, borderRadius: 10}}>
            <h2>Баланс на {date}</h2>
            <p style={{ fontSize: 32, fontWeight: 'bold', color: '#2e7d32'}}>
                {balance?.toLocaleString() || 0} ₽
            </p>
            
            <div style={{ display: 'flex', gap: 20, marginTop: 10}}>
                <span style={{ color: '#2e7d32'}}>📈 Доходы: {income?.toLocaleString() || 0}₽</span>
                <span style={{ color: '#c62828'}}>📉 Расходы: {expense?.toLocaleString() || 0}₽</span>
            </div>
        </div>

    );
}

export default BalanceCard;