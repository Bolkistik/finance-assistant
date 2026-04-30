//Этот файл является главной страницей дашборда финансового ассистента и отображает баланс и дневные лимиты, а так же список операций за дату.

import React, {useState, useEffect} from 'react'; //Хуки для реакт. Состояние и побочные эффекты.
import {getBalance, getTransactions, getCategories, addTransaction} from '../services/api';//функции api
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

    const [form, setForm] = useState ({
        date: new Date().toISOString().split('T')[0],
        amount: '',
        category_id: '',
        description: '',
        transaction_type: 'actual'
    });

    const [formVisible, setFormVisible] = useState(false);

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

    const handleAddTransaction = async (e) => {
        e.preventDefault();

        if (!form.category_id) {
            alert('Выбери категорию!');
            return;
        }
        
        try {
            await addTransaction({
                date: form.date,
                amount: parseFloat(form.amount),
                category_id: parseInt(form.category_id),
                description: form.description || '',
                transaction_type: form.transaction_type,
                is_manual: true
            });
            setForm({
                date: new Date().toISOString().split('T')[0],
                amount: '',
                category_id: '',
                description: '',
                transaction_type: 'actual'
            });
            setFormVisible(false);
            loadData();
        } catch (error) {
            console.error('Ошибка добавления:', error);
            alert('ошибка добавления транзакции');
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

            {/*Кнопка добавления транзакции*/}
            <div style={{ margin: '20px 0'}}>
                <button
                    onClick={() => setFormVisible(!formVisible)}
                    style={{
                        padding: '10px 20px',
                        fontSize: 16,
                        background: formVisible ? '#f44336' : '#4caf50',
                        color: 'white',
                        border: 'none',
                        borderRadius: 5,
                        cursor: 'pointer'
                    }}
                >
                    {formVisible ? 'Отмена' : '+ Добавить операцию'}
                </button>
            </div>

            {/*Форма добавления*/}
            {formVisible && (
                <div style={{
                    background: '#f5f5f5',
                    padding: '20px',
                    borderRadius: '10px',
                    margin: '20px 0'
                }}>
                    <h3>Новая операция</h3>
                    <form onSubmit={handleAddTransaction}>
                        <div style={{ margin: '10px 0'}}>
                            <label>Дата:</label>
                            <input
                            type="date"
                            value={form.date}
                            onChange={e => setForm({ ...form, date: e.target.value})}
                            style={{ padding:8, fontSize: 16 }}
                            />
                        </div>

                        <div style={{ margin: '10px 0'}}>
                            <label>Категория:</label>
                            <select
                                value={form.category_id}
                                onChange={e => setForm({ ...form, category_id: e.target.value})}
                                required
                                style={{ padding: 8, fontSize: 16 }}
                            >
                                <option value="">Выбери категорию</option>
                                {categories.map(c => (
                                    <option key={c.id} value={c.id}>
                                        {c.type === 'income' ? 'coin' : 'baks'} {c.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div style={{ margin: '10px 0'}}>
                            <label>Сумма: </label>
                            <input
                            type="number"
                            step="0.01"
                            placeholder="Сумма"
                            value={form.amount}
                            onChange={e => setForm({ ...form, amount: e.target.value})}
                            required
                            style={{ padding: 8, fontSize: 16}}
                            />
                        </div>

                        <div style={{ margin: '10px 0'}}>
                            <label>Описание:</label>
                            <input
                                type="text"
                                placeholder="Описание"
                                value={form.description}
                                onChange={e => setForm({ ...form, description: e.target.value})}
                            />
                        </div>

                        <button
                            type="submit"
                            style={{
                                padding: '10px 20px',
                                fontSize: 16,
                                background:'#2196f3',
                                color: 'white',
                                border: 'none',
                                borderRadius: 5,
                                cursor: 'pointer',
                                marginTop: 10
                            }}
                        >
                            Сохранить
                        </button>
                    </form>
                </div>
            )}

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