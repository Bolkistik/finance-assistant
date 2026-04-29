import React from 'react';

function BalanceCard({balance, date}) {
    return (
        <div style={{ background: '#e8f5e9', padding: 20, borderRadius: 10}}>
            <h2>Баланс на {date}</h2>
            <p style={{ fontSize: 32, fontWeight: 'bold', color: '#2e7d32'}}>
                {balance?.toLocaleString() || 0} rub
            </p>
        </div>

    );
}

export default BalanceCard;