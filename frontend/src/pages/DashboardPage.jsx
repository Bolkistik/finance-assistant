//Этот файл является главной страницей дашборда финансового ассистента и отображает баланс и дневные лимиты, а так же список операций за дату.

import React, {useState, useEffect} from 'react'; //Хуки для реакт. Состояние и побочные эффекты.
import {getBalance, getTransactions, getCategories} from '../services/api';//функции api
import BalanceCard from '../components/Dashboard/BalanceCard';//Компоненты для отображения различных частей интерфейса
import DatePicker from '../components/Dashboard/DatePicker';
import LoadingSpinner from '../components/Dashboard/LoadingSpinner';//Компоненты для отображения различных частей интерфейса
import {formatCurrency, formatDate} from '../utils/formatters';//Утилиты для форматирования

function DashboardPage() {
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]); //Получаем дату
    const [balance, setBalance] = useState(null); //Текущий баланс
    const [categories, setCategories] = useState([]); //
    const [transactions, setTransactions] = useState([]); //Список транзакций за выбранную дату
    const [loading, setLoading] = useState(true); //Флаг загрузки данных (показываем спиннер пока грузим)

    useEffect(() => { //Хук для побочных эффектов, загружает даннфе при монтировании компонента или изменени данных
        loadData(); //Вызываем функцию загрузки данных
    }, [selectedDate]); //Следим за изменениями selectedData

    const loadData = async () => { //Ассинхронная функция загрузки данных. Загружает баланс и транзакции параллельно для оптимизации
        setLoading(true); //Показываем индикатор загрузки
        try {
            const [balanceRes, transactionsRes, categoriesRes] = await Promise.all([ //Promise.all - запускает оба запроса паралельно
                getBalance(selectedDate), //Запрос баланса на дату 
                getTransactions(selectedDate, selectedDate), //Транзакции за день
                getCategories()// загружаем категории
            ]);
//Обновляем состояние полученными данными
            setBalance(balanceRes.data.balance);
            setTransactions(transactionsRes.data || []);
            setCategories(categoriesRes.data || []);

        } catch (error) {
            console.error('Ошибка загрузки:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner/>;

    return (
        <div className="Dashboard" style={{ padding: 20, maxWidth: 800, margin: '0 auto', fontFamily: 'Arial'}}>
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

            <div className="transaction-section">
                <h3>Операции за день ({transactions.length})</h3>
                {transactions.length === 0 ?(
                    <p>Нет операций</p>
                ) : (
                    <ul>
                        {transactions.map(t => (
                            <li key={t.id}>
                                {t.category_ref?.name || 'Без категории'} : {formatCurrency(t.amount)} - {t.description || '-'}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default DashboardPage;