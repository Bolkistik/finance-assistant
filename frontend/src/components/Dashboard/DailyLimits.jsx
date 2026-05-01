import React from "react";

function DailyLimits({ transactions, categories }) {
    const limits = {
        'Продукты' : { limit: 1000, color: '#ff9800', icon: '🛒'},
        'Авто' : { limit: 2000, color: '#2196f3', icon: '🚗'},
        'Прочее' : { limit: 4000, color: '#9c27b0', icon: '📦'},
    };

    //Считаем расходы за сегодня
    const spentByCategory = {};
    transactions.forEach(t => {
        const catName = t.category_ref?.name;
        if (catName && limits[catName] && t.amount <0){
            spentByCategory[catName] = (spentByCategory[catName] || 0) + Math.abs(t.amount);
        }
    });

    return (
        <div style={{ background: '#fff', padding: 20, borderRadius: 10, boxShadow: '0 2px 4px rgba(0,0,0,0.1)', margin: '20px 0'}}>
            <h3>Дневные лимиты</h3>
            {Object.entries(limits).map(([name, config]) => {
                const spent = spentByCategory[name] || 0;
                const percent = Math.min((spent / config.limit) * 100, 100);
                const barColor = percent > 80 ? '#f44336' : percent > 50 ? '#ff9800' : '#4caf50';

                return (
                    <div key={name} style={{margin: '15px 0'}}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5}}>
                            <span>{config.icon} {name}</span>
                            <span style={{fontWeight: 'bold '}}>
                                {spent} / {config.limit} ₽
                            </span>
                        </div>

                        <div style={{
                            width: '100%',
                            height: 12,
                            background: '#e0e0e0',
                            borderRadius: 6,
                            overflow: 'hidden'
                        }}>
                            <div style={{
                                width: `${percent}%`,
                                height: '100%',
                                background: barColor,
                                borderRadius: 6,
                                transition: 'width 0.5s ease'
                            }}>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export default DailyLimits;