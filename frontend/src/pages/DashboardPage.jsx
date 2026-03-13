//Этот файл является главной страницей дашборда финансового ассистента и отображает баланс и дневные лимиты, а так же список операций за дату.

import React, {useState, useEffect} from 'react'; //Хуки для реакт. Состояние и побочные эффекты.
import {getBalance, getTransactions} from '../services/api';//функции api
import BalanceCard from '../components/Dashboard/BalanceCard';//Компоненты для отображения различных частей интерфейса
import DailyLimitCard from '../components/Dashboard/DailyLimitCard';
import ExpensesList from '../components/Dashboard/ExpensesList';
import DatePicker from '../components/Dashboard/DatePicker';
import LoadingSpinner from '../components/Dashboard/LoadingSpinner';//Компоненты для отображения различных частей интерфейса
import {formatCurrency, formatDate} from '../utils/formatters';//Утилиты для форматирования

function DashboardPage() {
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]); //Получаем дату
    const [balance, setBalance] = useState(null); //Текущий баланс
    const [transactions, setTransactions] = useState([]); //Список транзакций за выбранную дату
    const [loading, setLoading] = useState(true); //Флаг загрузки данных (показываем спиннер пока грузим)
    const [dailyLimits, setDailyLimits] = useState({ //Дневные лимиты по катрегориям
        products: 0,
        auto: 0,
        other: 0
    });

    useEffect(() => { //Хук для побочных эффектов, загружает даннфе при монтировании компонента или изменени данных
        loadData(); //Вызываем функцию загрузки данных
    }, [selectedDate]); //Следим за изменениями selectedData

    const loadData = async () => { //Ассинхронная функция загрузки данных. Загружает баланс и транзакции параллельно для оптимизации
        setLoading(true); //Показываем индикатор загрузки
        try {
            const [balanceRes, transactionsRes] = await Promise.all([ //Promise.all - запускает оба запроса паралельно
                getBalance(selectedDate), //Запрос баланса на дату 
                getTransactions(selectedDate, selectedDate), //Транзакции за день
            ]);
//Обновляем состояние полученными данными
            setBalance(balanceRes.data.balance);
            setTransactions(transactionsRes.data)

            setDailyLimits({
                products: 1000,
                auto: 500,
                other: 300
            });

        } catch (error) {
            console.error('Ошибка загрузки:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner/>;

    return (
        <div className="Dashboard">
            <header className="dashboard-header">
                <h1>Финансовый ассистент</h1>
                <DatePicker
                    value={selectedDate}
                    onChange={setSelectedDate}
                />
            </header>

            <div className="balance-section">
                <BalanceCard
                    balance={balance}
                    date={selectedDate}
                />
            </div>

            <div className="limits-section">
                <h3>Дневные лимиты</h3>
                <div className="limits-grid">
                    <DailyLimitCard
                        category="Продукты"
                        limit={dailyLimits.products}
                        spent={calculateSpent(transactions, 'products')}
                        color="#4caf50"
                    />

                    <DailyLimitCard
                        category="Авто"
                        limit={dailyLimits.auto}
                        spent={calculateSpent(transactions, 'auto')}
                        color="#2196f3"
                    />

                    <DailyLimitCard
                        category="Прочее"
                        limit={dailyLimits.other}
                        spent={calculateSpent(transactions, 'other')}
                        color="#ff9800"
                    />
                </div>
            </div>

            <div className="transaction-section">
                <h3>Операции за день</h3>
                <ExpensesList
                    transactions={transactions}
                    onAddTransaction={() => {}} //Это дописать!!!
                />
            </div>
        </div>
    );
}

function calculateSpent(transactions, category) {
    return transactions
        .filter(t => t.category === category && t.amount <0)
        .reduce((sum, t) => sum + Math.abs(t.amount), 0);
}

export default DashboardPage;